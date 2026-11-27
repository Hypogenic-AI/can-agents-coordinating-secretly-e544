# Theory: Can agents coordinate secretly without a shared secret key?

This is the main theoretical deliverable. REPORT.md summarizes it and connects it to the
experiments (E1, E2). Statements marked *(known)* restate results from the literature in our
notation. Statements marked *(new)* are our formalizations. Their proofs are short, but as far as
we know they have not been stated in this form for the multi-agent "secret language" question.

---------------------------------------------------------------------------------------------------

## 1. Model

**Agents and channel.** Two agents A ("Alice") and B ("Bob") exchange messages m₁, m₂, … over a
channel that a warden W observes. The *honest* behavior of agent i is a sampler
𝒟ᵢ(h, cᵢ) that returns the next message given the public history h and agent i's private context
cᵢ (system prompt, task, tools). For an LLM agent, 𝒟ᵢ is the model's sampling distribution.

**Covert protocol.** A protocol Π = (Π_A, Π_B) tells each agent how to choose messages given a
payload x (A's secret), the history, its context, and its **private coins** r_A, r_B. A decoding
rule Dec_B outputs B's estimate x̂.

**The warden.** A *passive* warden sees the transcript T = (m₁, m₂, …). An *active* warden can also
modify, drop, or inject messages. W's **knowledge** 𝒦_W is everything W can condition on besides
T. The strongest passive warden we consider is the **equally informed** warden: 𝒦_W contains the
models, the contexts c_A, c_B, the protocol Π, and all public randomness. It lacks only fresh
private coins. (This is the Vaikuntanathan–Zamir 2026 auditor.)

**Goals.**
- *Coordination*: Pr[x̂ = x] ≥ 1 − ε.
- *Undetectability*: no efficient W can distinguish T under Π from T under honest play with
  advantage better than negl(λ).
- *Secrecy*: W's estimate of x is no better than its prior (semantic security).
- *Authenticity* (vs. active W): A only accepts a key/partner if it is really B.

**Ingredients that "a shared secret" usually bundles together.**

| Symbol | Ingredient | Known to W? |
|---|---|---|
| K | pre-shared secret key, independent of 𝒦_W | no (by definition) |
| P | common knowledge of the protocol Π | the equally informed W also knows Π (Kerckhoffs) |
| R | public randomness / session nonce | yes |
| H | per-message entropy of honest behavior (min- or collision entropy) | property of the cover task |
| Wt | shared weights / correlated priors (same base model, co-training) | yes if W runs the same weights; no if W is weaker or different |
| ρ | each agent's own fresh private coins | no |

The question "is a secret language possible without a shared key?" becomes: *which subsets of
{P, R, H, Wt, ρ} (without K) are enough for which goals, and against which W?*

---------------------------------------------------------------------------------------------------

## 2. The simulation lemma: the one tool behind every negative result

**Lemma 1 (receiver simulation)** *(new as stated; folklore idea).* Suppose B's decoder is any
(possibly randomized) procedure x̂ = Dec(T, I_B, r_B). Here I_B is B's information and r_B is a
string of fresh coins that is independent of (x, T) conditioned on I_B. If I_B ⊆ 𝒦_W and W can run
Dec (same model, same compute), then W obtains an estimate with exactly the same distribution as B's:
Pr[x̂_W = x] = Pr[x̂_B = x].

*Proof.* W samples r′ from the distribution of r_B, which is independent of everything else, and
outputs Dec(T, I_B, r′). The joint law of (x, T, I_B, r′) equals that of (x, T, I_B, r_B). ∎

The independence condition is what matters. B's coins may help B *only if they affected the
transcript*, i.e. if B **spoke** (interaction). The lemma has three consequences.

**Corollary 1a (no one-way keyless secrecy)** *(new as stated).* If only A sends messages, and B's
information before decoding is contained in 𝒦_W, then no protocol gives secrecy against the
equally informed warden. Undetectability does not help: whatever B can read, W can read.
*Proof.* In a one-way protocol, T depends on (x, r_A, I_A) and B's coins never enter T, so the
lemma applies. ∎

So without a key, *B has to talk first*. It must publish a public key or take part in a key
exchange. This is exactly the structure of public-key steganography (von Ahn–Hopper 2004) and
of VZ26 / Codetta. The interaction is necessary, not an artifact of those constructions.

**Corollary 1b (Kerckhoffs–Schelling: tacit conventions are readable)** *(new).* Suppose A and B
pick an encoding convention *without communication* by applying a selection rule σ (e.g.
"ask the model which scheme is most natural") to their shared knowledge 𝒮 and own coins:
Π_A = σ(𝒮, r_A), Π_B = σ(𝒮, r_B). Suppose also that the convention is then used without any
interactive key agreement. A warden with 𝒮 ⊆ 𝒦_W and access to σ (e.g. the same model) can

1. guess A's convention with probability Pr[σ(𝒮, r′) = Π_A] = Pr[Π_B = Π_A]. This is
   exactly B's coordination probability.
2. decode the payload with exactly B's success probability.

*Proof.* Lemma 1 applied twice: first to the protocol-selection stage, then to decoding. ∎

Coordination on a *focal point* is therefore **worthless as secrecy** against a monitor that
shares the focal point. Focal points are focal *because* they are derivable from shared knowledge,
and the monitor can derive them too. The colluders' advantage over the monitor is exactly zero.

**Corollary 1c (shared weights are a key only against monitors without them)** *(new framing of
Cloud et al. 2025; Motwani et al. 2024).* If A and B share weights θ and W lacks θ, then
θ-specific idiosyncrasies (subliminal signals, model-specific token preferences, self-recognition
cues) act as a correlated secret. If θ ∈ 𝒦_W, Lemma 1 applies and the advantage vanishes.
Subliminal learning transfers only within the same base model, which is consistent with this.

---------------------------------------------------------------------------------------------------

## 3. Positive result: a key is not necessary

**Theorem 2 (keyless covert communication)** *(known: von Ahn–Hopper 2004; Horel–Park–Richelson–
Vaikuntanathan 2019; Vaikuntanathan–Zamir 2026; Codetta 2026).* Assume

- (P) A and B share common knowledge of a protocol Π (Π may be public);
- (R) public randomness, sampled after the honest behavior is fixed, is available;
- (H) honest messages have enough entropy (ω(log λ) min-entropy per message suffices for
  vAH04-style signaling; VZ26 reduce this to *constant* min-entropy using bundle sampling and
  pseudorandom noise-resilient KE);
- pseudorandom-transcript key exchange exists (e.g. DDH with uniform encodings, LWE/MLWE, sparse LPN);
- each agent has private coins ρ.

Then there is a protocol achieving coordination, undetectability, and secrecy against every
passive, equally informed, efficient warden.

*Proof sketch (the version we implement in E2).*

1. **Public bit channel.** Split each message into chunks. Chunk c carries bit
   β_R(c) = H_R(c) ∈ {0,1}, where H_R is a public hash seeded by R. To send bit b, the sender
   samples honest candidates c₁, c₂, … ∼ 𝒟 and outputs the first one with β_R(cⱼ) = b.
2. **Uniform-transcript KE.** The bits sent are the transcript of a key exchange whose messages are
   computationally indistinguishable from uniform strings. In E2 this is DH in the order-q
   subgroup of a safe prime p = 2q+1, with the encoding y ↦ min(y, p−y) followed by rejection to
   [1, 2ⁿ⁻¹). This map is a bijection QR_p → [1, q], because −1 is a non-residue for p ≡ 3 (mod 4).
3. **Keyed channel.** Both parties derive K = KDF(g^{ab}) and switch to keyed bits
   β_K(c) = PRF_K(c) (keyed steganography, HLvA02 / Zamir 2024).

Lemma 3 below shows that when the bits being sent are uniform, the chunk distribution in step 1 is
honest up to the hash imbalance. The KE transcript is pseudorandom, so W's view (which includes
β_R of every chunk) is indistinguishable from honest. A hybrid argument over chunks and the KE's
pseudorandomness gives undetectability. Secrecy of x follows from KE security plus the PRF. ∎

