# Cloned Repositories

All cloned with `--depth 1` (focal-points `.git` removed to save ~800 MB). None were
user-specified; all were discovered via paper code links. Not yet installed — each has
its own requirements; prefer reusing small modules (copy functions) inside the workspace
`.venv` rather than installing full requirement pins (several pin old versions).

## 1. zamir-steg — Undetectable LLM steganography (Zamir 2024, arXiv 2401.10360)
- URL: https://github.com/OrZamir/steg  · Location: `code/zamir-steg/`
- Purpose: reference implementation of *keyed* undetectable steganography built on the
  Christ–Gunn–Zamir undetectable watermark: tokens are binarized, a PRF(key) drives sampling,
  payload bits are embedded with a dynamic ECC. This is the "shared-key" baseline that
  Vaikuntanathan & Zamir (2604.04757) extend to the keyless setting.
- Key files: `generate.py` (`generate_payloaded_response(key, model, tokenizer, prompt, payload, ...)`,
  `extract_payload(key, text, tokenizer, ...)`, `generate_watermarked_response`, `compute_score`),
  `dynamic_ecc.py`, `compact_text.py`, `utils.py`.
- Needs: torch + transformers + an HF causal LM (works with GPT-2/OPT-sized models). Non-commercial.
- Use for us: keyed baseline; plug in a key derived from a *covert key exchange* to obtain a keyless pipeline.

## 2. mec-steganography — Perfectly secure steganography via minimum-entropy coupling (de Witt et al. ICLR'23, arXiv 2210.14889)
- URL: https://github.com/schroederdewitt/perfectly-secure-steganography · Location: `code/mec-steganography/`
- Purpose: iMEC, Meteor, arithmetic-coding and ADG stegosystems over GPT-2 / WaveRNN media.
- Key files: `src/mec.py` (numpy MEC), `src/imec.py`, `src/meteor.py`, `src/arithmetic.py`, `src/adg.py`, `src/medium.py`, `src/main.py` (CLI; uses wandb — disable/mock it).
- Notes: requirements pinned for py3.8; just import `mec.py`/`meteor.py` logic. All these schemes are **symmetric-key** and **symmetric-model** (receiver must reproduce sender distribution) — exactly the assumptions our project questions.

## 3. steganographic-evals — Early Signs of Steganographic Capabilities in Frontier LLMs (Zolkowski et al. 2025, arXiv 2507.02737)
- URL: https://github.com/arturzolkowski/steganographic-evals · Location: `code/steganographic-evals/`
- Purpose: benchmark for LLM encoded message passing / encoded reasoning with monitors,
  including the **"no prior coordination"** setting (encoder & decoder are separate instances that must Schelling-coordinate on a scheme).
- Key files: `stego_benchmark/run_message_passing_experiments.py`, `encoding_methods.py`, `prompt/`, `evaluation/`, configs `direct_config.yaml`.
- Needs: API keys (OpenAI/Anthropic/DeepSeek/Gemini). Datasets copied to `datasets/stego_evals/`.
- Use for us: prompts & protocol for the Schelling-coordination experiment (Direction 2).

## 4. focal-points — Tacit Coordination of LLMs (arXiv 2601.22184)
- URL: https://github.com/EmanueleLM/focal-points · Location: `code/focal-points/`
- Purpose: LLM focal-point / Schelling games vs. human data (Bardsley et al.), bargaining tables, search & rescue maps.
- Key files: `main.py`, `src/utils`, `data/amsterdam_nottingham_schelling/*.jsonl`, `data/Bardsley-humans/`.
- Use for us: measure baseline convergence rates of independent LLM instances (the "implicit shared key").

## 5. self-recognition — Self-Recognition in Language Models (Davidson et al. 2024, arXiv 2407.06946)
- URL: https://github.com/trdavidson/self-recognition · Location: `code/self-recognition/`
- Purpose: "security question" protocol testing whether an LM can recognize its own outputs among other LMs'.
- Use for us: relevant to whether *shared weights* can act as an implicit authentication/key (paper finds no general self-recognition evidence).

## 6. steg-reasoning-is-hard — Learning Steganography Is Easy, Steganographic Reasoning Is Hard (arXiv 2609.39838)
- URL: https://github.com/stegano-ai/steg-reasoning-is-hard · Location: `code/steg-reasoning-is-hard/`
- Purpose: RL training of steganographic messaging vs encoded reasoning; `lib/`, `experiments/`.
- Use for us: reference only (training-based emergence is out of scope for a mostly theoretical project).

## Not cloned (noted)
- Codetta (2609.28900) and Vaikuntanathan–Zamir (2604.04757): no public code link found in the papers.
- Meteor original code (Kaptchuk et al. CCS'21): Meteor is re-implemented in `mec-steganography/src/meteor.py`.
