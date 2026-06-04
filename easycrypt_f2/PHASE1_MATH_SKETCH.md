# Phase 1 Math Sketch: F2 (Shuffled-with-Dummies) Falcon BerExp

> **Current status — stale proof-sketch note (2026-06-04).**
> This sketch is useful for the pure multiset game, but stale as a model of implementation traces. The current proof must parameterize observations explicitly as `O` and compare measured leakage against `BayesOracle(pi,k,O)`.

**Status**: archival architectural draft; useful only for the pure multiset subgame and notation.
**Companion to**: `easycrypt_h2/` (precision-side proof for H2 row truncation).
**Goal of this doc**: define the adversary, define the security game, state the main theorem, sketch the proof. The actual EasyCrypt formalization comes after this sketch is reviewed.

---

## 0. Why this document exists

The kill-plan's original thesis claimed F2(k=4) gives single-trace template accuracy ≤ 1/k = 25%. After P0 lit review (Pessl/Lin/Mitaka triangulation, see `PHASE0_MEMO.md`), three facts make the "1/k" bound wrong as stated:

1. **z₀ is sharply non-uniform**: P(z₀ = 0) ≈ 0.36 in Falcon. A trivial attacker who always guesses 0 gets 36% accuracy — *above* the claimed 25% bound. The 1/k bound from symmetric crypto assumes uniform secrets.

2. **The adversary doesn't just "guess a position"**: they observe a leakage trace that, even under perfect dummy indistinguishability, reveals the *multiset* of (real + dummies). Bayesian inference over that multiset is the actual best strategy, not uniform-random position guessing.

3. **Horizontal aggregation across ~1024 SamplerZ calls per signature** is Pessl-style territory. The single-call bound must compose into a multi-call bound without blowing up.

This sketch fixes the math.

---

## 1. Notation and setup

| Symbol | Meaning |
|---|---|
| `z₀ ∈ {0, 1, ..., 18}` | the secret half-Gaussian sample produced by Falcon's `gaussian0_sampler` for one BerExp call |
| `π` | PMF of `z₀`, where `π(v) = P(gaussian0_sampler = v)`. From Falcon's RCDT: `π(0) ≈ 0.3595`, `π(1) ≈ 0.3092`, ..., `π(18) ≈ 2⁻⁷²` |
| `k` | number of candidates per shuffled BerExp call (1 real + k-1 dummies). Default k = 4. |
| `D` | dummy distribution; the (k-1) decoy z₀ values are i.i.d. samples from `D` |
| `σ ∈ S_k` | random permutation applied to the k candidates, uniform over the symmetric group |
| `L` | leakage function: side-channel observation of one BerExp gadget invocation. Concrete realization: power trace from Chipwhisperer-Lite |
| `τ = L(σ, z₀, d₁, ..., d_{k-1})` | the observed trace |
| `M = 2N · num_iter` | number of SamplerZ calls per Falcon signature. For Falcon-512 dyn-sign with average 2 iterations of the outer rejection loop, `M ≈ 2 · 512 · log₂(512) · 2 ≈ 18000` (precise figure to be measured empirically) |

Two distinct senses of "secret" must be distinguished:
- **Per-call secret**: the value `z₀` used in *this particular* BerExp invocation.
- **Per-signature secret**: the full vector `(z₀^(1), ..., z₀^(M))` of all SamplerZ outputs in one Falcon signature.

The protected SamplerZ's job is to hide the per-call secret. The Falcon key-recovery attack ultimately wants the per-signature secret. Our security claim concerns the former; we then reduce the latter to it.

---

## 2. Adversary model

Three adversary classes, in increasing power:

### A_prior — the trivial adversary
- Receives no information; outputs `g = argmax_v π(v) = 0`.
- Accuracy: `π(0) = 0.3595`. This is the floor — any countermeasure that achieves accuracy below this would be doing *worse* than ignoring the trace, which is impossible. **Any honest security claim must compare to `π(0)`, not to 0.**

### A_single — single-call template adversary
- Observes one trace `τ` from one BerExp call.
- Has profiling-phase access: can build templates of `L` on chosen-`z₀` inputs.
- Outputs guess `g ∈ {0..18}`.
- This is exactly the adversary in Table 5 of Lin et al. 2025 (their 57%/62% accuracies are A_single applied to F1).

### A_horiz — horizontal-aggregation adversary
- Observes `(τ⁽¹⁾, ..., τ⁽ᴹ⁾)` for all M SamplerZ calls in one signature.
- Same profiling access.
- May exploit cross-call correlations.
- Outputs tuple `(g⁽¹⁾, ..., g⁽ᴹ⁾)`.
- This is the Pessl-2016 adversary at the scale our scheme actually faces.

