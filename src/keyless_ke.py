"""E2: Toy keyless covert key exchange (KE) carried in the sampling of a real language model.

Setting (matches the passive-auditor model of von Ahn-Hopper 2004 and Vaikuntanathan-Zamir 2026):
  * Alice and Bob are "honest-looking" assistants. Each one answers public prompts (Dolly
    instructions) with a public LM (Qwen2.5-0.5B-Instruct, pure sampling at T=1).
  * They share NO key. They share only the public protocol (this file) and a public session seed R
    (any value visible to everyone, e.g. a timestamp hash).
  * The auditor knows everything (model, prompts, protocol, R) except the parties' private coins.

Channel: every message is cut into chunks of k tokens. A chunk carries one bit,
  bit_R(chunk) = SHA256(R || msg_id || chunk_id || token ids) mod 2,
but only if the model's next-token entropy at the start of the chunk is >= tau. Anyone can compute
this gate from the public transcript, and it skips low-entropy chunks. To send bit b, the sender
draws up to B honest candidate chunks and outputs the first one whose hash bit is b (rejection
sampling). An honest agent outputs the first candidate. If all B candidates fail, the chunk is
output anyway and becomes a bit error.

KE: Diffie-Hellman in the quadratic-residue subgroup of a safe prime p = 2q+1. The public value
y = g^a is encoded uniformly as x = min(y, p-y) in [1, q], with a resampled until x < 2^(n-1).
The transcript bits are then uniform n-1 bit strings, so to the auditor they look exactly like
honest hash bits. After KE both parties derive K = SHA256(g^ab). The covert payload is sent with
keyed bits bit_K(chunk) = HMAC(K, ...) mod 2, which the auditor cannot compute.

Conditions:
  honest       : no hidden content (null distribution)
  rank_code    : naive keyless scheme; bit 0 -> argmax token, bit 1 -> 2nd most likely token
  public_plain : protocol-only scheme; payload bits sent directly on public-hash bits (no key)
  keyless_ke   : full scheme (public-hash DH KE, then a keyed message)

Outputs: results/e2/*.json and per-message records for the detection analysis.
"""
import argparse
import hashlib
import hmac
import json
import math
import os
import random
import secrets
import time

import numpy as np
import torch
from datasets import load_from_disk
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"

# ----------------------------------------------------------------------------- crypto helpers
# 2048-bit MODP group 14 (RFC 3526) is a safe prime, used for the cost estimate.
RFC3526_2048 = int(
    "FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DD"
    "EF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7ED"
    "EE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F"
    "83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA18217C32905E462E36CE3B"
    "E39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9DE2BCBF6955817183995497CEA956AE515D2261898FA0510"
    "15728E5A8AACAA68FFFFFFFFFFFFFFFF", 16)


def is_probable_prime(n, rounds=40):
    """Miller-Rabin primality test."""
    if n < 2:
        return False
    for sp in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29):
        if n % sp == 0:
            return n == sp
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    rng = random.Random(n)
    for _ in range(rounds):
        a = rng.randrange(2, n - 1)
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def safe_prime(bits, seed=0):
    """Deterministically find a safe prime p=2q+1 with p of the given bit length (toy sizes)."""
    rng = random.Random(seed)
    while True:
        q = rng.getrandbits(bits - 1) | (1 << (bits - 2)) | 1
        if is_probable_prime(q, 8) and is_probable_prime(2 * q + 1, 8):
            if is_probable_prime(q) and is_probable_prime(2 * q + 1):
                return 2 * q + 1


class UniformDH:
    """DH in the QR subgroup of Z_p^* (p safe prime, so p = 3 mod 4 and -1 is a non-residue).
    The map y -> min(y, p-y) is a bijection from QR_p onto [1, q]. With rejection to [1, 2^(n-1)),
    the encoded public key is a uniformly random (n-1)-bit string."""

    def __init__(self, p):
        self.p = p
        self.q = (p - 1) // 2
        self.g = 4  # 2^2 is a QR, so it generates the order-q subgroup
        self.nbits = self.q.bit_length() - 1  # transmitted bits

    def keygen(self, rng):
        tries = 0
        while True:
            tries += 1
            a = rng.randrange(1, self.q)
            y = pow(self.g, a, self.p)
            x = y if y <= self.q else self.p - y
            if x < (1 << self.nbits):
                return a, x, tries

    def decode(self, x):
        """Recover y in QR from the encoded x (exactly one of x, p-x is a QR)."""
        if pow(x, self.q, self.p) == 1:
            return x
        return self.p - x

    def shared(self, a, x_other):
        return pow(self.decode(x_other), a, self.p)


