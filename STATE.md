# Research State

- Current phase: `None`
- Pipeline completed: `False`

## Previous phases

resource_finder (succeeded), experiment_runner (failed)

## Current phase context

- Phase: `experiment_runner`
- Status: `failed`
- Started: `2026-11-27T03:41:34.588673Z`
- Next steps:
  - Validate the report and experimental artifacts before finalizing.

## Workspace check

- Root: `/net/spaces/scratch/chenhao/NeuriCo/workspaces/can-agents-coordinating-secretly-e544`
- Directory usable: `True`

## Output validation

- Valid: `False`
- Expected: `REPORT.md`
- Missing: `REPORT.md`
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
Update this section at the end of the `experiment_runner` phase.
<!-- NEURICO_AGENT_NOTES_END:experiment_runner -->

<!-- NEURICO_AGENT_NOTES_END -->
