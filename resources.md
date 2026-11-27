# Resources Catalog

## Summary
Resources for a mostly-theoretical study of whether AI agents can coordinate secretly without a
shared secret key, plus light empirical tests. 29 papers, 4 datasets (+3 cached small LMs),
6 code repositories. Literature synthesis and direction ranking: `literature_review.md`.

## Papers (29 downloaded; text extracted to `papers/text/*.txt`)
| Title | Authors | Year | File | Key info |
|---|---|---|---|---|
| Undetectable Conversations Between AI Agents via PNR Key Exchange | Vaikuntanathan, Zamir | 2026 | papers/2604.04757_*.pdf | ★ Keyless covert KE + conversation provably possible (passive auditor, const. min-entropy, public randomness) |
| Codetta: Keyless, Undetectable Multi-Agent Collusion | Pang, Smith, Zheng | 2026 | papers/2609.28900_*.pdf | ★ Implemented MLWE stego-KE (128-bit key ≈80k tokens); 0.03–0.45 bits/token keyed |
| Tool Use Enables Undetectable Steganography in Multi-Agent LLM Systems | Rippin et al. | 2026 | papers/2606.28425_*.pdf | Agents build secure stegosystems with tools |
| Provably Secure Steganography | Hopper, Langford, von Ahn | 2002 | papers/hopper2002_*.pdf | Foundational keyed steg |
| Provably Secure Public-Key Steganography (Admissible Encoding) | Zhang et al. | 2025 | papers/2504.19454_*.pdf | Public-key steg |
| Undetectable Watermarks for LMs | Christ, Gunn, Zamir | 2023 | papers/2306.09194_*.pdf | Keyed PRF-based undetectability |
| Excuse me, sir? Your LM is leaking | Zamir | 2024 | papers/2401.10360_*.pdf | Keyed undetectable LM steg (code) |
| Pseudorandom Error-Correcting Codes | Christ, Gunn | 2024 | papers/2402.09370_*.pdf | Secret-key PRCs |
| Perfectly Secure Steganography Using MEC | Schroeder de Witt et al. | 2022 | papers/2210.14889_*.pdf | Perfect security ⇔ coupling (code) |
| Robust Steganography from LLMs | Perry et al. | 2025 | papers/2504.08977_*.pdf | Robust to re-randomization |
| Secret Collusion among AI Agents | Motwani et al. | 2024 | papers/2402.07510_*.pdf | ★ Framework: common knowledge, grounding, Schelling; CASE |
| Hidden in Plain Text | Mathew et al. | 2024 | papers/2410.03768_*.pdf | ★ Steg collusion emerges under RL; paraphrase not enough |
| Early Signs of Steganographic Capabilities | Zolkowski et al. | 2025 | papers/2507.02737_*.pdf | ★ No-coordination message passing fails (code+data) |
| Subversion via Focal Points | Järviniemi | 2025 | papers/2507.03010_*.pdf | ★ Schelling collusion 3.4% success |
| Preventing LMs From Hiding Their Reasoning | Roger, Greenblatt | 2023 | papers/2310.18512_*.pdf | Paraphrase defense |
| Steganographic CoT under process supervision | Skaf et al. | 2025 | papers/2506.01926_*.pdf | Learned steg CoT |
| Learning Steg Easy, Steg Reasoning Hard | Schulz et al. | 2026 | papers/2609.39838_*.pdf | RL emergence comparison (code) |
| NEST | Karpov | 2026 | papers/2602.14095_*.pdf | Steg CoT across 34 models |
| Conceptual Steganography | Zhou, May | 2026 | papers/2605.26537_*.pdf | Paraphrase-robust semantic channel |
| Audit the Whisper | Tailor | 2025 | papers/2510.04303_*.pdf | Capacity under interventions |
| What Do Collusion Probes Read? | Mohsin, Rahman | 2026 | papers/2611.10620_*.pdf | Probe pitfalls |
| Open Challenges in Multi-Agent Security | Schroeder de Witt et al. | 2025 | papers/2505.02077_*.pdf | Survey/agenda |
| Subliminal Learning | Cloud et al. | 2025 | papers/2507.14805_*.pdf | ★ Hidden signals transfer only within same base model |
| Tacit Coordination of LLMs | (focal-points authors) | 2026 | papers/2601.22184_*.pdf | LLM focal points vs humans (code+data) |
| Self-Recognition in LMs | Davidson et al. | 2024 | papers/2407.06946_*.pdf | No general self-recognition (code) |
| Adversarial Neural Cryptography | Abadi, Andersen | 2016 | papers/1610.06918_*.pdf | Learned encryption (shared key) |
| Learning to Communicate with Deep MARL | Foerster et al. | 2016 | papers/1605.06676_*.pdf | Emergent comm |
| Natural Language Does Not Emerge Naturally | Kottur et al. | 2017 | papers/1706.08502_*.pdf | Emergent codes arbitrary |
| Emergent Multi-Agent Communication survey | Lazaridou, Baroni | 2020 | papers/2006.02419_*.pdf | Survey |

