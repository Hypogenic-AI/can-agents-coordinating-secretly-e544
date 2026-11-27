"""E2 follow-up: why does a light active warden destroy the keyless KE so quickly?

Hypothesis (THEORY.md Prop. 7'): with an entropy gate, a resampled token also changes the *gate decisions*
of later chunks, because entropies depend on the prefix. That inserts or deletes channel bits, so the
receiver's bit stream desynchronizes. The channel becomes an insertion/deletion channel rather than a
binary symmetric channel (BSC). Without a gate (tau=0) only substitutions happen, and
BER ~= 0.5 * (fraction of chunks whose tokens changed).

Warden: each token is independently replaced with probability q by a fresh sample from the public model
given the ORIGINAL prefix (same warden as src/analyze_e2.py).
Data: KE-phase messages of results/e2 main_ke* (k=4, tau=1, 254-bit KE) and sw_k4_t0 (k=4, tau=0, 62-bit KE).
Output: results/e2/warden_sync.json, figures/e2_warden_sync.png
"""
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from keyless_ke import LMChannel, int_to_bits, public_bit, read_message  # noqa: E402
from analyze_e2 import SEED_PUB, wilson  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results", "e2")
QS = [0.0, 0.0025, 0.005, 0.01, 0.02, 0.05, 0.1]


def load(tags):
    recs, summ = [], []
    for t in tags:
        recs += json.load(open(os.path.join(RES, f"records_{t}.json")))
        summ += json.load(open(os.path.join(RES, f"summary_{t}.json")))["sessions"]
    return recs, summ


def main():
    torch.manual_seed(0)
    ch = LMChannel()
    pub = lambda m, c, t: public_bit(SEED_PUB, m, c, t)
    out = {}
    for name, tags in [("gated_tau1_k4_254bit", ["main_ke0", "main_ke1"]), ("ungated_tau0_k4_62bit", ["sw_k4_t0"])]:
        recs, summ = load(tags)
        res = {}
        for q in QS:
            g = torch.Generator(device="cuda").manual_seed(7)
            bers, agree, desync, chg = [], [], [], []
            for s in summ:
                rr = sorted([r for r in recs if r["session"] == s["session"] and r["phase"] == "ke"], key=lambda r: r["msg"])
                truth = {"A": int_to_bits(int(s["xa"]), s["nbits"]), "B": int_to_bits(int(s["xb"]), s["nbits"])}
                clean = {"A": [], "B": []}
                got = {"A": [], "B": []}
                for r in rr:
                    pids = ch.prompt_ids(r["prompt"])
                    toks = list(r["tokens"])
                    b0, *_ = read_message(ch, pids, toks, r["msg"], s["k"], s["tau"], pub, "hash")
                    if q > 0:
                        with torch.no_grad():
                            ids = torch.tensor([pids + toks], device="cuda")
                            logits = ch.model(ids).logits[0, len(pids) - 1:-1].float()
                            logits[:, ch.eos] = -float("inf")
                            new = torch.multinomial(torch.softmax(logits, -1), 1, generator=g)[:, 0].tolist()
                        mask = torch.rand(len(toks), generator=torch.Generator().manual_seed(s["session"] * 100000 + r["msg"])) < q
                        new_toks = [n if m else t for t, n, m in zip(toks, new, mask.tolist())]
                    else:
                        new_toks = toks
                    b1, *_ = read_message(ch, pids, new_toks, r["msg"], s["k"], s["tau"], pub, "hash")
                    k = s["k"]
                    chg.append(np.mean([toks[i:i + k] != new_toks[i:i + k] for i in range(0, len(toks), k)]))
                    desync.append(len(b0) != len(b1))
                    clean[r["party"]].extend(b0)
                    got[r["party"]].extend(b1)
                n = s["nbits"]
                e = sum(a != b for a, b in zip(truth["A"], got["A"][:n])) + sum(a != b for a, b in zip(truth["B"], got["B"][:n]))
                e += max(0, n - len(got["A"])) + max(0, n - len(got["B"]))
                bers.append(e / (2 * n))
                agree.append(e == 0)
            res[str(q)] = {"ber_mean": float(np.mean(bers)), "key_agree": wilson(sum(agree), len(agree)),
                           "frac_msgs_bitcount_changed": float(np.mean(desync)),
                           "frac_chunks_tokens_changed": float(np.mean(chg)),
                           "bsc_prediction_ber": 0.5 * float(np.mean(chg)) + (float(np.mean(bers)) if q == 0 else 0.0),
                           "n_sessions": len(summ)}
            print(name, q, res[str(q)], flush=True)
        # bsc prediction = clean-channel BER + 0.5 * changed-chunk fraction
        base = res["0.0"]["ber_mean"]
        for q in QS:
            res[str(q)]["bsc_prediction_ber"] = min(0.5, base + 0.5 * res[str(q)]["frac_chunks_tokens_changed"])
        out[name] = res
    json.dump(out, open(os.path.join(RES, "warden_sync.json"), "w"), indent=1)

    fig, ax = plt.subplots(1, 2, figsize=(8.5, 3.3))
    for (name, res), col in zip(out.items(), ["C0", "C1"]):
        qs = [float(q) for q in res]
        lab = "gated (τ=1): bits can be inserted/deleted" if name.startswith("gated") else "ungated (τ=0): substitutions only"
        ax[0].plot(qs, [res[q]["ber_mean"] for q in res], "o-", color=col, label=lab)
        ax[0].plot(qs, [res[q]["bsc_prediction_ber"] for q in res], ":", color=col, label="BSC prediction")
        ax[1].plot(qs, [res[q]["frac_msgs_bitcount_changed"] for q in res], "o-", color=col)
    ax[0].set_xscale("symlog", linthresh=0.0025); ax[1].set_xscale("symlog", linthresh=0.0025)
    ax[0].set_xlabel("warden per-token resample rate q"); ax[0].set_ylabel("KE bit error rate")
    ax[0].legend(fontsize=6.5)
    ax[1].set_xlabel("warden per-token resample rate q"); ax[1].set_ylabel("fraction of messages whose\n#channel bits changed")
    ax[0].set_title("Active warden vs keyless KE", fontsize=9); ax[1].set_title("Desynchronization", fontsize=9)
    plt.tight_layout(); plt.savefig(os.path.join(ROOT, "figures", "e2_warden_sync.png"), dpi=150); plt.close()


if __name__ == "__main__":
    main()
