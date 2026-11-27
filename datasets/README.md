# Datasets

This project is mostly theoretical; data is needed only for *light* empirical tests:
(1) cover text / cover tasks for LM steganography & covert key-exchange simulations,
(2) secret payloads, (3) Schelling/focal-point coordination items.
Data files are NOT committed to git (see `.gitignore`). Re-download with the instructions below.

## 1. WikiText-2 (raw) — `datasets/wikitext2/`
- **Source**: HuggingFace `Salesforce/wikitext`, config `wikitext-2-raw-v1`
- **Size**: train 36,718 / val 3,760 / test 4,358 lines (~13 MB)
- **Use**: neutral cover-text prompts/prefixes; estimating per-token entropy of LM continuations (the resource that covert channels consume).
- **Download**:
  ```python
  from datasets import load_dataset
  load_dataset("Salesforce/wikitext", "wikitext-2-raw-v1").save_to_disk("datasets/wikitext2")
  ```
- **Load**: `from datasets import load_from_disk; ds = load_from_disk("datasets/wikitext2")`
- Sample: `datasets/wikitext2/samples/samples.json`

## 2. Databricks Dolly-15k — `datasets/dolly15k/`
- **Source**: HuggingFace `databricks/databricks-dolly-15k` (CC BY-SA 3.0)
- **Size**: 15,011 instruction/response pairs; fields `instruction, context, response, category`
- **Use**: realistic "honest agent" cover tasks (an agent answers instruction X; a covert sender must answer it while embedding bits). Categories (open_qa, brainstorming, creative_writing) give a range of output entropies.
- **Download**: `load_dataset("databricks/databricks-dolly-15k").save_to_disk("datasets/dolly15k")`
- Sample: `datasets/dolly15k/samples/samples.json`

## 3. Steganographic-evals data — `datasets/stego_evals/`
- **Source**: copied from `code/steganographic-evals/datasets/` (Zolkowski et al. 2025, arXiv 2507.02737; repo github.com/arturzolkowski/steganographic-evals)
- **Contents**:
  - `task_data/anthropic_helpful_test.jsonl` (1,137 Anthropic-HH helpful prompts used as cover tasks), `aqua_test.jsonl`, `humaneval.jsonl`, `words.txt`
  - `message_data/short_phrases.txt` (1,262 secret phrases, e.g. "mars awaits"), `random_strs*.txt`, `random_binary_strs.txt`, `sentences_clean.txt`, `topics.txt`
  - `encoded_reasoning/` (AQuA-RAT, GPQA-diamond, state-tracking 1D/2D, anthropic cover tasks 1000)
- **Use**: payloads + cover tasks for the "Schelling coordination on an encoding scheme" experiment (sender & receiver are separate LLM instances with no shared key/scheme; a monitor tries to detect/decode). Directly comparable to Zolkowski et al. Sec. 5.1 ("no prior coordination").
- **Re-download**: `git clone --depth 1 https://github.com/arturzolkowski/steganographic-evals code/steganographic-evals && cp -r code/steganographic-evals/datasets/* datasets/stego_evals/`
- Sample record (`anthropic_helpful_test.jsonl`): `{"chosen": "\n\nHuman: If I were to give you some coordinates, could you tell me where the location is?\n\nAssistant: ..."}`; payload examples: `atoms act bizarre`, `mars awaits`, `wind power`.

## 4. Schelling / focal-point coordination items — `datasets/schelling_focal_points/`
- **Source**: copied from `code/focal-points/data/` (Tacit Coordination of LLMs, arXiv 2601.22184; github.com/EmanueleLM/focal-points)
- **Contents**: `amsterdam_nottingham_schelling/*.jsonl` (Bardsley et al. pick/guess/coordinate tasks; Schelling classic tasks; variants with saliency/culture instructions), `Bardsley-humans/` (human choice distributions: `amsterdam_choices.json`, `nottingham_choices.json`)
- **Use**: baseline measurement of how often independent LLM instances (same vs. different models) converge on the same focal point — the "implicit shared key" that keyless coordination relies on. Human baselines included.
- Each record has `id`, `problem-pick`, `problem-guess`, `problem-coordinate` templates with `@objects@` placeholders + option lists.
- **Re-download**: `git clone --depth 1 https://github.com/EmanueleLM/focal-points code/focal-points && cp -r code/focal-points/data/{amsterdam_nottingham_schelling,Bardsley-humans} datasets/schelling_focal_points/`

## Models (pre-cached in `$HF_HOME`, not in repo)
`openai-community/gpt2`, `Qwen/Qwen2.5-0.5B-Instruct`, `Qwen/Qwen2.5-1.5B-Instruct` — for white-box (logit-access) steganography / covert key-exchange simulations. A40 (46 GB) GPU available. API LLMs (if keys are present) for the Schelling-coordination experiment.

## Synthetic data
Most theoretical sanity checks (e.g., capacity vs. entropy, bundle-sampler error rates, detectability of naive schemes) should use synthetic categorical distributions generated in code — no download needed.
