# F2 Project Kill Plan

> **Current status — stale archival note (2026-06-04).**
> This plan predates the d2 ASM selector work and the oracle-conditioned proof target. Treat the original `Acc(F2_k) <= mu(pi,k)` gate as archival only. Current work should follow `CURRENT_PROOF_ROADMAP.md`.

**Project**: F2 — shuffled-with-dummies countermeasure for Falcon's BerExp, as a cheaper alternative to Lin et al. PKC 2025's constant-time enumeration.
**Status**: Phase 1 in progress.

---

## Thesis (the single claim we're trying to kill)

> Current claim under test: replacing Lin et al.'s protected BerExp path with F2's four BerExp calls plus a d2 ASM selector preserves a large speed advantage and removes direct `z0_idx` selector leakage. Security equivalence to Lin is not yet proven; it depends on `z0_real` leakage relative to an observation-conditioned oracle and Lin baseline.

**Revised again after selector experiments**: the original "1/k = 25%" bound and the later pure-multiset `μ(π,k)` bound are not sufficient as implementation-level security claims. `μ(π,k)` remains a valid pure multiset oracle component, but the current bound must condition on explicit observations `O`.

**F2 design locked**: F2-radical (shuffle at gaussian0_sampler output level; only compute BerExp for k candidates). NOT F2-conservative (which keeps Lin's enumeration and costs more).

---

## Killer experiment (the make-or-break)

**Phase 3, Week 18**: implement F2 with k=4 on Chipwhisperer-Lite + STM32F415, measure template-attack classification accuracy on the same five leakage sources Lin et al. evaluated (Table 5 of the paper). If accuracy ≤ 40% (matched to revised non-uniform-prior math) on all five → thesis confirmed. If accuracy > 50% on any → dummies are detectable → abort or back to Phase 1.

---

## Phase plan

| Phase | Weeks | Deliverables | Gate (= abort condition) |
|---|---|---|---|
| **P0: Setup & lit review** | 1–2 | Annotated bibliography of shuffling in sym crypto; Chipwhisperer hw access; maskVerif / IronMask on toy gadgets; audit of Lin et al.'s 5 leakage sources | **G0**: has someone already applied shuffling to Gaussian samplers? |
| **P1: Formal model & math** | 3–8 (revised from 6) | Adversary spec; dummy distribution definition; security theorem `Acc(F2_k) ≤ μ(π,k)`; EasyCrypt formalization; horizontal-attack bound | **G1**: does `Adv ≤ μ - π(0)` actually hold with realistic dummy distribution? |
| **P2: Prototype impl** | 9–12 | `sign_f2.c` with `BerExp_shuffled(k=4)`; `test_falcon` passes; Intel benchmark; statistical test on 10M signatures | **G2**: SamplerZ < 6000 ns on Intel |
| **P3: Chipwhisperer eval** | 13–20 | Trace collection; SNR plots; template-attack accuracy plots; Table 5 equivalent at k ∈ {2, 4, 8} | **G3 = THE KILLER GATE**: F2(k=4) template accuracy ≤ 40% on every leakage source |
| **P4: Paper & artifact** | 21–28 | Paper draft (CHES 2027 / TCHES); GitHub release; artifact-evaluation submission | **G4**: paper passes internal review |

**Total realistic timeline**: 28 weeks ≈ 7 months. Buffer to 9 months covers one phase needing revision.

---

## Critical path

```
P0 ──► P1 ──► P2 ──► P3 ──► P4
       │        │      │
       │        │      ▼
       │        │   killer exp (G3)
       │        ▼
       │     bit-identity
       ▼     check (G2 cost)
   theorem (G1 math)
```

P1 and P2 can partially overlap (P2 starts at week 7 if P1 math is converging). P3 is the bottleneck — Chipwhisperer trace collection at ≥100K traces is wall-clock-bound.

---

## Risk register

| # | Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|---|
| R1 | Dummies distinguishable on real hardware | **kills project** | medium | P2 builds two dummy-distribution variants; if v1 fails P3, swap to v2 |
| R2 | Shuffle PRNG itself leaks order | high | low | P1 audits randomness source; consider masking the shuffle index too |
| R3 | Horizontal aggregation breaks bound | **major** | medium-high | P1 bounds this analytically; add refresh between SamplerZ invocations if needed |
| R4 | PRNG/shuffle overhead exceeds BerExp savings | medium | medium | P2 profiles early; amortize PRNG calls |
| R5 | Reviewer says "just use Lin et al." | low | high | Frame as "alternative tradeoff curve" |
| R6 | Bit-identity breaks because dummies share state | **kills bit-identity claim** | low | P2 uses strict isolation; verified by 10M-signature statistical test |

---

## Required resources

- 1 PhD student full-time, 7-9 months
- 1 advisor, 2-4 hrs/week
- Chipwhisperer-Lite + STM32F415 UFO board (~$500 one-time)
- 1 workstation for trace analysis
- EasyCrypt 2024.09, maskVerif, Python+scikit-learn

---

## Strategic decisions made

1. **Keep H2 + pivot to F2 sequentially**: publish H2 first as a smaller paper, then F2 paper citing it. Don't run both in parallel.
2. **k = 4 starting point**: μ(π,4) = 0.547 beats Lin's 0.58; cost 58.8% e2e speedup. (See `G1_0_RESULT.txt`.)
3. **Dummy generation strategy = D = π**: matched distribution, run gaussian0_sampler on side buffer. Fall back to replay-buffer if Phase 3 shows distinguishability.
4. **F2-radical** (not F2-conservative): shuffle at gaussian0 output, no inner enumeration.

---

## Backup plan if F2 fails

If G3 fires (dummies distinguishable):
1. Pivot to F4 (per-leakage hardening) — modest e2e win, publishable as "engineering refinement of Lin et al."
2. Combine H2 + Lin as is — publish H2 alone as a smaller paper.
3. Negative result paper — "Why shuffling doesn't transfer from sym crypto to Falcon's sampler" — TCHES sometimes takes these.

---

## Foundational references (from P0 — verified by full-text reading 2026-05-18)

### Target paper
1. **Lin, Zhang, Yu, Wang et al. PKC 2025 (eprint 2025/351)** — the F1 countermeasure we beat

### Shuffling-with-dummies SCA literature (closest priors)
2. **Veyrat-Charvillon, Medwed, Kerckhof, Standaert. ASIACRYPT 2012** — "Shuffling Against Side-Channel Attacks: A Comprehensive Study with Cautionary Note." First formal information-theoretic data-complexity lower bounds for shuffled AES. Assumes uniform secret.
3. **Azouaoui, Bronchain, Grosso, Papagiannopoulos, Standaert. TCHES 2022(2) (eprint 2021/951)** — "Bitslice Masking and Improved Shuffling." Most recent shuffling-theory framework. **Eq. (4) explicitly assumes uniform Y** — provides the verbatim cite anchor for our non-uniform-prior novelty.
4. **Pessl. INDOCRYPT 2016 (eprint 2017/033)** — "Analyzing the Shuffling Side-Channel Countermeasure for Lattice-Based Signatures." Cautionary tale: broke BLISS polynomial-level shuffling. §5.5 "Merging equal y" uses multiplicity-weighted priors — closest mathematical neighbor, but attacker-side / polynomial granularity (dual to our defender-side / single-sample).
5. **Roy, Reparaz, Vercauteren, Verbauwhede. eprint 2014/591** — Originated BLISS sampler shuffling (the proposal Pessl broke).
6. **Park, Han. ASOC 2020** — "Security analysis on dummy based side-channel countermeasures — Case study: AES with dummy and shuffling." AES-specific (uniform).

### Foundational masking / probing model
7. **Migliore, Gérard, Tibouchi, Fouque. ACNS 2019** — Masked Dilithium (different countermeasure family from F2).
8. **Belaïd, Goudarzi, Rivain. EUROCRYPT 2018 (eprint 2018/439)** — "Tight Private Circuits": probing-model masking bounds (not directly shuffling-related, but referenced in the SCA framework).

### Falcon SCA prior work
9. **Bruinderink, Hülsing, Lange, Yarom. CHES 2016** — First SCA on a lattice Gaussian sampler (BLISS via cache attack).
10. **Karabulut, Aysu. DAC 2021** — First Falcon SCA (FFT-side).
11. **Guerreau, Martinelli, Ricosset, Rossi. TCHES 2022(3)** — "The Hidden Parallelepiped Is Back Again": Falcon base-sampler SPA.
12. **Zhang, Lin, Yu, Wang. EUROCRYPT 2023 (eprint 2023/224)** — Improved Falcon SCA, predecessor to Lin25.
13. **Howe, Prest, Ricosset, Rossi. PQCrypto 2020** — Falcon's constant-time SamplerZ baseline.

### Adjacent Falcon designs / countermeasures
14. **Espitau et al. EUROCRYPT 2022** — Mitaka, alternative Falcon design with masking-only SCA story.
15. **Coron, Carrier. 2024 [CC24]** — Masked floating-point for Falcon pre-image computation.

### Classical math foundation (cited but not novel to us)
16. **de Finetti 1937 / Aldous 1985** — Exchangeability theorems; underlying principle for Lemma 5.2.
17. **Bishop, "Pattern Recognition and Machine Learning," 2006, §1.5** — Bayesian decision theory / MAP estimator optimality.

**Note on prior versions of this file**: an earlier draft listed phantom "BBE+18 / BBE+19" citations (Belaïd-Benhamouda-Eraly...). These were hallucinated references that don't match any real paper. They have been removed. The real Belaïd-Goudarzi-Rivain "Tight Private Circuits" 2018 paper is cited as #8.

---

## Phase tracker

```
✅ P0 lit review           — F2 is novel (PHASE0_LITREVIEW.md)
✅ G1.0 numerical bound    — μ(π,4) = 0.547 < Lin's 0.58 (G1_0_RESULT.txt)
✅ SP1.1 Claim 1 proof     — single-call bound (PHASE1_PROOF_CLAIM1.md)
✅ SP1.2 Claim 2 proof     — horizontal independence (PHASE1_PROOF_CLAIM2.md)
✅ SP1.3 Claim 3 spec      — ε_leak empirical test design (PHASE1_PROOF_CLAIM3.md)
✅ SP1.4 composition       — main theorem (PHASE1_MAIN_THEOREM.md) — security argument MATHEMATICALLY COMPLETE
✅ G1.2 impl cost check    — F2-radical built and benched on PRISTINE main (G1_2_RESULT.txt)
                             RESULT: 3.09× faster than F1 as-published (67.6% e2e time reduction)
                             vs projection 2.43× / 58.8% — exceeded by +27% / +8.8 pp
                             Both F1 and F2 pass test_falcon EXIT=0 on pristine main
⏳ G1.1 external review    — schedule for week 4
⏳ G1.3 ε_leak measurement — Phase 3 executes the SP1.3 protocol
⏳ SP1.5 EasyCrypt stubs   — formalization (week 8)
```

---

*Last updated: 2026-05-15.*
