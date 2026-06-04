# Phase 1, Claim 3: Leakage-Invariance Specification (Empirical Bridge to Phase 3)

> **Current status — stale measurement-target note (2026-06-04).**
> The original `epsilon_leak` permutation-invariance test is insufficient as the sole empirical gate. Current experiments require separate gates for selector leakage, accept/event conditioning, selected-value opening, and excess `z0_real` leakage over an explicit oracle.

**Status**: SP1.3 deliverable (week 6 of Phase 1). Specification document, not a proof.
**Prerequisites**: `PHASE1_PROOF_CLAIM1.md` (defines ε_leak; §7 lists hardware sources), `PHASE1_PROOF_CLAIM2.md` (defines per-call independence; §6 lists implementation requirements), `KILL_PLAN_SECURITY.md` §SP1.3.
**What this document does**: defines `ε_leak` rigorously, specifies the empirical test protocol that measures it on Chipwhisperer-Lite, and sets pass/fail thresholds derived from Claims 1 and 2.

---

## 1. Why Claim 3 is different

The old Claims 1 and 2 were mathematical theorems whose statements bottomed out at one unmeasured parameter: `ε_leak`. That is no longer enough. The active measurement plan needs separate empirical obligations for selector leakage, oracle-conditioned accept/event leakage, selected-value opening, and excess `z0_real` leakage.

The old math said:

```
Adv_HZ  ≤  μ(π, k)  -  π(0)  +  ε_leak
        =  0.187          +  ε_leak     (for Falcon-512, k=4)
```

But `ε_leak` is **not** a math object — it's a property of the implementation + hardware. SP1.3's job is therefore not to prove a theorem but to:

1. Give a rigorous mathematical *definition* of ε_leak
2. Design an empirical *protocol* that measures it
3. Set pass/fail *thresholds* derived from the security claim
4. List the *implementation guidelines* that minimize it
5. Define the *fallback* if measurement shows ε_leak too large

This document is the bridge between Phase 1 (math) and Phase 3 (hardware).

---

## 2. The ε_leak hypothesis — rigorous definition

**Definition 3 (recap from Claim 1 §3)**.
For a leakage function `L`, define:

```
ε_leak  :=  sup_{X, Y :  M(X) = M(Y)}  Δ_TV(  L_σ(X),  L_σ(Y)  )
```

where `Δ_TV` is total variation distance between distributions over traces (with σ marginalized as uniform over S_k), and `M(X), M(Y)` are the multisets of the candidate tuples.

**Equivalent operational definition**:
ε_leak is the maximum statistical distance between the distributions of leakage traces from two BerExp invocations whose candidate multisets are identical but whose orderings differ. If `ε_leak = 0`, the hardware reveals nothing about the ordering — exactly what F2 needs. If `ε_leak > 0`, the leakage contains a fraction `ε_leak` of "ordering information" that the adversary can exploit.

### 2.1 What is being conditioned on

