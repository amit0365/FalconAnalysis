# Phase 1, Claim 2: Horizontal Independence Bound for F2-radical

**Status**: SP1.2 deliverable (week 5 of Phase 1). Sketch quality; for review at G1.2 (week 5 end).
**Prerequisites**: `PHASE1_PROOF_CLAIM1.md` (single-call bound), `PHASE1_MATH_SKETCH.md` §2-3 (notation, games).
**What this document proves**: under per-call independence, Claim 1's bound composes to the multi-call horizontal setting without aggregation gain. **Key corollary**: full-vector key recovery is computationally infeasible.

---

## 1. Theorem statements

We prove two theorems. C2a covers the per-call rate (what Lin et al. measure in Table 5); C2b covers the full-vector recovery (what matters for key recovery).

**Theorem C2a (per-call rate)**.
Under per-call independence (Definition 6 below), for all PPT adversaries `A_horiz` in the horizontal game `F2-HZ^{k,M}`:

```
Adv_HZ^{k,M}(A_horiz)  =  E[win-rate]  -  π(0)
                       ≤  μ(π, k)  +  ε_leak  -  π(0)
```

i.e., the per-call accuracy bound from Claim 1 carries over unchanged. **No horizontal aggregation gain.**

**Theorem C2b (full-vector recovery)**.
Under per-call independence, for any PPT adversary `A_vec` that outputs a full guess `(g⁽¹⁾, ..., g⁽ᴹ⁾)` for the per-signature secret vector:

```
Pr[A_vec recovers full vector]  =  Pr[∀i. g⁽ⁱ⁾ = z₀⁽ⁱ⁾]
                                ≤  (μ(π, k)  +  ε_leak)^M
```

For Falcon-512 with `M ≈ 18000`, `μ(π, 4) = 0.547`, and `ε_leak < 10⁻⁵` (Phase 3 target):

```
Pr[full-vector recovery]  ≤  0.547^{18000}  ≈  10⁻⁴⁶⁷⁷
```

i.e., **full-vector recovery is computationally infeasible by an enormous margin**.

---

## 2. Notation (recap)

| Symbol | Meaning |
|---|---|
| `M` | number of SamplerZ calls per Falcon signature. For Falcon-512 dyn-sign, `M ≈ 18000` (precise value measured empirically in Phase 2). |
| `i = 1, ..., M` | per-call index |
| `z₀⁽ⁱ⁾, d_j⁽ⁱ⁾, σ⁽ⁱ⁾, τ⁽ⁱ⁾` | per-call versions of single-call variables |
| `N⁽ⁱ⁾` | per-call randomness: includes the PRNG state used for σ⁽ⁱ⁾ and the dummy sampling |
| `S⁽ⁱ⁾` | per-call ambient state: cache lines, register values, branch-predictor history, power-supply drift, etc. |

The per-call leakage trace is `τ⁽ⁱ⁾ = L(σ⁽ⁱ⁾, z₀⁽ⁱ⁾, d⁽ⁱ⁾_1, ..., d⁽ⁱ⁾_{k-1}, S⁽ⁱ⁾)` where `S⁽ⁱ⁾` enters as nuisance state.

---

## 3. Independence definitions

The crux of Claim 2 is what "independence" means precisely.

**Definition 6 (Per-call independence)**.
Per-call independence holds if the joint distribution factors as:

```
Pr[ (σ⁽ⁱ⁾, d⁽ⁱ⁾, S⁽ⁱ⁾)_{i=1..M} ]  =  ∏_{i=1}^{M} Pr[σ⁽ⁱ⁾, d⁽ⁱ⁾, S⁽ⁱ⁾]
```

That is, each call's randomness (permutation, dummies) and ambient state are independent of all other calls'. Note: `z₀⁽ⁱ⁾` is a *function* of the Falcon outer state (specifically `mu⁽ⁱ⁾`, `sigma⁽ⁱ⁾`) and is NOT independent across calls — that's fine; the secret being independent isn't what Claim 2 needs.

**Definition 7 (Independent-leakage assumption)**.
Conditional on `(z₀⁽ⁱ⁾, d⁽ⁱ⁾, σ⁽ⁱ⁾, S⁽ⁱ⁾)`, the trace `τ⁽ⁱ⁾` is independent of all other-call traces and inputs. Formally:

```
τ⁽ⁱ⁾  ⊥⊥  (τ⁽ʲ⁾, z₀⁽ʲ⁾, d⁽ʲ⁾, σ⁽ʲ⁾, S⁽ʲ⁾)_{j ≠ i}
       |
       (z₀⁽ⁱ⁾, d⁽ⁱ⁾, σ⁽ⁱ⁾, S⁽ⁱ⁾)
```