Out of scope (for now): multi-signature adversaries who aggregate across many signatures. Those reduce to A_horiz by union bound and are handled in Phase 4 of the kill plan as a corollary.

---

## 3. Security games

### 3.1 Single-call game `Exp_F2-SC^k(A_single)`

```
1.  z₀  ← π                                  // sample the real
2.  (d₁, ..., d_{k-1}) ← D^{k-1}             // sample dummies
3.  σ ← Uniform(S_k)                         // pick a permutation
4.  τ ← L(BerExp_shuffled(σ, z₀, d₁, ..., d_{k-1}))
5.  g ← A_single(τ)
6.  Return 1 if g = z₀ else 0
```

Adversary advantage:

```
Adv_SC^k(A_single) := Pr[Exp_F2-SC^k = 1] - π(0)
```

We subtract `π(0)` so that `Adv = 0` means "the trace gave the adversary no benefit beyond the prior."

### 3.2 Horizontal game `Exp_F2-HZ^{k,M}(A_horiz)`

```
1.  For i = 1..M:
2.    z₀⁽ⁱ⁾ ← π
3.    (d₁⁽ⁱ⁾, ..., d_{k-1}⁽ⁱ⁾) ← D^{k-1}
4.    σ⁽ⁱ⁾ ← Uniform(S_k)
5.    τ⁽ⁱ⁾ ← L(BerExp_shuffled(σ⁽ⁱ⁾, z₀⁽ⁱ⁾, d₁⁽ⁱ⁾, ..., d_{k-1}⁽ⁱ⁾))
6.  (g⁽¹⁾, ..., g⁽ᴹ⁾) ← A_horiz(τ⁽¹⁾, ..., τ⁽ᴹ⁾)
7.  Return (1/M) · #{i : g⁽ⁱ⁾ = z₀⁽ⁱ⁾}
```

Adversary advantage:

```
Adv_HZ^{k,M}(A_horiz) := E[Exp_F2-HZ^{k,M}] - π(0)
```

Note `Exp_F2-HZ` returns a *rate* of correct guesses, not a single bit.

---

## 4. The old theorems this sketch tried to prove

These theorem targets are archival. The current theorem target must condition on an explicit observation variable `O`.

### Theorem 1 (single-call bound)

For all PPT adversaries `A_single` and dummy distribution `D = π`:

```
Adv_SC^k(A_single) ≤ μ(π, k) - π(0)
```

where `μ(π, k)` is the **Bayes-optimal multiset-predictor accuracy**:

```
μ(π, k) := E_M [ max_v Pr[z₀ = v | M] ]
        = Σ_M Pr[multiset = M] · max_v Pr[z₀ = v | multiset = M]
```

By Bayesian inversion with i.i.d. dummies from π:

```
Pr[z₀ = v | M] = π(v) · #{i : M_i = v} / Σ_w π(w) · #{i : M_i = w}
```

The bound `μ(π, k)` is computable in closed form for small k. For Falcon's π and k = 4:

