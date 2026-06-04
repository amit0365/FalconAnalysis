# Phase 0 Literature Review: F2 Novelty Assessment

> **Current status — partially stale note (2026-06-04).**
> The novelty survey remains useful background, but the claimed security framing is stale where it relies on `mu(pi,4)` as the full implementation bound. Current framing: d2 ASM selector masking fixes direct `z0_idx` leakage; remaining `z0_real` leakage must be compared against an observation-conditioned oracle and Lin baseline.

**Question**: Is "shuffling-with-dummies applied at single-sample granularity to Falcon's BerExp" novel? If so, what's the closest prior work?

**Verdict**: PROCEED to Phase 1. F2 at single-sample granularity is novel. Pessl 2016's attack does not directly preempt it, but its horizontal-aggregation variant must be defeated in Phase 1.

---

## 1. Bottom line (initial P0 memo)

Applying shuffling-with-dummies to a single SamplerZ / BerExp invocation in Falcon is, to the best of public knowledge, novel. Confidence: medium-high. Shuffling has been proposed for lattice samplers before, but always in the form of **permuting the order of the N polynomial-coefficient samples** drawn during one signature (Roy et al. 2014; Pessl 2016; Kyber/Dilithium variants). No published work inserts (k-1) dummy BerExp / discrete-Gaussian draws around a single real one and shuffles inside that micro-batch. Lin et al. PKC 2025 (the target paper we beat) explicitly chooses full enumeration (19/19) and does not consider a dummy-shuffle alternative.

**Main caveat**: Pessl 2016 broke polynomial-level shuffling for BLISS in 7,000 traces using a "histogram-based unshuffling" via an n×n Bayesian likelihood matrix. F2's security proof must explain why his technique does not transfer to single-sample dummy-shuffling.

---

## 2. Direct prior work

- **Peter Pessl, "Analyzing the Shuffling Side-Channel Countermeasure for Lattice-Based Signatures," Indocrypt 2016 (eprint 2017/033).** Attacks the Roy et al. shuffling countermeasure for BLISS's Gaussian sampler. The shuffled object is the full polynomial of N coefficient-samples, not a single sample. Profiled SCA recovers the key in ~7,000 signatures; "shuffle + convolution applied twice" still falls to ~285,000 traces. *Does not preempt our work* — F2 shuffles dummies inside one z₀ draw, not a polynomial — but its unshuffling-by-statistics technique is a serious threat we must analyze.

- **Sujoy Sinha Roy, Oscar Reparaz, Frederik Vercauteren, Ingrid Verbauwhede, "Compact and Side Channel Secure Discrete Gaussian Sampling," IACR eprint 2014/591.** Originated the "shuffle the sampled polynomial" countermeasure for BLISS-style schemes, the very proposal Pessl broke. *Does not preempt* — same polynomial-level granularity, different scheme (BLISS CDT sampler, not Falcon BerExp).

- **Lin, Zhang, Yu, Wang, "Thorough Power Analysis on Falcon Gaussian Samplers and Practical Countermeasure," PKC 2025 (eprint 2025/351).** Algorithm 6 ("Protected SamplerZ") iterates all 19 z₀ values for every call; ~6× SamplerZ cost, ~3.5× full-signing. *Defines the baseline we beat* — explicitly does not consider dummy-shuffling.

- **Beizhan, Lin, et al. (arXiv 2407.02452), "A Hardware-Friendly Shuffling Countermeasure Against Side-Channel Attacks for Kyber," 2024.** Fisher-Yates over Kyber polynomial coefficients in hardware. Same "permute the N samples" pattern. *Does not preempt.*

---

## 3. Adjacent prior work (intro citations)

- Veyrat-Charvillon, Medwed, Kerckhof, Standaert, "Shuffling against Side-Channel Attacks: A Comprehensive Study with Cautionary Note," ASIACRYPT 2012 — canonical foundational paper for shuffling-as-countermeasure theory and the 1/k accuracy intuition; warns of "indirect leakages" in shuffled implementations.
- Groot Bruinderink, Hülsing, Lange, Yarom, "Flush, Gauss, and Reload," CHES 2016 — first SCA on a lattice Gaussian sampler.
- Migliore, Gérard, Tibouchi, Fouque, "Masking Dilithium," ACNS 2019 (eprint 2019/394) — masking (not shuffling) for Dilithium.
- Karabulut, Aysu, "FALCON Down," DAC 2021 — first SCA on Falcon.
- Guerreau, Martinelli, Ricosset, Rossi, "The Hidden Parallelepiped Is Back Again," TCHES 2022(3) — Falcon base-sampler SPA.
- Zhang, Lin, Yu, Wang, "Improved Power Analysis Attacks on Falcon," EUROCRYPT 2023 (eprint 2023/224).
- Howe, Prest, Ricosset, Rossi, "Isochronous Gaussian Sampling," PQCrypto 2020 — Falcon's constant-time SamplerZ baseline.
- Berthet, Tavernier, Danger, Sauvage, "Masked Computation of the Floor Function and Its Application to FALCON Signature," CiC 2024 (eprint 2024/709).
- Chen, Chen TCHES 2024(2) "Masking Floating-Point of Falcon."
- Roy, Basso, "When Masking Multiplication Isn't Enough," TCHES 2024 — motivates lightweight alternatives.
- Azouaoui, Bronchain, Grosso, Papagiannopoulos, Standaert, "Bitslice Masking and Improved Shuffling," TCHES 2022(2) — most recent shuffling-theory framework.