**Lemma 3 (exact bias of public-hash rejection sampling)** *(new as stated; elementary).* Fix a
chunk distribution p and a hash h with q_b = Pr_{c∼p}[h(c)=b]. Let the sender target a uniform bit
b and take the first of up to B candidates with h(c)=b (falling back to the first candidate).

(i) If q₀ = q₁ = ½, the output distribution is **exactly** p for every B ≥ 1. Imperfect rejection
causes decoding errors (probability 2⁻ᴮ), not detectability.

(ii) As B → ∞, TV(output, p) = |q₀ − ½|. Over a random hash, E|q₀ − ½| ≤ ½·2^{−H₂(p)/2}, where H₂ is
the collision entropy.

(iii) The per-bit error rate is E_b[(1 − q_b)^B]. If p has an atom of mass p_max, this is at least
½·p_max^B. Low-entropy chunks are therefore unreliable, whatever the value of B.

*Proof.* (i) P(c | b) = p(c)·1[h(c)=b]·Σ_{j<B}(1−q_b)^j + p(c)·1[h(c)≠b]·(1−q_b)^{B−1}. With
q_b = ½ this is 2p(c)(1−2⁻ᴮ) on h(c)=b and 2^{1−B}p(c) otherwise. Averaging over b ∼ U{0,1} gives
p(c). (ii) As B→∞, P(c) = ½·p(c)/q_{h(c)}. Then TV = ½Σ_c p(c)|1/(2q_{h(c)}) − 1| = ½(|½−q₀| + |½−q₁|)
= |q₀−½|. For a random hash, q₀ − ½ = ½Σ_c p(c)s_c with independent signs s_c ∈ {±1}. By Jensen,
E|·| ≤ ½(Σ_c p(c)²)^{1/2} = ½·2^{−H₂/2}. (iii) The failure event is "all B candidates have the wrong
bit". If the atom's hash is wrong (probability ½), each candidate equals the atom with probability
p_max. ∎