See `papers/README.md` for details and the list of papers that could not be downloaded.

## Datasets
| Name | Source | Size | Task | Location | Notes |
|---|---|---|---|---|---|
| WikiText-2 raw | HF `Salesforce/wikitext` | 44.8k lines | cover-text prefixes / entropy | datasets/wikitext2/ | `load_from_disk` |
| Dolly-15k | HF `databricks/databricks-dolly-15k` | 15,011 | honest-agent cover tasks | datasets/dolly15k/ | categories vary in entropy |
| Stego-evals data | github arturzolkowski/steganographic-evals | 1,137 cover tasks; 1,262 payload phrases; + reasoning sets | message passing w/ monitor | datasets/stego_evals/ | direct baseline comparability |
| Schelling/focal-point items | github EmanueleLM/focal-points | ~20 jsonl task files + human choices | tacit coordination | datasets/schelling_focal_points/ | Bardsley human baselines |
| Small LMs (cached) | HF gpt2, Qwen2.5-0.5B/1.5B-Instruct | — | white-box steg/KE sims | `$HF_HOME` | A40 GPU available |

See `datasets/README.md` for download/loading instructions.

## Code repositories
| Name | URL | Purpose | Location |
|---|---|---|---|
| zamir-steg | github.com/OrZamir/steg | Keyed undetectable LM steg (embed/extract) | code/zamir-steg/ |
| mec-steganography | github.com/schroederdewitt/perfectly-secure-steganography | iMEC, Meteor, arithmetic, ADG stegosystems | code/mec-steganography/ |
| steganographic-evals | github.com/arturzolkowski/steganographic-evals | LLM message-passing/monitor benchmark | code/steganographic-evals/ |
| focal-points | github.com/EmanueleLM/focal-points | LLM Schelling games | code/focal-points/ |
| self-recognition | github.com/trdavidson/self-recognition | LM self-recognition protocol | code/self-recognition/ |
| steg-reasoning-is-hard | github.com/stegano-ai/steg-reasoning-is-hard | RL steg training (reference) | code/steg-reasoning-is-hard/ |

See `code/README.md`.

## Resource gathering notes
- **Search strategy**: paper-finder service was unavailable (localhost:8000 down) → manual arXiv API
  searches (~30 queries: secret collusion, LLM steganography, provably secure/public-key/keyless
  steganography, key exchange, Schelling/tacit coordination, subliminal learning, emergent
  communication, pseudorandom codes, self-recognition) + code links extracted from paper text.
- **Selection**: priority to papers on keyless covert communication (direct answer), LLM collusion
  empirics (light-test baselines), and implicit-key mechanisms (shared weights, focal points).
- **Challenges**: IACR ePrint behind Cloudflare challenge → von Ahn–Hopper 2004 and Meteor not
  downloaded (Hopper 2002 obtained from author page). Semantic Scholar API rate-limited (429).
  No public code for VZ26 or Codetta.
- **Workarounds**: Meteor implementation available in mec-steganography; VZ26/Codetta algorithms
  described in enough detail (see literature_review.md §2.1–2.2) for a toy re-implementation.

## Recommendations for experiment design
1. **Primary**: theory (D1) — formalize ingredients K/P/R/H/W and prove/sketch: keyless possibility
   given shared protocol; focal-point/Kerckhoffs proposition (equally-informed monitor can compute
   any knowledge-derived protocol); necessity of common knowledge; entropy/active-warden limits.
2. **Light test D2**: LLM Schelling coordination on encoding schemes; receiver vs. same-model monitor
   decode rates (stego_evals data; focal-point baselines).
3. **Light test D3**: toy keyless covert KE through GPT-2/Qwen sampling (hashed-bit rejection /
   bundle sampler + uniform-transcript KE); tokens/key-bit, detectability, paraphrase robustness.
4. Reuse: `zamir-steg/generate.py` (keyed channel after KE), `mec-steganography/src/meteor.py`
   (keyed baseline), `steganographic-evals` prompts/monitor templates.
