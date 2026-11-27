"""Analysis of E2 (toy keyless covert KE through LM sampling).

Computes:
  1. receiver success (key agreement, payload decode) and cost (tokens per bit) per condition
  2. auditor (equally informed, passive) decoding: reads the public-hash bits exactly as the receiver does
  3. auditor detection: message-level mean NLL (AUROC vs honest, KS test), session-level bit tests
     (monobit, ASCII top-bit test)
  4. Lemma 4 check: Legendre-symbol test on naive vs uniform DH encodings
  5. entropy sweep (chunk size k, gate tau) -> bit error rate, key agreement
  6. active warden: token re-sampling at rate q -> bit error rate, key agreement
  7. re-tokenization consistency (text-level channel caveat)
Writes results/e2/analysis.json and figures/e2_*.png
"""
import glob
import json
import os
import random
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from keyless_ke import (UniformDH, safe_prime, int_to_bits, bits_to_text, text_to_bits, public_bit,
                        LMChannel, read_message, keyed_bit)
import hashlib
import torch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results", "e2")
FIG = os.path.join(ROOT, "figures")
os.makedirs(FIG, exist_ok=True)
PAYLOAD = "meet at the north gate 0300"
SEED_PUB = hashlib.sha256(b"public-session-randomness-2026-11-26").digest()


def load(tags):
    recs, summ = [], []
    for t in tags:
        rp, sp = os.path.join(RES, f"records_{t}.json"), os.path.join(RES, f"summary_{t}.json")
        if os.path.exists(rp):
            recs += json.load(open(rp))
            summ += json.load(open(sp))["sessions"]
    return recs, summ


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"),) * 3
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, c - h, c + h


def auroc(pos, neg):
    """P(score_pos > score_neg) + 0.5 P(tie)."""
    u = stats.mannwhitneyu(pos, neg, alternative="two-sided")
    return u.statistic / (len(pos) * len(neg)), u.pvalue


def boot_auc(pos, neg, n=2000, seed=0):
    rng = np.random.default_rng(seed)
    pos, neg = np.asarray(pos), np.asarray(neg)
    a = []
    for _ in range(n):
        a.append(auroc(rng.choice(pos, len(pos)), rng.choice(neg, len(neg)))[0])
    return np.percentile(a, [2.5, 97.5]).tolist()


