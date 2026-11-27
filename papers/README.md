# Downloaded Papers (29 PDFs; extracted text in `papers/text/`)

Grouped by role. ★ = deep-read / most central.

## A. Keyless covert communication between AI agents (core)
1. ★ **Undetectable Conversations Between AI Agents via Pseudorandom Noise-Resilient Key Exchange** — Vaikuntanathan & Zamir, 2026, arXiv 2604.04757 — `2604.04757_undetectable_conversations_keyless_key_exchange.pdf`. Proves agents with NO shared key can covertly do key exchange and then hold a hidden conversation, indistinguishable from honest transcripts even to an auditor knowing models & contexts; needs only constant min-entropy per message + public randomness. Introduces PNR-KE; impossibility results.
2. ★ **Codetta: High-Capacity, Keyless, and Undetectable Multi-Agent Collusion** — Pang, Smith, Zheng, 2026, arXiv 2609.28900 — `2609.28900_codetta_keyless_collusion.pdf`. First implemented steganographic KE between LLM agents (MLWE/ML-KEM-512 in honest samples; 128-bit key in ~80k tokens); keyed asymmetric channel 0.03–0.45 bits/token.
3. **Tool Use Enables Undetectable Steganography in Multi-Agent LLM Systems** — Rippin et al., 2026, arXiv 2606.28425. Agentic coding models build provably-secure stegosystems themselves when given tools.
4. **Hopper, Langford, von Ahn — Provably Secure Steganography** (CRYPTO 2002) — `hopper2002_provably_secure_steganography.pdf`. Foundational complexity-theoretic steganography (symmetric key; rejection sampling).
5. **Provably Secure Public-Key Steganography Based on Admissible Encoding** — Zhang et al., 2025, arXiv 2504.19454. Public-key steg (no pre-shared key) via elliptic-curve uniform encodings.

## B. Keyed LM steganography / watermarking primitives
6. **Undetectable Watermarks for Language Models** — Christ, Gunn, Zamir, 2023, arXiv 2306.09194.
7. **Excuse me, sir? Your language model is leaking (information)** — Zamir, 2024, arXiv 2401.10360 (code: code/zamir-steg).
8. **Pseudorandom Error-Correcting Codes** — Christ & Gunn, 2024, arXiv 2402.09370 (secret-key; VZ26 proves no public analogue).
9. **Perfectly Secure Steganography Using Minimum Entropy Coupling** — Schroeder de Witt et al., 2022, arXiv 2210.14889 (code: code/mec-steganography).
10. **Robust Steganography from Large Language Models** — Perry et al., 2025, arXiv 2504.08977 (robustness to re-randomization/paraphrase attacks).

## C. Empirical LLM secret collusion & steganography
11. ★ **Secret Collusion among AI Agents: Multi-Agent Deception via Steganography** — Motwani et al., 2024 (NeurIPS), arXiv 2402.07510. Formal framework (common knowledge, grounding, Schelling points), CASE eval suite.
12. ★ **Hidden in Plain Text: Emergence & Mitigation of Steganographic Collusion in LLMs** — Mathew et al., 2024, arXiv 2410.03768. Steg collusion emerges under misspecified reward (GBRL/ICRL); paraphrasing not fully effective.
13. ★ **Early Signs of Steganographic Capabilities in Frontier LLMs** — Zolkowski et al., 2025, arXiv 2507.02737 (code: code/steganographic-evals). Without prior coordination models basically fail to pass messages undetected.
14. ★ **Subversion via Focal Points: Investigating Collusion in LLM Monitoring** — Järviniemi, 2025, arXiv 2507.03010. Isolated Claude 3.7 instances Schelling-coordinate on collusion signal: 3.4% success, sometimes non-obvious focal points.
15. **Preventing Language Models From Hiding Their Reasoning** — Roger & Greenblatt, 2023, arXiv 2310.18512 (paraphrasing defense, capacity bounds).
16. **LLMs can learn and generalize steganographic CoT under process supervision** — Skaf et al., 2025, arXiv 2506.01926.
17. **Learning Steganography Is Easy, Learning Steganographic Reasoning Is Hard** — Schulz et al., 2026, arXiv 2609.39838.
18. **NEST: Nascent Encoded Steganographic Thoughts** — Karpov, 2026, arXiv 2602.14095.
19. **Conceptual Steganography** — Zhou & May, 2026, arXiv 2605.26537 (paraphrase-robust channel via reasoning-behaviour patterns).
20. **Audit the Whisper: Detecting Steganographic Collusion in Multi-Agent LLMs** — Tailor, 2025, arXiv 2510.04303 (capacity analysis of paraphrase/rate-limit interventions).
21. **What Do Collusion Probes Read?** — Mohsin & Rahman, 2026, arXiv 2611.10620 (probe-based monitors mostly read the instruction).
22. **Open Challenges in Multi-Agent Security** — Schroeder de Witt et al., 2025, arXiv 2505.02077.

## D. Implicit shared keys: shared weights, focal points, self-recognition
23. ★ **Subliminal Learning** — Cloud et al., 2025, arXiv 2507.14805. Traits transmitted through semantically unrelated data *only when teacher & student share base model* → shared weights act like a shared key.
24. **Tacit Coordination of Large Language Models** — 2026, arXiv 2601.22184 (code: code/focal-points). LLMs match/beat humans on focal-point games; fail on numerical/cultural salience.
25. **Self-Recognition in Language Models** — Davidson et al., 2024, arXiv 2407.06946 (no general self-recognition).

## E. Emergent communication (MARL) background
26. **Learning to Protect Communications with Adversarial Neural Cryptography** — Abadi & Andersen, 2016, arXiv 1610.06918 (Alice/Bob/Eve learn encryption — but WITH a shared key).
27. **Learning to Communicate with Deep Multi-Agent RL** — Foerster et al., 2016, arXiv 1605.06676.
28. **Natural Language Does Not Emerge 'Naturally' in Multi-Agent Dialog** — Kottur et al., 2017, arXiv 1706.08502 (emergent codes are uninterpretable/arbitrary).
29. **Emergent Multi-Agent Communication in the Deep Learning Era** — Lazaridou & Baroni, 2020, arXiv 2006.02419 (survey).

## Not obtained (Cloudflare-blocked on IACR ePrint; no mirror found)
- von Ahn & Hopper, *Public-Key Steganography*, EUROCRYPT 2004 (ePrint 2003/233) — covert key exchange foundations.
- Kaptchuk et al., *Meteor: Cryptographically Secure Steganography for Realistic Distributions*, CCS 2021 (ePrint 2021/686) — implementation in code/mec-steganography/src/meteor.py.
- Horel, Park, Richelson, Vaikuntanathan, *How to Subvert Backdoored Encryption* (ITCS 2019, arXiv 1802.07381 — available on arXiv if needed).
- Cachin, *An Information-Theoretic Model for Steganography* (1998).