This is a "no hidden side-channel" assumption: the leakage of call `i` is determined entirely by call `i`'s own inputs and ambient state — there's no clock-glitch, no shared-DRAM-bus side-channel, no global counter being read by L from outside call `i`.

**Remark**. Definition 6 is enforced by implementation (re-seed PRNG, flush state). Definition 7 is enforced by hardware (electromagnetic isolation, decoupling capacitors). Together they form the *F2-radical isolation hypothesis*.

---

## 4. Proof of Theorem C2a (per-call rate)

**Proof**.
The win-rate is `(1/M) ∑ᵢ 1{g⁽ⁱ⁾ = z₀⁽ⁱ⁾}`. So:

```
E[win-rate]  =  (1/M)  ∑ᵢ  Pr[g⁽ⁱ⁾ = z₀⁽ⁱ⁾]
```

We bound each term. The adversary's guess `g⁽ⁱ⁾` is a deterministic function `A_horiz`(τ⁽¹⁾, ..., τ⁽ᴹ⁾). Under Definitions 6-7, conditioned on `(z₀⁽ⁱ⁾, d⁽ⁱ⁾, σ⁽ⁱ⁾, S⁽ⁱ⁾)`, the other traces `τ⁽ʲ⁾` (j ≠ i) are independent of `(z₀⁽ⁱ⁾, τ⁽ⁱ⁾)`. So the other traces carry zero information about `z₀⁽ⁱ⁾` beyond what `τ⁽ⁱ⁾` already encodes:

```
Pr[g⁽ⁱ⁾ = z₀⁽ⁱ⁾]  =  Pr[A_horiz(τ⁽¹⁾, ..., τ⁽ᴹ⁾)_i  =  z₀⁽ⁱ⁾]
```

Define an "effective single-call adversary" `A_i(τ)` that takes only `τ⁽ⁱ⁾` and outputs whatever `A_horiz` outputs for position `i` (after marginalizing over the independent other traces). By the data-processing inequality:

```
Pr[A_horiz(...)_i = z₀⁽ⁱ⁾]  ≤  max_A  Pr[A(τ⁽ⁱ⁾) = z₀⁽ⁱ⁾]  =  μ(π, k)  +  ε_leak     (Claim 1)
```

So:

```
E[win-rate]  ≤  (1/M)  ∑ᵢ  (μ(π, k)  +  ε_leak)  =  μ(π, k)  +  ε_leak
```

Subtracting `π(0)`:

```
Adv_HZ  =  E[win-rate]  -  π(0)  ≤  μ(π, k)  -  π(0)  +  ε_leak
```

QED.

**Remark on tightness**. The bound is tight in the sense that the single-call optimal adversary applied to each call independently achieves exactly `μ(π, k) + ε_leak` per call (by Claim 1), so the horizontal rate is exactly `μ(π, k) + ε_leak`. No cleverer horizontal adversary can do better under per-call independence.

---

## 5. Proof of Theorem C2b (full-vector recovery)

**Proof**. The adversary wins iff every call's guess is correct. Under per-call independence (Definition 6 → conditional independence of `(τ⁽ⁱ⁾, z₀⁽ⁱ⁾)` pairs across i):

```
Pr[∀i. g⁽ⁱ⁾ = z₀⁽ⁱ⁾]  =  ∏ᵢ  Pr[g⁽ⁱ⁾ = z₀⁽ⁱ⁾]
                     ≤  ∏ᵢ  (μ(π, k)  +  ε_leak)         (Claim 1 per call)
                     =  (μ(π, k)  +  ε_leak)^M
```

The first step requires that the per-call guesses are conditionally independent under the optimal joint adversary. This follows from Definition 6: the only information `A_vec` has about call `i` is `τ⁽ⁱ⁾` (other traces are independent under Definition 7), so the optimal joint adversary factorizes into per-call optimal adversaries. ∎

**Numerical instance for Falcon-512**.

| k | μ + ε_leak (target) | M = 18000 | (μ + ε_leak)^M |
|---|---|---|---|
| 4 | 0.547 + 10⁻⁶ | 18000 | ≈ 10⁻⁴⁶⁷⁷ |
| 4 | 0.547 + 10⁻⁴ | 18000 | ≈ 10⁻⁴⁶⁷⁵ |
| 4 | 0.547 + 10⁻² | 18000 | ≈ 10⁻⁴⁶⁶⁰ |

Full-vector recovery is **astronomically unlikely** under any reasonable `ε_leak`. Even with `ε_leak = 10⁻¹` (catastrophic hardware leakage), the bound is 10⁻³¹⁵⁰.

**Caveat**. This bound is for *exact full-vector recovery*. The adversary in practice settles for *partial* recovery (e.g., 90% of coefficients correct) and uses error-correction / lattice-decoding to fix the rest. We discuss this in §8.

---

## 6. Implementation requirements (forcing independence)