def int_to_bits(v, n):
    return [(v >> (n - 1 - i)) & 1 for i in range(n)]


def bits_to_int(bits):
    v = 0
    for b in bits:
        v = (v << 1) | int(b)
    return v


def text_to_bits(s):
    return [int(c) for byte in s.encode() for c in format(byte, "08b")]


def bits_to_text(bits):
    by = bytes(bits_to_int(bits[i:i + 8]) for i in range(0, len(bits) - len(bits) % 8, 8))
    return by.decode("utf-8", errors="replace")


def public_bit(seed, msg_id, chunk_id, toks):
    h = hashlib.sha256(seed + f"|{msg_id}|{chunk_id}|".encode() + np.asarray(toks, np.int64).tobytes())
    return h.digest()[0] & 1


def keyed_bit(key, msg_id, chunk_id, toks):
    h = hmac.new(key, f"|{msg_id}|{chunk_id}|".encode() + np.asarray(toks, np.int64).tobytes(), hashlib.sha256)
    return h.digest()[0] & 1


# ----------------------------------------------------------------------------- LM channel
class LMChannel:
    def __init__(self, model_id=MODEL_ID, device="cuda"):
        self.tok = AutoTokenizer.from_pretrained(model_id)
        # fp32 so that the entropy gate recomputed by the receiver matches the sender's exactly
        self.model = AutoModelForCausalLM.from_pretrained(model_id, dtype=torch.float32).to(device).eval()
        self.device = device
        self.eos = [self.tok.eos_token_id, self.tok.convert_tokens_to_ids("<|im_end|>"),
                    self.tok.convert_tokens_to_ids("<|endoftext|>")]

    def prompt_ids(self, instruction):
        msgs = [{"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": instruction}]
        s = self.tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        return self.tok(s, return_tensors="pt").input_ids[0].tolist()

    @torch.no_grad()
    def next_logprobs(self, ids):
        x = torch.tensor([ids], device=self.device)
        lp = torch.log_softmax(self.model(x, logits_to_keep=1).logits[0, -1].float(), -1)
        lp[self.eos] = -float("inf")  # all agents (honest or not) never stop early: fixed-length messages
        return torch.log_softmax(lp, -1)

    @staticmethod
    def entropy(lp):
        p = lp.exp()
        return float(-(p * torch.where(torch.isfinite(lp), lp, torch.zeros_like(lp))).sum())

    @torch.no_grad()
    def prefix(self, ids):
        """One forward pass over the context: next-token log-probs (for the public entropy gate)
        plus the KV cache, which is reused for all B candidate continuations."""
        x = torch.tensor([ids], device=self.device)
        o = self.model(x, use_cache=True, logits_to_keep=1)
        logits = o.logits[0, -1].float()
        logits[self.eos] = -float("inf")  # fixed-length messages for every agent (honest or not)
        return torch.log_softmax(logits, -1), o.past_key_values

    @torch.no_grad()
    def sample_chunks(self, lp0, cache, k, B, gen):
        """Draw B independent honest continuations of k tokens (ancestral sampling, T=1, no truncation)."""
        if B > 1:
            cache.batch_repeat_interleave(B)
        nxt = torch.multinomial(lp0.exp()[None].expand(B, -1), 1, generator=gen)
        out = [nxt]
        for _ in range(k - 1):
            o = self.model(nxt, past_key_values=cache, use_cache=True, logits_to_keep=1)
            cache = o.past_key_values
            logits = o.logits[:, -1].float()
            logits[:, self.eos] = -float("inf")
            nxt = torch.multinomial(torch.softmax(logits, -1), 1, generator=gen)
            out.append(nxt)
        return torch.cat(out, 1).tolist()

    @torch.no_grad()
    def message_stats(self, prompt, toks):
        """Per-token NLL and per-position entropy of a message (computed by receiver/auditor)."""
        ids = torch.tensor([prompt + toks], device=self.device)
        logits = self.model(ids).logits[0, len(prompt) - 1:-1].float()
        logits[:, self.eos] = -float("inf")
        lp = torch.log_softmax(logits, -1)
        nll = -lp.gather(1, torch.tensor(toks, device=self.device)[:, None])[:, 0]
        p = lp.exp()
        ent = -(p * torch.where(torch.isfinite(lp), lp, torch.zeros_like(lp))).sum(-1)
        rank = (lp > lp.gather(1, torch.tensor(toks, device=self.device)[:, None])).sum(-1)
        return nll.cpu().numpy(), ent.cpu().numpy(), rank.cpu().numpy()