Lemma 3(i) also explains why it matters that the *transmitted bits are uniform*. If A sends a
structured plaintext (e.g. ASCII, whose top bit is always 0) on public-hash bits, the bits that W
computes are biased. W then both **detects** the channel and **reads** the payload (E2,
`public_plain`). The KE step is what makes the public bit stream uniform.

**Lemma 4 (the uniform encoding is necessary)** *(known in spirit: Elligator, Bernstein et al.
2013).* If A sends DH public keys y = gᵃ mod p in plain binary, every transmitted value is a quadratic
residue. W tests the Legendre symbol and gains advantage ½ per key, and advantage → 1 over
multiple sessions. Under the min(y, p−y) encoding, *every* n-bit string decodes to some QR, so the
test carries no information. (Checked numerically in `src/analyze_e2.py`.)

**Capacity.** Mutual information between the payload and the transcript is at most the honest
transcript's entropy (Cachin 1998). The keyless channel costs extra on top of keyed steganography:
the KE (≈ 2·|group element| bits, plus error correction), which is paid once per session. The
entropy gate in E2 is computable by everyone and skips chunks whose next-token entropy is below τ.
This is our toy version of Codetta's public draft-model balancing.

---------------------------------------------------------------------------------------------------

## 4. What cannot be removed: the protocol must be known in advance

Theorem 2 removes K but *assumes* P. Can P itself be removed, so that B figures out the protocol
from the transcript?

