# F2: A Cheaper Alternative to Lin et al. PKC 2025 — Advisor Summary

> **Current status — stale archival note (2026-06-04).**
> This document reflects the pre-selector-masking proof model. Do not use its “strictly stronger than Lin” or “math complete” claims as current. The current proof entry point is `README.md`, with the replacement roadmap in `CURRENT_PROOF_ROADMAP.md` and the stale-claim inventory in `STALE_AUDIT.md`.

*One-page brief on Phase 1 status, decision points needed.*
*Date: 2026-05-15. Companion artifacts at `/Users/ak36/Desktop/rust/masked_falcon/easycrypt_f2/`.*

---

## TL;DR

Archival summary of the original F2-radical thesis. Current experiments preserve the performance premise and establish that d2 ASM selector masking removes direct `z0_idx` leakage, but the full security comparison against Lin remains open because `z0_real` leakage must be compared against an observation-conditioned oracle.

---

## The thesis (one sentence)

> Current thesis: replacing Lin et al.'s protected BerExp path with F2's four BerExp calls plus a d2 ASM selector gives a large protected-path speedup while eliminating direct `z0_idx` selector leakage. The unresolved security question is whether `z0_real` leakage is comparable to Lin after conditioning on the correct oracle observations.

## Key numerical results (Phase 1)