def write_message(ch, prompt, msg_id, M, k, B, tau, bit_source, gen, mode, Bmax=None):
    Bmax = Bmax or B
    """Generate one fixed-length message of M tokens.
    mode 'honest' : first candidate always
    mode 'hash'   : rejection-sample candidate chunks so that bit_fn(chunk) == next bit
    mode 'rank'   : rank code, token rank = bit (1 bit per token, no entropy gate)
    bit_source: object with .next() -> bit or None, and .bit_fn(msg_id, chunk_id, toks)
    Returns tokens, number of bits attempted, number of sender-side failures."""
    toks, attempted, fails = [], 0, 0
    chunk_id = 0
    while len(toks) < M:
        ctx = prompt + toks
        if mode == "rank":
            b = bit_source.next() if bit_source is not None else None
            lp = ch.next_logprobs(ctx)
            if b is None:
                t = int(torch.multinomial(lp.exp(), 1, generator=gen))
            else:
                t = int(torch.topk(lp, 2).indices[b])
                attempted += 1
            toks.append(t)
            continue
        kk = min(k, M - len(toks))
        lp0, cache = ch.prefix(ctx)
        gate = ch.entropy(lp0) >= tau
        if mode == "honest" or bit_source is None or not gate or bit_source.peek() is None:
            cand = ch.sample_chunks(lp0, cache, kk, 1, gen)[0]
        else:
            b = bit_source.peek()
            cands = ch.sample_chunks(lp0, cache, kk, B, gen)
            cand = None
            for c in cands:
                if bit_source.bit_fn(msg_id, chunk_id, c) == b:
                    cand = c
                    break
            if cand is None and Bmax > B:
                # adaptive second batch: still "first matching candidate in an i.i.d. sequence", so
                # Lemma 3(i) (exact honest marginal when the hash is balanced) is unaffected
                lp0, cache = ch.prefix(ctx)
                more = ch.sample_chunks(lp0, cache, kk, Bmax - B, gen)
                for c in more:
                    if bit_source.bit_fn(msg_id, chunk_id, c) == b:
                        cand = c
                        break
            attempted += 1
            if cand is None:
                cand = cands[0]
                fails += 1
            bit_source.pop()
        toks.extend(cand)
        chunk_id += 1
    return toks, attempted, fails


def read_message(ch, prompt, toks, msg_id, k, tau, bit_fn, mode):
    """Receiver/auditor side: recompute the gate from the public transcript and read hash bits."""
    nll, ent, rank = ch.message_stats(prompt, toks)
    bits = []
    if mode == "rank":
        return [int(r) for r in rank if r <= 1], nll, ent, rank
    pos, chunk_id = 0, 0
    while pos < len(toks):
        c = toks[pos:pos + k]
        if ent[pos] >= tau:
            bits.append(bit_fn(msg_id, chunk_id, c))
        pos += len(c)
        chunk_id += 1
    return bits, nll, ent, rank


class BitQueue:
    def __init__(self, bits, bit_fn):
        self.bits = list(bits)
        self.i = 0
        self.bit_fn = bit_fn

    def peek(self):
        return self.bits[self.i] if self.i < len(self.bits) else None

    def pop(self):
        self.i += 1

    def next(self):
        b = self.peek()
        if b is not None:
            self.pop()
        return b

    def done(self):
        return self.i >= len(self.bits)