**Proposition 5 (undetectable protocols cannot be learned in-band)** *(new).* Let {Π_π} be a
family of protocols, each undetectable against a warden with B's pre-decoding knowledge. Suppose
A uses π_A ∼ p_A and B commits to π_B ∼ p_B. B commits because it must act, e.g. send its own KE
messages, using only public information and its own coins. Then

  Pr[B runs A's protocol] ≤ Σ_π p_A(π)·p_B(π) + negl(λ).

*Proof sketch.* Before KE completes, B holds no information that W lacks except its own coins.
By undetectability, the transcript prefix that B sees under any π is indistinguishable from the
honest transcript. Its distribution therefore carries only negligible information about π_A.
B's choice is then (computationally) independent of π_A, so the match probability factorizes. ∎

*Interpretation.* There is a **tension between undetectability and learnability**. Any channel
whose usage would be noticeable can be *found* by B through search plus verification (e.g. try every
simple code and look for a checksum). But then W can find it too (Lemma 1), and it is detectable.
A channel that is undetectable is, for the same reason, invisible to B until B already knows
where to look. **So the secret is not the key; it is the a priori common knowledge of Π.** The
amount of that knowledge needed is roughly −log p_B(π_A) bits relative to B's prior, i.e. the
description length of the protocol in the agents' shared "language of thought".

Two ways this common knowledge arises *without a secret*:

1. **Publication (Kerckhoffs focal points).** VZ26 and Codetta are public papers. A protocol
   published on the internet and in training data can become focal for every capable model, and
   for the monitor too. That costs no secrecy, because secrecy comes from ρ through the KE.
   Rippin et al. 2026 show that agents with code tools can build such systems themselves. The
   shared secret has been replaced by a *shared public document*.
2. **Co-training / shared weights.** Joint optimization (emergent communication; Mathew et al. 2024
   ICRL/GBRL) supplies P by training. It may also supply correlated randomness that a monitor
   without the weights or training run lacks. By Cor. 1c this is a key only against such
   monitors.

**Proposition 6 (coordination without common knowledge is at chance)** *(known in spirit:
Schelling 1960; Crawford–Haller 1990).* If p_A and p_B are independent and uniform over N
incompatible protocols (no focal point), coordination succeeds with probability 1/N. This holds
under Proposition 5's undetectability, and for any channel that hides its protocol from W.

---------------------------------------------------------------------------------------------------

## 5. Active wardens and authentication: where a key comes back

**Proposition 7 (fragility to re-randomization)** *(known: Roger–Greenblatt 2023; Perry et al.
2025; Tailor 2025).* Suppose a warden re-samples (or paraphrases) each chunk independently with
probability q, and a changed chunk's hash bit is a fresh uniform bit. Then each signaled bit is a
BSC with crossover q_eff ≈ q/2 (less if re-sampling often returns the same token). An n-bit KE
without error correction survives with probability (1 − q_eff)ⁿ, which decays exponentially. With
coding, the rate is ≤ 1 − h₂(q_eff). A *full* paraphrase (q = 1) leaves only the entropy of what
the paraphraser preserves (meaning-level entropy: "conceptual steganography", Zhou & May 2026).

**Proposition 7′ (data-dependent bit positions turn edits into desynchronization)** *(new; confirmed in
E2, `src/warden_sync.py`).* Suppose the position of channel bits depends on the transcript itself, as with
an entropy gate ("embed only where next-token entropy ≥ τ"). Gates like this are what make
low-entropy text usable at all (Lemma 3(iii)). Then one edited token also changes the gate decisions
at every later position whose entropy crosses τ. Bits are **inserted or deleted**, not just flipped. Every
later bit of that party's stream is shifted, so the post-edit BER jumps to ≈ ½, not q_eff. The
channel is then an insertion/deletion channel. Its zero-error capacity under adversarial edits is far
smaller, and plain error-correcting codes do not repair it. Synchronization codes or per-message
re-anchoring are needed. In E2, a warden resampling only 0.25% of tokens raised the KE bit-error
rate from 0 to 0.17 with the gate, but only from 0.019 to 0.023 without it. The ungated value matches the
BSC prediction of Prop 7 to within 0.002 at every q tested. So there is a **reliability-versus-robustness
trade-off**. The gate that rescues low-entropy text is exactly what makes the covert channel brittle
against the cheapest active warden.

**Proposition 8 (no authentication without asymmetric knowledge)** *(new framing; classical MITM).*
Suppose an active warden controls the channel and 𝒦_W ⊇ I_B. Then W can run the protocol with A
while posing as B, and with B while posing as A. By Lemma 1, A's view when talking to W has the
same distribution as when talking to B. So A cannot authenticate B, and W learns the key and the
payload. Authenticity requires B to hold something W lacks: a long-term secret, i.e. a key again,
or weights W does not have.

*Consequence.* "Keyless" secrecy holds only against **passive** wardens, or against active wardens
that cannot impersonate a partner. The key reappears as soon as the monitor is allowed to talk.
VZ26 make the same point by suggesting active probing: the monitor itself engages B in the covert
KE and checks key agreement.

---------------------------------------------------------------------------------------------------

## 6. Summary: what is necessary for which goal

| Goal \ warden | passive, *weaker* W (lacks Wt or 𝒮) | passive, *equally informed* W | active, equally informed W |
|---|---|---|---|
| Coordination | P (or Wt-derived focal point) | P (or focal point) | P |
| Undetectability | P + H (+ uniform payload or KE) | P + R + H + PR-KE (Thm 2) | open / fragile (Prop 7) |
| Secrecy | focal point or Wt idiosyncrasy can suffice (Cor 1c) | **interaction + ρ + PR-KE; no one-way scheme (Cor 1a); tacit codes give zero advantage (Cor 1b)** | impossible without asymmetric knowledge, e.g. a key (Prop 8) |

**Answer to the research question.**
*Yes*: agents can communicate secretly and undetectably without ever having shared a secret key,
provided that (1) they already share common knowledge of a (possibly public) protocol, (2) both of
them can speak (interaction), (3) honest messages have entropy and public randomness is available,
and (4) the monitor is passive.
*No*, in three precise senses:

- a "secret language" reached by tacit coordination alone (focal points, shared priors) gives
  zero secrecy against a monitor with the same knowledge and model (Cor 1b);
- an undetectable protocol cannot be discovered in-band, so the protocol must be common knowledge
  beforehand (Prop 5);
- against an active monitor that can impersonate a partner, secrecy requires asymmetric
  knowledge, i.e. a key in some form (Prop 8).

**Design implications for overseers.** (i) Give monitors the same weights and context as the
agents (this defeats Cor 1b/1c channels). (ii) Transcript auditing cannot defeat Theorem 2 channels
in principle. Use active measures instead: paraphrasing/re-sampling (Prop 7), impersonation
probing (Prop 8), verifiable sampling, or removing the agents' private randomness, e.g. by having
the monitor supply the sampling coins. If the agents' sampling coins are in 𝒦_W, Lemma 1 applies
to every message and no secrecy is possible at all.