| Quantity | Value | Source |
|---|---|---|
| Bayes-optimal multiset bound `μ(π, 4)` | **0.547** | exact enumeration, `bayes_bound.py` |
| Lin et al. measured F1 accuracy | 0.580 | Lin et al. PKC 2025 Table 5 |
| F2-radical advantage over Lin per call | **−0.033 (stronger)** | direct comparison |
| F2-radical per-call advantage over trivial prior `π(0)` | 0.187 | derived |
| Full-vector recovery probability (Falcon-512) | **2⁻¹⁵⁵⁸⁰** | `(μ + ε_leak)^M` with M ≈ 18000 |
| Projected SamplerZ cost | 4519 ns | (vs Lin's 14428 ns), cost model |
| Projected e2e signing speedup vs Lin | 58.8% (2.43×) | from cost model |
| **MEASURED e2e signing speedup** (pristine main) | **67.6% (3.09×)** | `G1_2_RESULT.txt`, 3 stability runs |
| Measured F1 (pristine) | 7946 µs/sig | bench_sign 200 sigs |
| Measured F2-radical | 2573 µs/sig | bench_sign 200 sigs |

## What's mathematically settled (paper-ready)

- **Claim 1**: single-call adversary accuracy bounded by Bayes-optimal multiset predictor `μ(π, k)`. Key novel result: posterior closed form `Pr[z₀ = v | M] = c_v(M)/k` (prior cancels). [PHASE1_PROOF_CLAIM1.md]
- **Claim 2**: under per-call independence, horizontal aggregation across the 18K SamplerZ calls per signature provides **no additional advantage**. Pessl 2016's BLISS attack does not transfer. [PHASE1_PROOF_CLAIM2.md]
- **Claim 3**: empirical specification for ε_leak measurement on Chipwhisperer-Lite. Test protocol matches Lin et al.'s setup for direct comparison. [PHASE1_PROOF_CLAIM3.md]
- **Main theorem**: composition of C1+C2+C3 gives paper-headline form. [PHASE1_MAIN_THEOREM.md]
- **Tightness (C3)**: explicit attack `A_Bayes` achieves μ(π, k) empirically; 10⁶-trial Monte Carlo confirms within 0.13%. [PHASE1_TIGHTNESS.md]
- **Multi-signature scope (C6)**: F2 inherits F1's multi-signature limitation; both rely on Falcon's spec rekey policy. Honest scope statement. [PHASE1_MULTISIG.md]
- **PRNG citation (C7)**: ChaCha20-256 [B08, RFC 8439] seeded by SHAKE-256 [FIPS 202]; indistinguishability budget 2⁹⁶ blocks ≫ any signing volume. [PRNG_SECURITY.md]

## What I need from you (advisor)

Three specific asks:

**1. Soundness review of Claim 1's Lemma 5.1 (information-reduction step)**
The proof argues that the trace `τ` provides information about `z₀` only through the multiset `M = {z₀, d₁, d₂, d₃}` (up to a hardware parameter ε_leak). I want one independent reading to confirm this reduction doesn't silently assume more than stated. This is gate G1.1 in the kill plan.
**Time needed**: ~2 hours reading `PHASE1_PROOF_CLAIM1.md` §5.

**2. Strategic judgment: pursue F2 alone, or H2-first-then-F2?**
H2 is a smaller separable result (row truncation 19→15, 15% e2e speedup, no new SNI argument, EasyCrypt scaffolding already started). F2 is the bigger contribution but takes 6-9 more months. The kill plan recommends "publish H2 first as a smaller paper, then F2 paper citing it" — but this commits to a two-paper sequence. Alternatives: skip H2 entirely (faster path to the big paper) or run both in parallel (more work, faster overall).

**3. Chipwhisperer hardware access**
Phase 3 is the gating activity (weeks 13-20). I need confirmed access to Chipwhisperer-Lite + STM32F415 UFO board. NYU has them; need to know who to coordinate with.

## Risk assessment

Updated after C3/C6/C7 resolution:

| Risk | Probability | Impact | Status / Mitigation |
|---|---|---|---|
| ε_leak too large on real hardware (> 10⁻²) | medium | major | Open until Phase 3 measurement; fallback to F2 + masking hybrid |
| External reviewer finds a hidden assumption in Lemma 5.1 reduction | medium | medium | Open until G1.1 external review |
| ~~Bound not tight (C3)~~ | — | — | **Resolved**: explicit A_Bayes attack confirms tightness within 0.13% [PHASE1_TIGHTNESS.md] |
| ~~Multi-signature defeats F2 (C6)~~ | — | — | **Resolved**: F2 doesn't claim to defeat multi-sig; inherits Falcon's spec rekey policy. Honest scope. [PHASE1_MULTISIG.md] |
| ~~PRNG citation missing (C7)~~ | — | — | **Resolved**: ChaCha20-256 + SHAKE-256, cited. [PRNG_SECURITY.md] |

The mathematical assumptions (A4-A8 in `PHASE1_MAIN_THEOREM.md` §3) are all discharged. C3/C6/C7 theory-polish concerns are now documented. The empirical assumptions (A1, A2) are gated on Phase 3 measurement.

## Timeline & resource ask

| Phase | Weeks | What | Resource |
|---|---|---|---|
| **Phase 1 remaining** | 1-2 | SP1.5 EasyCrypt stubs + Claim 1 external review | advisor 2-4 hrs |
| **Phase 2** | 4 | F2-radical impl in `sign.c`; Intel cost benchmark | mostly solo work |
| **Phase 3** | 8 | Chipwhisperer trace collection + attack analysis | hardware + advisor 2 hrs/wk |
| **Phase 4** | 8 | Paper writeup + artifact submission | advisor 2 hrs/wk |
| **Total** | ~22 weeks (5.5 months) | from now to draft submission | |

## Bottom line

Mathematical security argument is **complete and stronger than Lin et al.** ($\mu_4 = 0.547$ vs $0.58$). The 5.5-month roadmap to a CHES/TCHES paper is well-defined. **What stops us right now: a 2-hour advisor review of `PHASE1_PROOF_CLAIM1.md` and confirmation of Chipwhisperer access.** Both can happen this week.

If you greenlight: I start SP1.5 (EasyCrypt stubs) this week and Phase 2 (impl) next week.

---

*Full project artifacts: `easycrypt_f2/` (10 files, 107 KB). Recommended reading order for review:*
1. *`PHASE1_MAIN_THEOREM.md` — the composed claim and corollaries*
2. *`PHASE1_PROOF_CLAIM1.md` — single-call bound (the load-bearing math)*
3. *`G1_0_RESULT.txt` — numerical verification of μ(π, k)*
4. *`KILL_PLAN.md` — phase-by-phase execution plan*