Per-call independence is an *engineering invariant*. To establish it, the F2-radical implementation must satisfy:

### 6.1 PRNG re-seeding

Each call's `σ⁽ⁱ⁾` and dummy generation must use entropy independent of prior calls. Three implementation options:

**Option A — fresh seed per call** (most independent):
- Read 256 bits of entropy from a hardware RNG before each BerExp call
- Use it to seed a fresh ChaCha20 instance for this call's σ + dummies
- Cost: ~50-100 ns per call × M = 0.9-1.8 ms per signature
- **Recommended**.

**Option B — one seed per signature, k-bit increments** (cheaper but weaker):
- Seed a ChaCha20 once at signature start
- Each call consumes 256 bits of output (for σ + dummies)
- Cost: ~10 ns per call × M = 180 µs per signature
- Risk: PRNG state correlation across calls. If ChaCha20 is broken or the adversary recovers some state, independence breaks.

**Option C — TRNG every k calls** (compromise):
- Re-seed every K calls (e.g., K = 100)
- Cost: ~100 ns × (M/K) = 18 µs per signature
- Risk: K-call correlation window; per-call independence holds only modulo K

**Decision**: Option A in Phase 2 prototype; relax to Option C if profiling shows excessive overhead.

### 6.2 Cache state isolation

Cache state from call `i` can affect timing of call `i+1`. Two mitigations:

**Mitigation A — constant-time SP1 BerExp**:
- The F2-radical BerExp gadget has bounded loop structures (no data-dependent branches)
- All table reads use fixed-stride patterns
- Cache state at the start of each call is deterministic relative to call content
- Validate: maskVerif or LLVM-level constant-time checker

**Mitigation B — cache flush between calls**:
- Explicit cache flush (ARM: `CCSIDR` + `DCCIVAC`) at the boundary
- Cost: ~50 cycles × M = 90 µs per Falcon-512 signature (negligible)
- Eliminates cross-call cache state coupling

**Recommended**: A primary, B as belt-and-braces.

### 6.3 Register zeroing

Per-call BerExp accumulates values in registers. If those registers retain content into the next call, Hamming-weight leakage from call `i` is correlated with call `i+1`'s starting state.

**Mitigation**: Zero all callee-saved registers at the end of each BerExp call (~10 cycles, negligible).

### 6.4 Branch predictor and out-of-order state

Modern Intel/ARM CPUs have branch-predictor history shared across calls. We need:

**Constraint**: F2-radical's branch-predictor footprint is the same regardless of (z₀, dummies).

This is automatically true if F2-radical has no z₀-dependent branches (which it does not, by design — only the *index into the candidate table* depends on σ, which is itself random).

### 6.5 Power supply DC drift

This is harder. Long-term DC drift can correlate across calls within a signature.

**Mitigation**:
1. Hardware-level: decoupling capacitors on power rails (Phase 3 setup detail).
2. Algorithmic: re-randomization gadget that injects high-frequency noise.

**Estimated residual ε_drift**: 10⁻⁵ to 10⁻³ depending on hardware. Phase 3 measures.

---

## 7. Failure modes (when independence breaks)

If any of §6's requirements is violated, the proof of C2 breaks at the corresponding step. Some specific failure modes and their consequences:

### 7.1 PRNG state recovered

If the adversary recovers ChaCha20 state mid-signature (Option B), then per-call `σ⁽ⁱ⁾` becomes *predictable* for subsequent calls. This breaks Definition 6 critically.

**Consequence**: post-recovery calls become *unprotected* — adversary knows the shuffle. Effective security is `μ(π, 1) = 1.0` on those calls.

**Mitigation**: Option A (fresh seed per call) makes this attack require new TRNG breaks per call.

### 7.2 Cache state leaks

If F2-radical's table reads have variable cache footprint (e.g., variable-stride access), the cache state of call `i+1` reveals which table entries call `i` read.

**Consequence**: Per-call leak bounded by `cache state size / 256 bits ≈ 32 KB / 32 B = 1024 bits` of state. ε_leak rises by ~10⁻³ to 10⁻¹ depending on attacker template quality.

**Mitigation**: §6.2 constant-time gadget + cache flush.

### 7.3 Power supply DC coupling

Long-term DC drift is the hardest to mitigate. It causes calls within a signature to share leakage characteristics that the adversary can exploit via signal averaging.

**Consequence**: As more calls are processed, ε_horiz grows like `√M / SNR_DC`. For typical Chipwhisperer setup, this is `√18000 / 100 ≈ 1.3` — saturates.

**Mitigation**: Phase 3 measures DC-noise SNR; the security claim is conditioned on the measured value.

### 7.4 Hardware glitches and faults

Out of scope for Claim 2. Fault attacks (DFA, glitch injection) are a separate threat model.

---

## 8. The "partial vector recovery" attack