---

## 4. Theoretical gap — VERIFIED by full-text PDF reading (2026-05-18)

The standard "shuffling reduces single-trace accuracy to 1/k" intuition in symmetric-crypto SCA literature **explicitly bakes uniform-secret assumption into its foundational equations**.

**Smoking gun — Azouaoui, Bronchain, Grosso, Papagiannopoulos, Standaert. "Bitslice Masking and Improved Shuffling," TCHES 2022(2) [eprint 2021/951], p. 5, Equation (4)**:

> *"Thanks to this PDF, the conditional probability of a sensitive variable Y given the leakage, denoted as Pr[Y = y | L = l] := p(y|l), can be computed via Bayes. **Assuming that Y is uniformly distributed (which is the case for the cryptographic secrets we aim to recover)**, it is expressed as: p(y|l) = f(l|y) / Σ_y* f(l|y*)."*

The uniform-Y assumption is in the Bayes equation itself, not relegated to a footnote.

**Veyrat-Charvillon, Medwed, Kerckhof, Standaert. "Shuffling Against Side-Channel Attacks: A Comprehensive Study with Cautionary Note," ASIACRYPT 2012, §1**:

> *"As a result and for the first time, we obtain **lower bounds for the data complexity** of standard side-channel attacks against shuffled implementations."*

Target: AES (uniform key bytes). Object: data-complexity bounds (number of traces), not per-trace accuracy.

For Falcon's z₀, the distribution is sharply non-uniform: P(z₀=0) ≈ 0.36, P(z₀=18) ≈ 2⁻⁷². An attacker who always guesses 0 already achieves 36% accuracy — *above* the naive 1/k = 25% bound for k=4. Azouaoui's framework cannot apply because its eq. (4) assumes uniform Y.

**The right statement is the Bayes-optimal multiset-predictor accuracy `μ(π, k) = E_M[c_{g*(M)}(M) / k]`**, derived rigorously in `PHASE1_PROOF_CLAIM1.md`, evaluated numerically to `μ(π, 4) = 0.547` in `bayes_bound.py` / `G1_0_RESULT.txt`.

**F2's strongest novelty hook**: the first closed-form, defender-side, Bayes-optimal per-trace accuracy bound for shuffling-with-dummies under non-uniform secret prior — a regime explicitly excluded by Azouaoui et al. TCHES 2022(2) eq. (4).

---

## 5. Pessl/Lin/Mitaka triangulation (P0 follow-up)

### Q1: Does Pessl 2016 preempt F2? → NO (closest prior; verified by full-text reading 2026-05-18)

Pessl's attack is structurally a **population-of-N un-shuffler** that exploits BLISS's polynomial-level shuffle over N=512 coefficients per signature. The attack constructs an n×n likelihood matrix `L ∈ (n × n), with Lᵢⱼ = Xsc(zᵢ − yⱼ)` and applies Bayesian normalization across rows and columns to re-assign each leaked sample to its index. With only k=4 shuffled candidates per SamplerZ invocation, there is no n×n matrix to build — the matching is trivial within a call.

**Closest prior — Pessl §5.5 "Merging equal y"** (the technique most resembling our Lemma 5.2):

> *"We use this observation as follows. We create a vector u which contains the unique elements of y₁. We then compute P(z_i ∼ u_j | u). For that, we use the number of times each u_j appears in u as prior probabilities (instead of the uniform distribution)."*

So Pessl DOES use multiplicity-weighted (non-uniform) priors — BUT:
- As an **attacker's likelihood-matrix optimization** for matching n=512 shuffled BLISS coefficients
- NOT as a **defender-side closed-form accuracy bound**
- Different math object: attacker's posterior `P(z_i ∼ u_j | u)` for matching; our `P(real = v | M) = c_v(M)/k` is the defender's information-theoretic bound
- Different problem (polynomial unshuffling vs single-call F2 multiset)

Our work is essentially the **dual perspective** (defender-side, single-sample granularity) of Pessl §5.5's idea (attacker-side, polynomial granularity).

The relevant remaining question is whether an attacker can do horizontal aggregation across the ~18,000 SamplerZ calls per Falcon-512 signature, treating those calls collectively as Pessl's population. **Pessl himself does not evaluate "shuffling within a single sample"** — his scope is single-stage and two-stage polynomial shuffling.