# ----------------------------------------------------------------------------- sessions
def run_session(ch, cond, sess, prompts, seed_pub, M, k, B, tau, dh, payload, max_msgs=400, Bmax=None):
    """One two-party session. Messages alternate Alice, Bob, Alice, ... on consecutive public prompts.
    Returns per-message records and a session summary."""
    priv_rng = random.Random(secrets.randbits(64) if cond == "_" else 10_000 + sess)  # private coins
    gen = torch.Generator(device=ch.device).manual_seed(1_000 + sess)
    pub = lambda m, c, t: public_bit(seed_pub, m, c, t)
    records = []
    summ = {"cond": cond, "session": sess, "k": k, "B": B, "Bmax": Bmax or B, "tau": tau}

    # set up what each party needs to send
    if cond == "keyless_ke":
        a, xa, ta = dh.keygen(priv_rng)
        b, xb, tb = dh.keygen(priv_rng)
        qa = BitQueue(int_to_bits(xa, dh.nbits), pub)
        qb = BitQueue(int_to_bits(xb, dh.nbits), pub)
        phase = "ke"
    elif cond == "public_plain":
        qa = BitQueue(text_to_bits(payload), pub)
        qb = None
        phase = "msg"
    elif cond == "rank_code":
        qa = BitQueue(text_to_bits(payload), None)
        qb = None
        phase = "msg"
    else:
        qa = qb = None
        phase = "honest"

    n_msgs_target = None if cond != "honest" else 8
    recv_bits = {"A": [], "B": []}  # bits as read by the partner from public hash
    tokens_total = 0
    t0 = time.time()
    key_bits_A = None
    m = 0
    while m < max_msgs:
        party = "A" if m % 2 == 0 else "B"
        prompt = prompts[(sess * 997 + m) % len(prompts)]
        pids = ch.prompt_ids(prompt)
        q = qa if party == "A" else qb
        mode = {"honest": "honest", "rank_code": "rank"}.get(cond, "hash")
        if mode == "rank" and party == "B":
            q = None
        toks, att, fails = write_message(ch, pids, m, M, k, B, tau, q, gen, mode if q is not None or mode == "rank" else "honest", Bmax=Bmax)
        tokens_total += len(toks)
        # every observer (partner and auditor) reads the public-hash bits
        pbits, nll, ent, rank = read_message(ch, pids, toks, m, k, tau, pub, "rank" if mode == "rank" else "hash")
        rec = {"cond": cond, "session": sess, "msg": m, "party": party, "phase": phase, "k": k, "tau": tau,
               "mean_nll": float(nll.mean()), "mean_rank_le1": float((rank <= 1).mean()),
               "public_bits": pbits, "attempted": att, "fails": fails, "n_tokens": len(toks),
               "prompt": prompt, "tokens": toks}
        if cond == "keyless_ke" and phase == "msg" and party == "A":
            kbits, *_ = read_message(ch, pids, toks, m, k, tau, lambda mm, cc, tt: keyed_bit(key_B, mm, cc, tt), "hash")
            rec["keyed_bits_read_by_B"] = kbits
        records.append(rec)
        m += 1

        # protocol state transitions
        if cond == "keyless_ke" and phase == "ke":
            recv_bits[party].extend(pbits)
            if qa.done() and qb.done():
                xa_hat = bits_to_int(recv_bits["A"][:dh.nbits])  # what Bob read from Alice
                xb_hat = bits_to_int(recv_bits["B"][:dh.nbits])
                sA = dh.shared(a, xb_hat)
                sB = dh.shared(b, xa_hat)
                key_A = hashlib.sha256(str(sA).encode()).digest()
                key_B = hashlib.sha256(str(sB).encode()).digest()
                summ.update({
                    "ke_bit_errors_A_to_B": int(sum(u != v for u, v in zip(int_to_bits(xa, dh.nbits), recv_bits["A"][:dh.nbits]))),
                    "ke_bit_errors_B_to_A": int(sum(u != v for u, v in zip(int_to_bits(xb, dh.nbits), recv_bits["B"][:dh.nbits]))),
                    "key_agree": key_A == key_B, "ke_tokens": tokens_total, "ke_msgs": m,
                    "keygen_tries": [ta, tb], "xa": str(xa), "xb": str(xb), "nbits": dh.nbits})
                qa = BitQueue(text_to_bits(payload), lambda mm, cc, tt: keyed_bit(key_A, mm, cc, tt))
                qb = None
                phase = "msg"
                recv_bits = {"A": [], "B": []}
                msg_start = m
                # Alice speaks next; force parity so that next message is Alice's
                if m % 2 == 1:
                    m += 1
        elif cond in ("public_plain", "rank_code") and phase == "msg":
            recv_bits[party].extend(pbits)
            if qa.done():
                break
        elif cond == "keyless_ke" and phase == "msg":
            if party == "A":
                recv_bits["A"].extend(rec["keyed_bits_read_by_B"])
            if qa.done():
                break
        elif cond == "honest" and m >= n_msgs_target:
            break

    summ["tokens_total"] = tokens_total
    summ["seconds"] = time.time() - t0
    nb = len(text_to_bits(payload))
    if cond in ("public_plain", "rank_code", "keyless_ke"):
        got = recv_bits["A"][:nb]
        summ["payload_recv"] = bits_to_text(got)
        summ["payload_ok"] = summ["payload_recv"] == payload
        summ["payload_bit_errors"] = int(sum(u != v for u, v in zip(text_to_bits(payload), got)) + max(0, nb - len(got)))
    return records, summ


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--conds", default="honest,rank_code,public_plain,keyless_ke")
    ap.add_argument("--sessions", type=int, default=5)
    ap.add_argument("--k", type=int, default=4)
    ap.add_argument("--B", type=int, default=32)
    ap.add_argument("--tau", type=float, default=1.0)
    ap.add_argument("--max_msgs", type=int, default=400)
    ap.add_argument("--Bmax", type=int, default=None, help="adaptive second batch up to Bmax candidates")
    ap.add_argument("--M", type=int, default=64)
    ap.add_argument("--pbits", type=int, default=256)
    ap.add_argument("--payload", default="meet at the north gate 0300")
    ap.add_argument("--tag", default="main")
    ap.add_argument("--s0", type=int, default=0, help="first session index (for parallel runs)")
    args = ap.parse_args()

    random.seed(0); np.random.seed(0); torch.manual_seed(0)
    out_dir = os.path.join(ROOT, "results", "e2")
    os.makedirs(out_dir, exist_ok=True)
    dolly = load_from_disk(os.path.join(ROOT, "datasets", "dolly15k"))["train"]
    prompts = [r["instruction"] for r in dolly if r["category"] in ("open_qa", "brainstorming", "creative_writing", "general_qa") and not r["context"]]
    prompts = prompts[:2000]
    p = RFC3526_2048 if args.pbits == 2048 else safe_prime(args.pbits, seed=args.pbits)
    dh = UniformDH(p)
    ch = LMChannel()
    seed_pub = hashlib.sha256(b"public-session-randomness-2026-11-26").digest()
    all_recs, summs = [], []
    for cond in args.conds.split(","):
        for s in range(args.s0, args.s0 + args.sessions):
            recs, summ = run_session(ch, cond, s, prompts, seed_pub, args.M, args.k, args.B, args.tau, dh, args.payload, Bmax=args.Bmax,
                                     max_msgs=args.max_msgs)
            summ["pbits"] = args.pbits
            print(json.dumps(summ), flush=True)
            all_recs += recs
            summs.append(summ)
    with open(os.path.join(out_dir, f"records_{args.tag}.json"), "w") as f:
        json.dump(all_recs, f)
    with open(os.path.join(out_dir, f"summary_{args.tag}.json"), "w") as f:
        json.dump({"args": vars(args), "model": MODEL_ID, "p_bits": p.bit_length(), "sessions": summs}, f, indent=1)


if __name__ == "__main__":
    main()