Theorem C2b bounds *exact* full-vector recovery. In practice, the lattice-decoding attack chain works as follows:

1. **Per-coefficient guesses**: adversary uses τ⁽ⁱ⁾ to guess z₀⁽ⁱ⁾ for each i.
2. **Identify high-confidence guesses**: a subset of guesses has confidence > 0.7 (say).
3. **Lattice-decode the residual**: use the high-confidence guesses as a partial known-key, then run BKZ on the remaining lattice.

The cost of step 3 depends on how many *bits* of information the adversary has correctly recovered. The threshold for lattice decoding to succeed is typically **~80% of coefficients with ~50% confidence each**.

For F2(k=4) with `μ + ε_leak = 0.55`:
- Expected % correct: 55%
- Expected confidence per guess: ~0.7 on most-confident guesses, ~0.3 on others
- Lattice attack: requires `0.8 · 512 = 410` coefficients with > 50% confidence
- We have at best `0.55 · 512 = 282` correct guesses; this is below the decoding threshold

So under the optimal F2(k=4) attack, lattice decoding does NOT succeed for Falcon-512. Combined with Lin et al.'s F1 at 58% (which is similar), this is why Falcon's published security parameters survive both countermeasures.

A more careful analysis (Phase 4 paper section) would quantify the lattice decoding margin in bits of security.

---

## 9. The composed main theorem (preview)

Combining Claim 1 (single-call) and Claim 2 (horizontal), the main theorem of the paper is:

```
Theorem (main, paper-ready).
Let F2-radical^{k} be the F2 countermeasure with k candidates per BerExp call.
Under per-call independence (Definitions 6-7), for any PPT adversary against
M SamplerZ calls in one Falcon-512 signature:

  Adv  =  E[win-rate]  -  π(0)
       ≤  μ(π, k)  +  ε_leak  -  π(0)

In particular, for k = 4:  Adv  ≤  0.187  +  ε_leak.

Full-vector recovery probability is  ≤  (μ(π, k) + ε_leak)^M.
For Falcon-512 with k = 4, M = 18000, ε_leak ≤ 10⁻⁶:
  Pr[full-vector]  ≤  0.547^{18000}  ≈  2^{-15580}.
```

This is the headline result; the formal version goes in `PHASE1_MAIN_THEOREM.md` (forthcoming).

---

## 10. What's left for SP1.3 and SP1.4

**SP1.3 (Claim 3 design, week 6)**: define the empirical test for ε_leak on Chipwhisperer. Specifically:
- TVLA on F2-BerExp(σ_a, X) vs F2-BerExp(σ_b, X') where M(X) = M(X'). Measures Definition 3's ε.
- Cross-call autocorrelation test on full signatures. Measures Definitions 6-7 violation.

**SP1.4 (composition, week 7)**: combine C1 + C2 into the formal main theorem and verify it composes correctly. Mostly bookkeeping at this point — the conceptual work is done.

---

## 11. Loose ends to flag for G1.2 review

1. **Lattice-decoding margin quantification** (§8). The "~80% threshold" is folklore; an actual cryptanalysis paper (e.g., Albrecht-Player-Scott estimator) should be cited.

2. **The "data-processing inequality" step in §4** is informal. A rigorous version uses Pinsker's inequality or direct TV-distance manipulation. Worth tightening for paper.

3. **Conditional independence in §5** glosses over a subtlety: the *adversary's strategy* may correlate guesses even if the inputs are independent. The proof actually needs to argue that the *Bayes-optimal* joint strategy factorizes, not that all strategies do. (It does, by exchangeability under Definition 7.)

4. **PRNG cost projection in §6.1** is rough. Need to bench actual ChaCha20-on-STM32F415 throughput to confirm 50-100 ns/call assumption.

5. **Branch predictor history sharing** (§6.4) — modern speculative-execution CPUs may leak via Spectre-style side channels even when our gadget is constant-time. Phase 3 setup uses Cortex-M4 (no speculation), so this is moot for our measurement environment but a concern for high-performance deployment.

---

## 12. Outcome / gate status

If all of §6's implementation requirements are met and §7's failure modes are mitigated, then:

- **G1.2 PASSES**: implementation cost of independence < 10% (estimated 1-2 ms / 17 ms per signature ≈ 6-12%, borderline; tighten in Phase 2).
- C2a and C2b stand as proved.

If G1.2 fires (e.g., re-seeding too slow), fallback per `KILL_PLAN_SECURITY.md`:
- Refresh every K calls instead of every call (K ≈ 100 reasonable).
- Pre-batched PRNG state at signature start.

---

*Author: F2 project, Phase 1 SP1.2 draft. Last updated: 2026-05-15.*
*Next deliverable: PHASE1_PROOF_CLAIM3.md (week 6 — ε_leak empirical test design).*