**Verbatim** [Pessl16 §5.2, p.10]: *"Note that all following descriptions are in context of sampling from the 'small' Dσ₀ and thus Algorithm 2, which is called 2048 times during signature generation."*

**Verbatim** [Pessl16 §5.5, p.13]: *"7,000 (46,000) and 46,000 (301,000) signatures, respectively"* for break thresholds.

### Q2: Does Lin et al. mention shuffling? → NO. Zero hits.

A full-text grep of eprint 2025/351 for "shuffl", "dumm", "permut", "random order", "decoy" returns **zero matches**. Sections 6.1-6.2 describe protected SamplerZ purely as exhaustive enumeration. No Conclusion or Future Work section. No justification for enumeration-over-shuffling — alternatives are simply never raised. **F2's novelty hook is intact.**

### Q3: Does Mitaka discuss sampler shuffling? → NO

Zero "shuffl" tokens in the Eurocrypt 2022 paper. The three "permut" hits are about Galois action on keygen candidate-pools (algebraic permutations, not SCA). Mitaka's only sampler-level countermeasure is t-probing masking. Does not cite Pessl 2016.

---

## 6. Updated kill conditions for Phase 1 (from P0 follow-up)

F2's security proof must explicitly establish:

1. **Horizontal-aggregation bound across SamplerZ calls** — defeats Pessl-style across the ~18,000 calls per signature.
2. **Non-uniform-secret SCA bound** — the dummy distribution D must be matched to π (or proof must show mismatched dummies yield ≥ log₂(k) bits of secret-hiding entropy per call).
3. **No "single-trace template" leak that breaks unshuffling within a call** — template attack must produce k truly indistinguishable hypotheses.
4. **Composability with masking-only baseline** — adding F2 on top of t-probing masked SamplerZ preserves t-probing bound.

---

## 7. Recommended novelty framing (one sentence)

> *"We give the first shuffling-with-dummies countermeasure applied at single-sample granularity for Falcon's discrete Gaussian sampler — together with the first formal SCA security bound for shuffling of a non-uniform discrete-Gaussian secret — protecting BerExp against the PKC 2025 leakages at ~58.8% lower overhead than constant-time enumeration, validated on Chipwhisperer-Lite."*

Avoid: "first shuffling for Falcon" (Pessl/Roy occupy this for BLISS; Kyber shuffling exists). Avoid: "first single-trace 1/k bound" (AES literature occupies it).

---

## 8. Open questions P0 couldn't close

Three sources behind paywalls that should be re-read before Phase 1 review (probably available via NYU library):

1. Pessl 2016 (Indocrypt full text) — verify attack requires N ≥ 256 parallel leaks
2. Lin et al. PKC 2025 (eprint full text confirmed in P0 follow-up — zero hits on shuffling)
3. Espitau et al. Mitaka EUROCRYPT 2022 (confirmed — zero hits on shuffling)

If any turn out to preempt our claim, that's the project-kill condition.

---

## 9. Final verdict

**PROCEED-WITH-CAVEAT to Phase 1.**

F2 is clearly novel by the strict reading of the three target papers. However, Pessl's attack would, in principle, transfer to F2 if you can stack horizontally across the ~18,000 SamplerZ calls per Falcon signature. F2's security proof must explicitly defeat a horizontal Pessl-style adversary who treats the union of all SamplerZ-call-internal candidate lists as one big shuffled population. This is the focus of `PHASE1_PROOF_CLAIM2.md` (forthcoming).

---

## Sources

- [Pessl 2016 IACR eprint](https://eprint.iacr.org/2017/033)
- [Lin et al. PKC 2025](https://eprint.iacr.org/2025/351)
- [Roy et al. eprint 2014/591](https://eprint.iacr.org/2014/591)
- [Migliore et al. ACNS 2019](https://eprint.iacr.org/2019/394)
- [Guerreau et al. TCHES 2022](https://eprint.iacr.org/2022/057)
- [Zhang et al. EUROCRYPT 2023](https://eprint.iacr.org/2023/224)
- [Kyber shuffling 2024](https://arxiv.org/abs/2407.02452)
- [Mitaka EUROCRYPT 2022 / NIST PQC 2021 preprint](https://csrc.nist.gov/CSRC/media/Events/third-pqc-standardization-conference/documents/accepted-papers/espitau-mitaka-pqc2021.pdf)
- [Howe-Prest-Ricosset-Rossi PQCrypto 2020](https://link.springer.com/chapter/10.1007/978-3-030-44223-1_4)
- [Azouaoui et al. TCHES 2022(2)](https://tches.iacr.org/index.php/TCHES/article/view/9484)
- [Park-Han ASOC 2020 dummy+shuffle bound](https://www.sciencedirect.com/science/article/pii/S1568494620302921)
- [Veyrat-Charvillon et al. ASIACRYPT 2012](https://link.springer.com/chapter/10.1007/978-3-642-34961-4_44)

---

*Last updated: 2026-05-15. Synthesized from two P0 research-agent passes.*
