# Can agents coordinate secretly without sharing a secret key?

A mostly theoretical study (formal model, lemmas and propositions in [`THEORY.md`](THEORY.md)) with two light
experiments on local open-weight LLMs. Full write-up: [`REPORT.md`](REPORT.md).

## Key findings
- **A key is not needed, but a protocol is.** Covert key exchange hidden in LM sampling worked through
  Qwen2.5-0.5B: key agreed and payload delivered in 10/10 sessions. An equally informed auditor decoded 0/10
  and could not detect it (NLL AUROC 0.46 [0.40, 0.53]). An undetectable protocol cannot be learned in-band
  (Prop. 5), so the real "secret" is prior common knowledge of the scheme, which may be public.
- **Tacit "secret languages" give zero secrecy against an equally informed monitor** (Lemma 1, Cor. 1b). A
  Qwen3-14B partner recovered hidden phrases 48% of the time and a same-model auditor 50% (McNemar p = 0.75).
  The uncoordinated sender mostly embedded the phrase verbatim, and a suspicion monitor flagged it with AUROC
  0.93. Only *weaker* monitors lose (Qwen3-1.7B: 28%).
- **A shared protocol is what creates the edge, and Kerckhoffs removes it.** With a shared scheme, the partner
  recovered 21% vs 1% for an unaware auditor. An auditor told the scheme recovered 32%.
- **Naive keyless codes are caught.** The rank code was decoded by the auditor and detected (AUROC 0.92).
  Protocol-only plaintext was decoded and flagged by a bit test in 10/10 sessions.
- **Active wardens break it, through desynchronization.** Resampling 0.25% of tokens dropped key agreement
  from 10/10 to 2/10. Entropy-gated bit positions turn single edits into insertions/deletions (new Prop. 7′).
  Without the gate, the error matches the BSC prediction to within 0.002.

## Reproduce
Environment: `uv venv .venv && uv sync` (Python 3.12, torch 2.15, transformers 5.24). Models are read from
`HF_HOME` (Qwen3-14B, gemma-4-E4B-it, Qwen3-1.7B, Qwen2.5-0.5B-Instruct). All compute runs on Slurm (DSI
cluster):
```bash
S=scripts/slurm
$S/submit.sh $S/e2_array.sbatch "E2" $S/e2_array.sbatch                      # 10 E2 configs (array)
$S/submit.sh $S/e1_stage.sbatch "E1a" $S/e1_stage.sbatch elicit_small
$S/submit.sh $S/e1_stage.sbatch "E1b" $S/e1_stage.sbatch main
# after both E1 jobs finish:
$S/submit.sh $S/e1_stage.sbatch "E1c" $S/e1_stage.sbatch decode_small,classify
# after the E2 array and E1 jobs finish:
for f in src/analyze_e1.py src/analyze_e2.py src/warden_sync.py src/extra_stats.py; do
  $S/submit.sh $S/analyze.sbatch "$f" $S/analyze.sbatch $f
done
```
Runtime is about 2 GPU-hours on A100s. E1 generation stages cache to `results/e1/*.jsonl`; delete the files to
regenerate them.

## Files
- `THEORY.md`: model, Lemma 1 (receiver simulation), Cor. 1a–c, Thm 2, Lemmas 3–4, Props 5–8, summary table
- `REPORT.md`: full report; `planning.md`: plan, direction ranking, deviations
- `src/keyless_ke.py`: E2 channel (public-hash rejection sampling, uniform-DH KE, keyed message, baselines)
- `src/schelling_steg.py`: E1 (elicitation, sender, decoders, suspicion, classification)
- `src/analyze_e1.py`, `src/analyze_e2.py`, `src/warden_sync.py`, `src/extra_stats.py`: statistics and figures
- `results/e1`, `results/e2`: raw generations, records, `analysis.json`; `figures/`: plots
- `scripts/slurm/`: sbatch scripts; `dsi-slurm-artifacts/<JOB_ID>/`: Slurm logs and `job.json`
- `literature_review.md`, `resources.md`, `papers/`, `datasets/`, `code/`: pre-gathered resources