| k | μ(π, k) | μ - π(0) (the actual advantage bound) |
|---|---|---|
| 1 (unprotected) | 1.000 | 0.640 |
| 2 | ~0.51 | ~0.15 |
| **4** | **~0.42** | **~0.06** |
| 8 | ~0.38 | ~0.02 |
| 19 (Lin et al.'s F1) | π(0) = 0.36 | 0 |

(Numerical values pending — must be computed exactly in `bayes_bound.py`.)

**Interpretation**: under F2(k=4), an optimal adversary's accuracy is bounded above by ~42%, vs the trivial-prior baseline of 36%, vs Lin et al.'s measured 58% on protected `return`. F2(k=4) is *stronger* than F1 at the single-call level, despite using 4 candidates instead of 19.

### Theorem 2 (horizontal bound)

For all PPT adversaries `A_horiz` against M SamplerZ calls in one signature:

```
Adv_HZ^{k,M}(A_horiz) ≤ μ(π, k) - π(0) + ε_horiz(M)
```

where `ε_horiz(M)` is the cross-call leakage. **The key claim**: `ε_horiz(M) = 0` if the per-call shuffles are independent and the leakage function is memoryless across calls.

Proof sketch (formal in Phase 1.5): independence of per-call (z₀, d, σ, leakage noise) → per-call leakages are conditionally independent given the per-call secrets → no horizontal aggregation gain.

The hard part is *establishing* independence in the physical implementation. PRNG output reuse, shared scratch memory, or cache state across calls would all introduce non-zero `ε_horiz`. This is what the Chipwhisperer evaluation in Phase 3 measures empirically.

---

## 5. Proof strategy

### 5.1 Theorem 1 — reduces to leakage-conditional Bayesian estimation

The proof goes through three steps:

1. **Reduction to multiset observation.** Show that for the optimal A_single, the trace `τ` reveals at most the multiset `{z₀, d_1, ..., d_{k-1}}` and nothing more about the permutation. This requires that the leakage function L is *invariant* under permutation of its arguments — which is true if the BerExp gadget code is identical for all k calls and the random tape σ is independent of (z₀, d₁, ..., d_{k-1}).

2. **Bayes-optimal estimator on multisets.** Given the multiset, the best estimator outputs argmax_v Pr[z₀ = v | multiset]. By the formula in §4, this is computable directly from π.

3. **Inequality.** Any A_single is bounded by the Bayes-optimal estimator: `Adv(A_single) ≤ Adv(A_Bayes)` = `μ(π, k) - π(0)`.

The non-trivial part is step (1): in practice, the leakage function L is NOT perfectly permutation-invariant. Hardware ordering effects, register reuse, and cache state all break invariance. The proof's tightness depends on a **leakage-invariance assumption** that must be validated empirically (this is what the Chipwhisperer evaluation in Phase 3 ultimately tests).

### 5.2 Theorem 2 — reduces to per-call independence

If per-call leakages are conditionally independent given per-call secrets:

```
Pr[A_horiz wins call i | τ⁽¹⁾, ..., τ⁽ᴹ⁾] = Pr[A_horiz wins call i | τ⁽ⁱ⁾]
```

then the per-call analysis from Theorem 1 applies independently to each call, and the per-call advantage is `Adv_SC^k`. Averaging:

```
E[Exp_F2-HZ^{k,M}] = (1/M) Σᵢ E[A_horiz wins call i] ≤ μ(π, k)
```

So `Adv_HZ ≤ μ(π, k) - π(0) = Adv_SC^k`.

The conditional independence is broken if:
- (a) Per-call PRNG outputs are correlated (shared seed, weak PRNG)
- (b) Cache/branch-predictor state from call i affects timing of call i+1
- (c) Power-supply DC drift correlates across calls

Mitigations: (a) re-seed the PRNG between SamplerZ calls (~50-100 ns per call), (b) explicit cache flush or constant-time guarantees, (c) physical countermeasure (decoupling caps).

---

## 6. Subtleties and open questions

### Q1: Is `D = π` the right dummy distribution?

If dummies are drawn from D ≠ π, the multiset structure shifts and `μ(D, π, k)` may be lower OR higher than `μ(π, k)`. Three candidate D's to evaluate empirically:

- **D = π** (matched): cleanest theoretical analysis; concrete realization requires running gaussian0_sampler on a side-buffer (cost ~290 ns × (k-1) per BerExp).
- **D = Uniform({0..18})**: cheap to sample but produces detectably wrong distributions in the multiset; would *increase* attacker accuracy (multiset is biased).
- **D = replay buffer**: pre-recorded real z₀ values from prior signing sessions; bit-perfect statistical match, but adds state and complexity.

Recommendation: (D = π) for Phase 1 math; revisit if Phase 3 Chipwhisperer shows distinguishability.

### Q2: Is the leakage-invariance assumption defensible?

This is the assumption that L is permutation-invariant w.r.t. the k candidates. Pessl 2016's attack exploits the failure of this assumption at polynomial-shuffling scale (N=512). At k=4, the invariance is *easier* to maintain in code (smaller loop, fewer cache eviction events), but harder to guarantee formally.

The right empirical test (Phase 3): TVLA on the leakage of "F2-BerExp with permutation A" vs "F2-BerExp with permutation B" on identical inputs. If statistically distinguishable → invariance broken → proof unsound at that ε.

### Q3: Composability with masking?

If F2 is composed with a t-probing masked BerExp internally (so each individual call is also d-SNI for some d ≥ 1), the bound becomes:

```
Adv_combined ≤ min(Adv_SC^k, Adv_masking(d))
```

This is the "belt-and-braces" claim. It's not required for our paper but might appease reviewers who say "shuffling alone is brittle." Worth noting in the discussion section.

### Q4: What about the BerExp accept/reject *output* bit?

The protected gadget returns 1 bit (accept/reject). Even with perfect shuffling, the attacker observes the bit. Does that leak?

The accept probability is `ccs · exp(-x(z₀))`, which DEPENDS on z₀. So the bit is a (noisy) 1-bit leak of z₀, independent of any side-channel observation. In Falcon's signing loop, this bit drives the rejection-loop termination, so it's already "observable" to a network adversary timing the signature. Lin et al.'s impl gives the attacker this bit unconditionally; F2 does too. No new leakage, but it's the asymptotic floor on any side-channel countermeasure for SamplerZ — even a perfectly masked + shuffled BerExp leaks the accept bit.

### Q5: Falcon-512 vs Falcon-1024?

The π distribution is identical (it's gaussian0_sampler with σ_max = 1.8205, shared across degrees). Only M differs: M_512 ≈ 18000, M_1024 ≈ 40000. The horizontal bound from Theorem 2 is unaffected. So F2's security and cost are degree-invariant.

---

## 7. Deliverables for Phase 1

To complete Phase 1 (originally 6 weeks; revised to ~8 weeks given non-uniform-prior math):

1. **`bayes_bound.py`** — numerical computation of `μ(π, k)` for k ∈ {2, 3, 4, 6, 8, 16, 19}. ~50 lines.
2. **`PHASE1_PROOFS.md`** — full proofs of Theorem 1 and Theorem 2 in informal math. Target 10-15 pages.
3. **`easycrypt_f2/security/F2BerExpSCI.eca`** — EasyCrypt formalization of the single-call game.
4. **`easycrypt_f2/security/F2BerExpHorizontal.ec`** — formalization of the horizontal reduction.
5. **`easycrypt_f2/security/F2BerExpBayes.ec`** — formalization of the Bayes-optimal bound (this is the hardest of the four; may use `axiom` for the leakage-invariance assumption and import a maskVerif certificate for it later).
6. **Independent review** — circulate `PHASE1_PROOFS.md` to one external cryptographer before starting Phase 2 code.

---

## 8. Connection to the H2 work

H2 truncates the per-call row count from 19 to 15. F2 reduces the per-call candidate count from 19 to k = 4 (using shuffling instead of enumeration). These are *compatible* layered optimizations:

- H2: row count 19 → 15 (precision-side argument, see `easycrypt_h2/`)
- F2: candidate count 19 → 4 (security-side argument, this document)
- H2 + F2 combined: 4 candidates × 15 rows each = 60 BerExp-rows total, vs Lin et al.'s 38. Wait — that's WORSE.

Need to think about this more carefully. The H2 truncation applies *within* a single BerExp call (the inner loop), regardless of how many such calls happen. F2 reduces the *number of BerExp calls*. So:

- Lin et al. F1: 1 call enumerating 19 rows × 2 sign lanes = 38 row-computations
- H2 alone: 1 call enumerating 15 rows × 2 sign lanes = 30 row-computations
- F2 alone (k=4): 4 calls × 19 rows × 2 sign lanes = 152 row-computations (WORSE than Lin)

Wait, this is wrong. F2 doesn't enumerate per call — F2's BerExp is the *unprotected* BerExp (1 row computed for the actual z₀), repeated k times for the dummies.

Let me redo:
- Unprotected BerExp: 1 row computed (only for the actual z₀)
- Lin et al. F1: 19 × 2 = 38 rows enumerated, of which 1 is "real"
- F2 (k=4): 4 calls × 2 lanes × 1 real-row-each = 8 rows computed total
- F2 + H2 (k=4, N'=15): same as F2, since each F2 call only computes 1 row anyway (H2 doesn't help inside a single non-enumerating call)

So F2 makes H2 redundant at the BerExp-row level. F2 alone gives 8 row-computations (vs Lin's 38), a 4.75× reduction at the row level.

But there's still the x̃ precomputation, which Lin et al. enumerates as 19 rows even within one call. Does F2 also need to precompute x̃ for all 19 z₀ values per shuffled BerExp call?

This depends on the design. If F2 follows Lin et al.'s structure (precompute x̃ for all possible z₀ values per call, then read by index), then yes, H2 still applies to the precomputation. If F2 is more radical and only precomputes x̃ for the k=4 actual candidates, then H2 is moot.

**Open design question for Phase 1.5**: which version of F2 does the math?

- **F2-conservative**: Lin's gadget structure but with k shuffled "selector indices" per call instead of enumerating all 19. Compatible with H2.
- **F2-radical**: shuffle (real z₀, k-1 dummies) AT THE GAUSSIAN0_SAMPLER LEVEL, and only compute x̃ + BerExp for those k values. Incompatible with H2 (H2 makes no sense here).

F2-radical is theoretically cleaner; F2-conservative might be easier to argue security for. Phase 1 should pick one.

---

## 9. First-week tasks

1. Implement `bayes_bound.py` and produce the numerical table for k ∈ {2, 4, 8}.
2. Decide F2-conservative vs F2-radical (see §8).
3. Read Azouaoui et al. TCHES 2022(2) for prior-aware shuffling-bound techniques.
4. Read Veyrat-Charvillon et al. ASIACRYPT 2012 §3 for the "indirect leakage" failure modes.
5. Draft Theorem 1's proof in informal math, get external review.

Phase 1 advances when steps 1-5 are checked off, the Bayes bound `μ(π, 4)` is computed exactly, and the F2 design (conservative vs radical) is locked in.

---

*Last updated: 2026-05-15. Author: F2 project, kill-plan Phase 1, week 0.*