Crucially, ε_leak is defined for a *single call* in isolation. The horizontal version (multi-call) is bounded by `M · ε_leak` (Claim 2's residual term).

The cross-call leakage decomposes:
- ε_leak^single: per-call invariance violation (this is what we measure)
- ε_horiz^cross-call: cross-call dependencies that break Claim 2's independence assumption

Both must be bounded; they are measured by different tests (§4 and §5 respectively).

---

## 3. Pass/fail thresholds (derived from Claims 1 + 2)

From the composition:
```
Adv_HZ  ≤  μ(π, 4) - π(0)  +  ε_leak  =  0.187  +  ε_leak
```

For the security claim "F2 is at least as secure as Lin et al.'s 0.58":

```
0.547  +  ε_leak  ≤  0.58
ε_leak  ≤  0.033
```

Under the old multiset-only theorem, any `ε_leak < 0.033` would have made F2(k=4) match Lin's bound. This is archival. The current pass/fail rule must compare measured leakage against the observation-conditioned oracle and Lin baseline. The old target table was:

| Target | ε_leak | What it buys | Verdict |
|---|---|---|---|
| **A — Ideal** | < 5 × 10⁻⁶ | F2 advantage `0.187 + 5e-6 ≈ 0.187`; full-vector recovery 2⁻¹⁵⁵⁸⁰ | publish as "strictly stronger and 58.8% faster" |
| **B — Acceptable** | < 10⁻⁴ | F2 advantage 0.187; full-vector 2⁻¹⁵⁵⁰⁰ | publish as "equivalent or stronger, 58.8% faster" |
| **C — Marginal** | < 10⁻³ | F2 advantage 0.188; F2 barely matches Lin | publish with caveat, less compelling |
| **D — Failing** | < 10⁻² | F2 advantage 0.197; F2 worse than Lin on per-call | kill OR fall back to F2+masking hybrid |
| **F — Catastrophic** | ≥ 10⁻¹ | F2 advantage > 0.28; key recovery feasible | kill F2-radical |

**Decision tree at G1.3**:
- ε_leak ≤ Target A → proceed to Phase 4 (paper).
- Target A < ε_leak ≤ Target B → proceed; weaken paper claim from "strictly stronger" to "equivalent or stronger".
- Target B < ε_leak ≤ Target C → proceed with explicit hardware-conditioned claim.
- Target C < ε_leak ≤ Target D → trigger backup plan: F2 + masking hybrid (provable d-SNI floor).
- ε_leak > Target D → kill F2-radical; retry F2-conservative or alternative countermeasure family.

---

## 4. Test Protocol — measuring ε_leak (single-call)

### 4.1 Test environment (matches Lin et al. for direct comparison)

| Component | Spec |
|---|---|
| Target board | STM32F415 UFO board (ARM Cortex-M4 @ 32 MHz, no speculation, no L2 cache) |
| Oscilloscope | Chipwhisperer-Lite Capture (10-bit ADC, max 105 MS/s) |
| Trace alignment | Hardware trigger from target GPIO; static alignment in software |
| Acquisition | 10,000 profiling traces + 5,767 attack traces (Lin et al.'s exact numbers) |
| Power | USB-isolated supply via decoupling capacitors |
| EM probe | Optional, RF-1 near-field probe for cross-validation |

This is **identical** to Lin et al. Section 5.3 setup. Direct side-by-side comparison feasible.

### 4.2 Trace collection — the invariance dataset

**Goal**: for the F2-radical BerExp gadget with k=4, collect trace pairs where the candidate multiset is identical but the ordering differs.

**Procedure**:
1. Fix a "test multiset" M_test = {a, b, c, d} with 4 distinct values, e.g., {0, 1, 2, 3} (the most common Falcon candidates).
2. For each of the 4! = 24 orderings (a, b, c, d), (a, b, d, c), ..., collect N_trace traces of F2-BerExp running on that exact ordering.
3. Total trace count: 24 × N_trace. For N_trace = 1000, that's 24,000 traces.

This data answers: are L(σ_a, ...) and L(σ_b, ...) distinguishable?

### 4.3 TVLA test for permutation invariance

For each ordering pair (σ_a, σ_b), compute Welch's t-test statistic at each sample point in the trace:

```
t(s)  =  (mean(L_σ_a)[s] - mean(L_σ_b)[s])  /  sqrt(var_a[s]/N_a + var_b[s]/N_b)
```

**Threshold**: per the TVLA standard, |t(s)| > 4.5 at any sample s means the two orderings are statistically distinguishable.

**Specification**:
- TVLA "passes" if max_s |t(s)| < 4.5 across all 24 × 23 / 2 = 276 ordering pairs.
- Conservative threshold: 3.0 (matches Lin et al.'s methodology).

**From t-statistic to ε_leak bound**: by Pinsker's inequality and Welch's t-test asymptotics, max-t < 4.5 corresponds to ε_leak ≲ 10⁻⁴ (Target B). Max-t < 3.0 corresponds to ε_leak ≲ 10⁻⁶ (better than Target A).

So the test is calibrated to detect ε_leak down to 10⁻⁶ with N_trace = 1000.

### 4.4 Template attack on single call (calibrates measured ε_leak)

Direct measurement of attacker accuracy under F2-radical:

1. **Profiling phase**: from 10,000 trace tuples (trace, ground-truth z₀), build a 19-class Gaussian template attack.
2. **Attack phase**: run 5,767 attack traces; classify each.
3. **Per-leakage-source accuracy**: report classification accuracy on each of the 5 leakage sources from Lin et al. Table 5 (BaseSampler, sign flip of z̃, computation of x̃, BerExp, return).

**Pass conditions**:
- F2(k=4) accuracy ≤ 0.547 + Target_threshold per leakage source.
- Specifically, accuracy ≤ 0.55 → Target A; ≤ 0.59 → Target B; ≤ 0.65 → Target C.

**Comparison to Lin et al.**: their reported accuracies are 57%, 50%, 51%, 54%, 58% (half-Gaussian leakage). We compare F2 to each at the same threshold.

### 4.5 Cross-call independence test (Definitions 6-7 from Claim 2)

This is a different test, measuring `ε_horiz^cross-call` rather than `ε_leak^single`.

**Procedure**:
1. Collect 1000 full Falcon-512 signatures, each with ~18000 SamplerZ calls = 18M trace tuples.
2. For each pair of call indices (i, j) within a signature (sampled randomly), compute the autocorrelation of trace features between calls i and j as a function of |j − i|.
3. **Pass condition**: autocorrelation falls off to noise level (<0.01) within |j−i| ≤ 10 calls.

If autocorrelation is significant across many calls, per-call independence (Definition 6-7) is broken at the hardware level. Mitigations from Claim 2 §6 must be re-applied or strengthened.

---

## 5. Implementation requirements (refinement of Claim 2 §6)

Each requirement gets a specific verification test. These are the constraints F2-radical implementation must satisfy to meet ε_leak target.

### IR1 — Constant-time gadget (per-call invariance)

**Requirement**: F2-BerExp's control flow and memory access pattern depend only on σ (the random permutation), not on (z₀, dummies).

**Verification**: static analysis with the LLVM `valgrind --tool=ct-check` (or equivalent) on the compiled binary. Should report zero data-dependent branches.

### IR2 — PRNG re-seed strategy (per-call independence)

**Requirement**: σ⁽ⁱ⁾ for each call is generated from entropy independent of prior calls.

**Verification**: instrument the PRNG to log seed materials; check independence statistically (Kolmogorov-Smirnov on consecutive seeds).

**Cost target**: < 100 ns/call (chosen at PRNG re-seed in Claim 2 §6.1 Option A).

### IR3 — Cache flush between calls

**Requirement**: between BerExp calls, all data caches are flushed.

**Verification**: cache-miss profiler (e.g., on STM32 use the DWT counters) shows constant miss rate per call regardless of call sequence.

**Cost target**: < 50 ns/call (negligible vs BerExp).

### IR4 — Register zeroing

**Requirement**: callee-saved registers are zeroed at BerExp call exit.

**Verification**: code review + compiler output inspection.

### IR5 — Branch predictor neutrality

**Requirement**: no z₀-dependent branches in F2-BerExp.

**Verification**: this follows from IR1 (constant-time) on Cortex-M4 (no speculative execution). Trivially satisfied on the test target.

### IR6 — Power supply decoupling

**Requirement**: power rails have decoupling capacitors as per Chipwhisperer-Lite reference design.

**Verification**: hardware inspection; no test in software.

### IR7 — Memory layout (cache associativity neutrality)

**Requirement**: F2-BerExp's working data fits in a single cache line, or in multiple lines with no associative conflicts.

**Verification**: linker map analysis + cache-line layout audit.

---

## 6. Statistical methodology details

### 6.1 Number of profiling traces

Lin et al. use 10,000 profiling traces. For F2(k=4), we use the same to enable direct comparison. The classification accuracy at 10K traces vs 100K traces is reported in their Figs 9-10 — F2 should report the same curve for consistency.

### 6.2 Principal Component Analysis

Lin et al. use the first 65 principal components. F2 uses the same. PCA is computed from the profiling traces; the same components project the attack traces.

### 6.3 Cross-validation

To prevent over-fitting on profiling traces:
- Hold out 10% of profiling traces as a validation set.
- Train templates on the remaining 90%.
- Compare reported accuracy on the validation set vs the held-out attack traces.
- Significant gap → over-fitting → re-collect profiling traces.

### 6.4 Confidence intervals

For each reported accuracy A on N_attack = 5,767 traces, the 95% CI is approximately A ± 1.96 × sqrt(A·(1-A)/N_attack). For A = 0.55, CI is ± 0.013, so reported accuracy is precise to about 1.3 percentage points.

**Specification**: report all accuracy claims with their 95% CIs.

---

## 7. Fallback plans

If the empirical tests show ε_leak > Target threshold:

### Backup 1: Mask + shuffle hybrid

If ε_leak ∈ (Target B, Target D):
- Add first-order Boolean masking on top of F2-radical's shuffling.
- Each BerExp call is now (masked + shuffled).
- Provable: d-SNI at order d=1 floor, regardless of ε_leak measurement.
- Cost: ~2× per-call vs raw F2. Combined SamplerZ ~9000 ns (still beats Lin's 14428).
- Paper claim: "F2 with masked belt-and-braces; secure under any ε_leak ≤ 10⁻²".

### Backup 2: K-call refresh

If cross-call independence (Test §4.5) fails:
- Insert a refresh gadget every K = 100 calls.
- Refresh costs ~100 ns; total per-signature ~180 ns (negligible).
- Bounds the cross-call correlation window.

### Backup 3: Restrict to higher k

If μ(π, 4) + ε_leak doesn't pass:
- Bump to k = 8: μ(π, 8) = 0.472. Budget for ε_leak grows to 0.108 (well above any measurable value).
- Cost: SamplerZ rises to ~7211 ns; e2e speedup drops to 42.9% (still publishable).

### Backup 4: Negative result paper

If all backups fail:
- Publish as "single-trace shuffling for Falcon: a feasibility study and its limits."
- Cites Claims 1 + 2 as the theoretical contribution.
- Reports empirical ε_leak as the measured limit.
- Less ambitious paper but salvages 9 months of work.

---

## 8. Phase 3 work plan (downstream of this spec)

The Phase 3 team executes this spec in 8 weeks (per `KILL_PLAN.md`):

| Week | Activity |
|---|---|
| 13 | Hardware setup: STM32F415 UFO + Chipwhisperer; bring-up of unprotected SamplerZ |
| 14 | Implement IR1-IR7 in `sign_f2.c`; build for STM32 |
| 15 | TVLA permutation-invariance dataset collection (24K traces) |
| 16 | TVLA analysis; if pass → continue, else iterate on IR1-IR7 |
| 17 | Template attack profiling (10K traces) |
| 18 | **KILLER GATE G3**: template attack on F2(k=4); report accuracy table |
| 19 | Cross-call independence test (1000 full signatures) |
| 20 | Write up Phase 3 report; decide on backup plan if needed |

---

## 9. Documentation deliverables (Phase 3 → Phase 4)

By end of Phase 3, the following are required for the paper:

1. **Figure equivalent to Lin et al. Fig 7-8**: SNR curves on F2(k=4).
2. **Figure equivalent to Lin et al. Fig 9-10**: template-attack accuracy curves.
3. **Table equivalent to Lin et al. Table 5**: 5-leakage-source accuracy comparison.
4. **Table of measured ε_leak per leakage source**: this is new (not in Lin et al.).
5. **Cross-call independence plot**: autocorrelation vs |j-i|.
6. **Implementation cost breakdown**: cycles per SamplerZ call on STM32F415.
7. **Full E2E timing**: cycles per Falcon-512 signature.

---

## 10. Loose ends

1. **Pinsker calibration in §4.3** is informal. Tightening: use the exact KL-distance formula for Gaussian distributions, or the explicit bound from Mangard-Oswald-Popp 2007 §5.2.

2. **The 24 orderings test in §4.2** ignores higher-multiplicity multisets. Falcon's multisets with k=4 often have repeats: P({0,0,0,0}) ≈ 0.017, P({0,0,0,*}) ≈ 0.12, etc. These multisets have fewer distinct orderings (24, 6, 4, ...). Should the test cover them too? Probably yes for completeness; adds ~5K traces.

3. **PCA component count (65)** is borrowed from Lin et al. without re-deriving. For F2, the optimal component count might differ. Worth pilot-testing in Phase 3 week 13.

4. **Cross-call test** (§4.5) measures autocorrelation but not joint mutual information. The stronger test uses Hilbert-Schmidt independence criterion (HSIC), but it's computationally expensive on 18M traces. Autocorrelation is the pragmatic compromise.

5. **EM probe addition** (§4.1) is listed as optional. If Chipwhisperer's power-channel SNR is too low for clean templates, EM is the fallback. Cost: ~$200 probe, no methodology change.

---

## 11. Connection to SP1.4

With Claims 1, 2, and 3's specification complete, SP1.4 composes them into the main theorem:

```
Theorem (paper main).
Under per-call independence (verified empirically in Phase 3 via §4.5) and
ε_leak ≤ {measured value from §4.3-4.4}, for any PPT adversary against
M = 18000 SamplerZ calls in one Falcon-512 signature:

  Adv_HZ  ≤  μ(π, 4)  -  π(0)  +  ε_leak  =  0.187  +  ε_leak

  Pr[full-vector recovery]  ≤  (μ(π, 4) + ε_leak)^M
```

The numbers are filled in once Phase 3 measurements complete.

---

*Author: F2 project, Phase 1 SP1.3 specification. Last updated: 2026-05-15.*
*Next deliverable: PHASE1_MAIN_THEOREM.md (week 7 — composition).*