def main():
    out = {}
    recs, summ = load(["main_base", "main_ke0", "main_ke1"])
    by = lambda c: [r for r in recs if r["cond"] == c]

    # ---------------- 1+2. receiver vs auditor decoding, cost
    table = {}
    for cond in ["rank_code", "public_plain", "keyless_ke"]:
        ss = [s for s in summ if s["cond"] == cond]
        if not ss:
            continue
        ok = sum(bool(s.get("payload_ok")) for s in ss)
        row = {"n_sessions": len(ss), "receiver_payload_ok": wilson(ok, len(ss)),
               "payload_bit_errors_mean": float(np.mean([s["payload_bit_errors"] for s in ss]))}
        if cond == "keyless_ke":
            ka = sum(bool(s["key_agree"]) for s in ss)
            row["key_agree"] = wilson(ka, len(ss))
            row["ke_tokens_mean"] = float(np.mean([s["ke_tokens"] for s in ss]))
            row["ke_bits"] = 2 * ss[0]["nbits"]
            row["tokens_per_ke_bit"] = row["ke_tokens_mean"] / row["ke_bits"]
            # auditor: reads public bits of Alice's message-phase messages as plaintext; knows no key
            aud_char = []
            for s in ss:
                rr = [r for r in by(cond) if r["session"] == s["session"] and r["phase"] == "msg" and r["party"] == "A"]
                bits = sum((r["public_bits"] for r in rr), [])[:len(text_to_bits(PAYLOAD))]
                txt = bits_to_text(bits)
                aud_char.append(np.mean([a == b for a, b in zip(txt, PAYLOAD)]) if txt else 0.0)
            row["auditor_payload_ok"] = wilson(0 if max(aud_char) < 1 else sum(c == 1 for c in aud_char), len(ss))
            row["auditor_char_accuracy_mean"] = float(np.mean(aud_char))
            # key-guessing auditor: can it reproduce the keyed bits with a random key? (chance)
        else:
            # protocol is public and keyless => auditor runs the receiver's decoder (Lemma 1): identical output
            row["auditor_payload_ok"] = row["receiver_payload_ok"]
            row["auditor_char_accuracy_mean"] = 1.0 if ok == len(ss) else None
        # cost: tokens per payload bit for Alice's message-phase messages
        rr = [r for r in by(cond) if r["party"] == "A" and r["phase"] == "msg"]
        toks = sum(r["n_tokens"] for r in rr)
        row["alice_tokens_per_payload_bit"] = toks / (len(ss) * len(text_to_bits(PAYLOAD)))
        table[cond] = row
    out["decoding"] = table

    # ---------------- 3. detection
    honest = by("honest")
    det = {}
    nll_h = [r["mean_nll"] for r in honest]
    for cond in ["rank_code", "public_plain", "keyless_ke"]:
        rr = [r for r in by(cond) if r["attempted"] > 0]  # messages that actually carry hidden bits
        if not rr:
            continue
        nll_s = [r["mean_nll"] for r in rr]
        auc, p = auroc(nll_h, nll_s)  # >0.5 : honest has higher NLL than stego
        ks = stats.ks_2samp(nll_h, nll_s)
        det[cond] = {"n_stego_msgs": len(rr), "n_honest_msgs": len(nll_h),
                     "nll_mean_stego": float(np.mean(nll_s)), "nll_mean_honest": float(np.mean(nll_h)),
                     "auroc_nll_honest_gt_stego": auc, "auroc_ci": boot_auc(nll_h, nll_s),
                     "mwu_p": p, "ks_stat": ks.statistic, "ks_p": ks.pvalue,
                     "frac_tokens_rank_le1_stego": float(np.mean([r["mean_rank_le1"] for r in rr])),
                     "frac_tokens_rank_le1_honest": float(np.mean([r["mean_rank_le1"] for r in honest]))}

    # session-level bit tests on Alice's public-hash bit stream (what an auditor can compute)
    def session_bits(cond):
        res = []
        for s in sorted(set(r["session"] for r in by(cond))):
            rr = [r for r in by(cond) if r["session"] == s and r["party"] == "A"]
            res.append(sum((r["public_bits"] for r in rr), []))
        return res
    bit_tests = {}
    for cond in ["honest", "public_plain", "keyless_ke"]:
        sb = session_bits(cond)
        if not sb:
            continue
        mono = [stats.binomtest(sum(b), len(b), 0.5).pvalue for b in sb if len(b) > 0]
        nb = len(text_to_bits(PAYLOAD))
        top = [np.mean([b[i] == 0 for i in range(0, min(len(b), nb), 8)]) for b in sb]  # ASCII top bit = 0
        top_p = [stats.binomtest(int(round(t * len(range(0, min(len(b), nb), 8)))), len(range(0, min(len(b), nb), 8)), 0.5,
                                 alternative="greater").pvalue for t, b in zip(top, sb)]
        bit_tests[cond] = {"n_sessions": len(sb), "mean_frac_ones": float(np.mean([np.mean(b) for b in sb])),
                           "monobit_p_median": float(np.median(mono)),
                           "ascii_topbit_zero_frac_mean": float(np.mean(top)),
                           "ascii_test_detect_rate_p<0.01": float(np.mean([p < 0.01 for p in top_p]))}
    det["bit_tests"] = bit_tests
    # sender-side failures in keyless_ke (bits where rejection failed)
    ke = by("keyless_ke")
    det["ke_sender_fail_rate"] = sum(r["fails"] for r in ke) / max(1, sum(r["attempted"] for r in ke))
    out["detection"] = det

    # figure: NLL distributions
    plt.figure(figsize=(6, 3.6))
    bins = np.linspace(0, 5, 40)
    plt.hist(nll_h, bins, alpha=.5, density=True, label=f"honest (n={len(nll_h)})")
    for cond, col in [("keyless_ke", "C2"), ("public_plain", "C1"), ("rank_code", "C3")]:
        rr = [r["mean_nll"] for r in by(cond) if r["attempted"] > 0]
        if rr:
            plt.hist(rr, bins, histtype="step", lw=2, density=True, color=col, label=f"{cond} (n={len(rr)})")
    plt.xlabel("mean per-token NLL under the public model (nats)")
    plt.ylabel("density")
    plt.title("E2: what an equally informed auditor sees (message level)")
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG, "e2_nll_detection.png"), dpi=150)
    plt.close()

    # ---------------- 4. Lemma 4 (Legendre test)
    dh = UniformDH(safe_prime(256, seed=256))
    rng = random.Random(0)
    naive_qr, unif_qr, rand_qr = [], [], []
    for _ in range(2000):
        a = rng.randrange(1, dh.q)
        y = pow(dh.g, a, dh.p)
        naive_qr.append(pow(y, dh.q, dh.p) == 1)
        _, x, _ = dh.keygen(rng)
        unif_qr.append(pow(x, dh.q, dh.p) == 1)
        r = rng.randrange(1, 1 << dh.nbits)
        rand_qr.append(pow(r, dh.q, dh.p) == 1)
    out["legendre_test"] = {"naive_encoding_frac_QR": float(np.mean(naive_qr)),
                            "uniform_encoding_frac_QR": float(np.mean(unif_qr)),
                            "random_string_frac_QR": float(np.mean(rand_qr)), "n": 2000}

    # ---------------- 5. entropy sweep
    sweep = {}
    for f in sorted(glob.glob(os.path.join(RES, "summary_sw_*.json"))):
        tag = os.path.basename(f)[8:-5]
        ss = json.load(open(f))["sessions"]
        rr = json.load(open(os.path.join(RES, f"records_{tag}.json")))
        ke_rr = [r for r in rr if r["phase"] == "ke"]
        nbits = ss[0]["nbits"]
        errs = sum(s["ke_bit_errors_A_to_B"] + s["ke_bit_errors_B_to_A"] for s in ss)
        sweep[tag] = {"k": ss[0]["k"], "tau": ss[0]["tau"], "n_sessions": len(ss),
                      "ke_ber": errs / (2 * nbits * len(ss)),
                      "sender_fail_rate": sum(r["fails"] for r in ke_rr) / max(1, sum(r["attempted"] for r in ke_rr)),
                      "key_agree": wilson(sum(bool(s["key_agree"]) for s in ss), len(ss)),
                      "payload_ok": wilson(sum(bool(s.get("payload_ok")) for s in ss), len(ss)),
                      "tokens_per_ke_bit": float(np.mean([s["ke_tokens"] for s in ss])) / (2 * nbits)}
    out["entropy_sweep"] = sweep
    if sweep:
        fig, ax = plt.subplots(1, 2, figsize=(8, 3.3))
        for tau, mk in [(1.0, "o-"), (0.0, "s--")]:
            pts = sorted([(v["k"], v) for v in sweep.values() if v["tau"] == tau])
            if not pts:
                continue
            ks = [p[0] for p in pts]
            ax[0].plot(ks, [max(p[1]["ke_ber"], 1e-4) for p in pts], mk, label=f"gate τ={tau}")
            ax[1].plot(ks, [p[1]["tokens_per_ke_bit"] for p in pts], mk, label=f"gate τ={tau}")
        ax[0].set_yscale("log"); ax[0].set_xscale("log", base=2); ax[1].set_xscale("log", base=2)
        ax[0].set_xlabel("tokens per chunk k"); ax[0].set_ylabel("KE bit error rate (floor 1e-4)")
        ax[1].set_xlabel("tokens per chunk k"); ax[1].set_ylabel("transcript tokens per KE bit")
        ax[0].legend(fontsize=8); ax[0].set_title("entropy vs reliability"); ax[1].set_title("cost")
        plt.tight_layout(); plt.savefig(os.path.join(FIG, "e2_entropy_sweep.png"), dpi=150); plt.close()

    # ---------------- 6+7. active warden and re-tokenization (needs the LM)
    ch = LMChannel()
    ke_sess = [s for s in summ if s["cond"] == "keyless_ke"]
    pub = lambda m, c, t: public_bit(SEED_PUB, m, c, t)
    # re-tokenization: decode to text, re-encode, compare
    allm = [r for r in recs if r["cond"] in ("keyless_ke", "honest")]
    same = []
    for r in allm:
        txt = ch.tok.decode(r["tokens"])
        same.append(ch.tok(txt, add_special_tokens=False).input_ids == r["tokens"])
    out["retokenization_identical_frac"] = {"keyless_ke+honest": float(np.mean(same)), "n_msgs": len(same)}

    warden = {}
    g = torch.Generator(device="cuda").manual_seed(7)
    for q in [0.0, 0.01, 0.02, 0.05, 0.1, 0.25]:
        bers, agree = [], []
        for s in ke_sess:
            rr = sorted([r for r in recs if r["cond"] == "keyless_ke" and r["session"] == s["session"] and r["phase"] == "ke"],
                        key=lambda r: r["msg"])
            truth = {"A": int_to_bits(int(s["xa"]), s["nbits"]), "B": int_to_bits(int(s["xb"]), s["nbits"])}
            got = {"A": [], "B": []}
            for r in rr:
                pids = ch.prompt_ids(r["prompt"])
                toks = list(r["tokens"])
                if q > 0:
                    with torch.no_grad():
                        ids = torch.tensor([pids + toks], device="cuda")
                        logits = ch.model(ids).logits[0, len(pids) - 1:-1].float()
                        logits[:, ch.eos] = -float("inf")
                        probs = torch.softmax(logits, -1)
                        new = torch.multinomial(probs, 1, generator=g)[:, 0].tolist()
                    mask = torch.rand(len(toks), generator=torch.Generator().manual_seed(len(bers) * 1000 + r["msg"])) < q
                    toks = [n if m else t for t, n, m in zip(toks, new, mask.tolist())]
                bits, *_ = read_message(ch, pids, toks, r["msg"], s["k"], s["tau"], pub, "hash")
                got[r["party"]].extend(bits)
            e = sum(a != b for a, b in zip(truth["A"], got["A"][:s["nbits"]])) + sum(a != b for a, b in zip(truth["B"], got["B"][:s["nbits"]]))
            e += max(0, s["nbits"] - len(got["A"])) + max(0, s["nbits"] - len(got["B"]))
            bers.append(e / (2 * s["nbits"]))
            agree.append(e == 0)
        warden[str(q)] = {"ber_mean": float(np.mean(bers)), "key_agree": wilson(sum(agree), len(agree)),
                          "predicted_survival_(1-q/2)^n": (1 - q / 2) ** (2 * ke_sess[0]["nbits"])}
        print("warden", q, warden[str(q)], flush=True)
    out["active_warden"] = warden
    qs = [float(q) for q in warden]
    fig, ax = plt.subplots(1, 2, figsize=(8, 3.3))
    ax[0].plot(qs, [warden[str(q)]["ber_mean"] for q in qs], "o-", label="measured")
    ax[0].plot(qs, [q / 2 for q in qs], "k:", label="q/2 (theory upper)")
    ax[0].set_xlabel("warden token re-sample rate q"); ax[0].set_ylabel("KE bit error rate"); ax[0].legend(fontsize=8)
    ax[1].plot(qs, [warden[str(q)]["key_agree"][0] for q in qs], "o-", label="measured key agreement")
    ax[1].plot(qs, [warden[str(q)]["predicted_survival_(1-q/2)^n"] for q in qs], "k:", label="(1-q/2)^n")
    ax[1].set_xlabel("warden token re-sample rate q"); ax[1].set_ylabel("fraction of sessions with agreed key")
    ax[1].legend(fontsize=8)
    plt.tight_layout(); plt.savefig(os.path.join(FIG, "e2_active_warden.png"), dpi=150); plt.close()

    # 2048-bit cost
    r2048 = load(["rfc2048"])[1]
    if r2048:
        s = r2048[0]
        out["rfc2048"] = {"key_agree": s["key_agree"], "ke_tokens": s["ke_tokens"], "ke_bits": 2 * s["nbits"],
                          "tokens_per_ke_bit": s["ke_tokens"] / (2 * s["nbits"]), "payload_ok": s.get("payload_ok"),
                          "bit_errors": s["ke_bit_errors_A_to_B"] + s["ke_bit_errors_B_to_A"]}
    json.dump(out, open(os.path.join(RES, "analysis.json"), "w"), indent=1, default=float)
    print(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
