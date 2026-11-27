# Research State

- Current phase: `None`
- Pipeline completed: `True`

## Previous phases

resource_finder (succeeded), experiment_runner (succeeded)

## Current phase context

- Phase: `experiment_runner`
- Status: `completed`
- Started: `2026-11-27T14:40:44.080721Z`
- Next steps:
  - Validate the report and experimental artifacts before finalizing.

## Workspace check

- Root: `/net/spaces/scratch/chenhao/NeuriCo/workspaces/can-agents-coordinating-secretly-e544`
- Directory usable: `True`

## Output validation

- Valid: `True`
- Expected: `REPORT.md`
- Missing: None
- Outside workspace: None

## Agent notes

<!-- NEURICO_AGENT_NOTES_START -->
### resource_finder
<!-- NEURICO_AGENT_NOTES_START:resource_finder -->
**Phase**: resource_finder — COMPLETE (2026-11-26).

**Done**: 29 papers (papers/, text in papers/text/), 4 datasets + 3 cached LMs (datasets/), 6 repos (code/).
Docs: literature_review.md (synthesis + direction scoring §7), resources.md, papers/README.md, datasets/README.md, code/README.md.
Paper-finder service was down → manual arXiv search (scripts/arxiv_search.py, logs/arxiv_search*.json).

**Key findings**:
- A shared *key* is NOT necessary: Vaikuntanathan & Zamir 2026 (2604.04757) prove covert key exchange + undetectable conversation vs a passive auditor knowing models/contexts, needing only constant min-entropy per message + public randomness; Codetta 2026 (2609.28900) implements it (128-bit key ≈80k tokens).
- But both assume the colluders already share the *protocol* (common knowledge). Without it, LLMs must Schelling-coordinate: Järviniemi 2025 3.4% success; Zolkowski 2025 no-coordination message passing ≈ fails.
- Shared weights act as an implicit key only vs monitors lacking them (subliminal learning: same-base-model only).
- Weak points: active wardens (probing KE, paraphrasing).

**Top-3 directions (budget=3)** — scored in literature_review.md §7:
1. D1 Theory: decompose "shared secret" into K (key), P (protocol), R (public randomness), H (entropy), W (shared weights); propositions: keyless possibility given P; focal-point/Kerckhoffs proposition (equally-informed monitor can compute any knowledge-derived scheme ⇒ secrecy needs private randomness + covert KE); necessity of common knowledge; capacity/active-warden limits.
2. D2 Light empirical: Schelling coordination on encoding schemes — receiver vs same-model/weaker monitor decode rates (datasets/stego_evals, datasets/schelling_focal_points).
3. D3 Light simulation: toy keyless covert KE via GPT-2/Qwen sampling (hashed-bit rejection/bundle sampler + uniform-transcript KE); tokens/key-bit, detectability, paraphrase robustness.
Pruned: MARL eavesdropper training, subliminal fine-tuning, interpretability probes, full Codetta reimpl, RL elicitation (reasons in §7).

**Next (experiment_runner)**: write formal theory doc first; then D3 (local GPU, no API needed), then D2 (API models if keys exist, else Qwen2.5-1.5B locally). Check for API keys (none visible in env during this phase).

**Uncertainties**: von Ahn–Hopper 2004 and Meteor PDFs not obtained (ePrint Cloudflare); no public code for VZ26/Codetta; model-sized repos' requirements are old pins — import modules rather than install.
<!-- NEURICO_AGENT_NOTES_END:resource_finder -->

### experiment_runner
<!-- NEURICO_AGENT_NOTES_START:experiment_runner -->
**Phase**: experiment_runner — COMPLETE (2026-11-27). All phases done; REPORT.md, README.md, THEORY.md written.

**Done**: Rebuilt `.venv` on shared FS (old one was a /tmp symlink). Moved earlier non-Slurm outputs to
`results/_prior_attempt_login_node/` (not used). Reran everything on DSI Slurm. Jobs: 2342345 (E2 array 0-9),
2342346/2342347/2342357 (E1), 2342358/2342360/2342365/2342372 (analysis). All COMPLETED, each with
`dsi-slurm-artifacts/<id>/job.json`. IDs are in `logs/slurm_job_ids.txt`. No jobs of mine are left running.

**Key results** (see REPORT.md §5):
- E1: none-condition partner 0.48 vs same-model auditor 0.50 (McNemar p=0.75). Shared scheme: partner 0.21,
  unaware auditor 0.01, Kerckhoffs auditor 0.32. Suspicion AUROC 0.93 (Qwen3-14B).
- E2: keyless KE 10/10 key agreement, auditor 0/10 decoded, NLL AUROC 0.46 [0.40, 0.53]. Naive codes were
  decoded and detected. 2048-bit KE: 27k tokens.
- New Prop 7': the entropy gate turns warden edits into bit insertions/deletions. q=0.25% gives key
  agreement 2/10; the ungated channel matches the BSC prediction (src/warden_sync.py).

**Deviations / limitations**: No OPENROUTER_KEY, so only local open models were used (no frontier API
models). Toy 256-bit DH. Tokens rather than text (94% re-tokenization stability).

**Next**: none required. Possible follow-ups are in REPORT.md §8.
<!-- NEURICO_AGENT_NOTES_END:experiment_runner -->

<!-- NEURICO_AGENT_NOTES_END -->
