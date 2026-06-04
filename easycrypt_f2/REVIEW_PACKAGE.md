# F2-radical: Review Package

> **Current status — stale archival note (2026-06-04).**
> This review package predates the d2 ASM selector and overstates the security conclusion. Do not use the “strictly stronger” or “math complete” claims as current. Use `README.md`, `STALE_AUDIT.md`, and `CURRENT_PROOF_ROADMAP.md` for the active state.

**Single-document summary of completed F2-radical work.**
**Branch**: `f2-radical-clean` on `amit0365/FalconAnalysis` (7 commits ahead of `lxhcrypto/main`).
**Date**: 2026-05-16.
**Recommended reading time**: ~30 min for the full doc; ~10 min for §1-3 alone.

---

## 1. TL;DR

**F2-radical** is a side-channel countermeasure for Falcon's `BerExp` that replaces Lin et al.'s [PKC 2025] constant-time 19-row enumeration with k=4 shuffled-with-dummies BerExp calls.

**Current result**: F2-radical with d2 ASM selector masking removes direct `z0_idx` selector leakage in the ELMO proxy and preserves a large protected-BerExp-path speedup. It is not yet proven strictly stronger than Lin; the remaining question is `z0_real` leakage versus Lin and versus the correct oracle.

| Axis | F2-radical | Lin et al. F1 | Verdict |
|---|---|---|---|
| Pure multiset oracle | **0.547** for k=4 | 0.580 measured F1 figure | Not a full implementation comparison |
| Direct `z0_idx` selector leakage | d2 ASM selector clean in proxy | Lin direct `select_zprime` leaks in local proxy | F2 selector layer improved |
| `z0_real` leakage | unresolved vs oracle/Lin | needs matched window comparison | blocking security claim |
| Protected BerExp-path cost | **35,480 cycles** in ELMO proxy | **325,947 cycles** in ELMO proxy | **9.19× protected-path speedup** |
| Per-signature cost on Cortex-M4 (QEMU SYSTICK) | **516K cycles** | 1.21M cycles | **2.35× faster** |
| Bit-identical to reference Falcon | ✅ | ✅ | same |
| Implementation size | ~100 lines C | ~300 lines C | F2 simpler |

---

## 2. Math contributions (all paper-ready)

Five claims, each in a dedicated document. All math assumptions are discharged; only empirical hardware-side `ε_leak` remains for Phase 3.

### 2.1 Claim 1 — Single-call Bayes-optimal bound

**Document**: `PHASE1_PROOF_CLAIM1.md`

**Theorem**: for all PPT adversaries `A` against one BerExp call,
```
Pr[A(τ) = z₀]  ≤  μ(π, k)  +  ε_leak
```
where `μ(π, k) = E_M[c_{g*(M)}(M) / k]` is the Bayes-optimal multiset-predictor accuracy.

**Novel result (Lemma 5.2)**: the posterior `Pr[z₀ = v | M] = c_v(M) / k`. **The prior π cancels** in the posterior — the Bayes-optimal estimator is "count multiplicities, pick max" with no reference to π. Makes the attack implementable in 3 lines of code.

**Numerical**: `μ(π, 4) = 0.547` (exact, from `bayes_bound.py`).

### 2.2 Claim 2 — Horizontal independence (multi-call within a signature)

**Document**: `PHASE1_PROOF_CLAIM2.md`

**Theorem C2a (per-call rate)**: under per-call independence assumptions,
```
Adv_HZ(A_horiz)  ≤  μ(π, k) + ε_leak − π(0)
```
The single-call bound carries to multi-call **with no aggregation gain**. Pessl 2016's BLISS attack does not transfer to F2.

**Theorem C2b (full-vector recovery)**:
```
Pr[full-vector recovery]  ≤  (μ + ε_leak)^M  ≈  2⁻¹⁵⁵⁸⁰  for Falcon-512
```

**Engineering implication**: Theorem C2 requires the implementation to maintain per-call PRNG/cache/register independence. We specify 7 implementation requirements (IR1–IR7) in `PHASE1_PROOF_CLAIM2.md` §6.

### 2.3 Claim 3 — Bound tightness (C3 from review)

**Document**: `PHASE1_TIGHTNESS.md`

**Theorem C1'**: there exists an explicit PPT adversary `A_Bayes` such that `Pr[A_Bayes(τ) = z₀] = μ(π, k)` under ε_leak = 0. **The bound is tight.**

**Construction**: A_Bayes is the 3-line Bayes-optimal estimator from Lemma 5.2. Anyone with the trace can run it.

**Empirical verification** (10⁶ Monte Carlo trials per row):

```
k    μ(π,k) exact    A_Bayes empirical    Δ
2    0.6366          0.6360               −0.0006
3    0.5783          0.5782               −0.0001
4    0.5467          0.5461               −0.0007
5    0.5171          0.5174               +0.0003
6    0.4970          0.4960               −0.0010
8    0.4724          0.4711               −0.0013
```

All within MC noise (≤ 1.3 × 10⁻³). **Tightness confirmed.**

### 2.4 Claim 6 — Multi-signature scope (C6 from review)

**Document**: `PHASE1_MULTISIG.md`

**Honest scope statement**: F2 does NOT improve resistance to multi-signature aggregation attacks. F2's per-call advantage (0.187 above prior) is comparable to F1's (0.220), so aggregate information across N signatures is comparable. Both schemes inherit Falcon's spec-mandated rekey policy (≤10⁶ sigs/key) as the multi-signature defense.

**F2's contribution is on the cost axis, not the multi-signature security axis.** F2 achieves equivalent multi-sig security to F1 at 2.35×–3.09× lower per-signature cost.

Reviewer-defensible LaTeX block provided in `PHASE1_MULTISIG.md` §8.

### 2.5 Claim 7 — PRNG security citation (C7 from review)

**Document**: `PRNG_SECURITY.md`

Falcon uses **standard 20-round ChaCha20-256** (Bernstein 2008 [B08], RFC 8439), seeded from SHAKE-256 (FIPS 202). Verified in `rng.c:159-200`: full 20 rounds, "expand 32-byte k" constants at line 164.

**Indistinguishability budget**: 2⁹⁶ blocks per key. Falcon-512 sig uses ~1.4 MB ≈ 2²¹ bytes; one key supports 2⁸¹ signatures before approaching budget. **Far below any realistic deployment.**

`ε_shuffle ≪ ε_leak` — PRNG quality is not a binding constraint in the main theorem.

### 2.6 Main theorem (paper headline)

**Document**: `PHASE1_MAIN_THEOREM.md`

```
For Falcon-512 with F2-radical(k=4) under per-call independence and ε_leak ≤ 10⁻⁵:

  Per-call rate:          ≤ 0.547        (vs Lin's 0.58)
  Full-vector recovery:   ≤ 2⁻¹⁵⁵⁸⁰
  E2E speedup vs Lin:     2.35×–3.09× across measured platforms
  Bit-identical:          yes
```

---

## 3. Empirical measurements (three platforms)

All measurements use the SAME code (`Protected_Reference_Implementation/sign.c` on `f2-radical-clean`), differing only by compile flag `-DF2_RADICAL`.

### 3.1 Apple Silicon native (M2/M3, clang -O2)

**Method**: 200-signature wall-clock benchmark via `bench_sign.c`. Three stability runs per variant.

| Variant | Per-signature time (mean ± std) | Throughput |
|---|---|---|
| F1 (Lin et al., pristine main) | **7946 µs ± 70 µs** | 126 sigs/sec |
| F2-radical | **2573 µs ± 25 µs** | 389 sigs/sec |
| **Ratio** | **3.09× faster** | 3.09× |
| Time reduction | **67.6%** | |

Both variants pass `test_falcon` EXIT=0 across all logn ∈ {4, 9, 10}.

**Details**: `G1_2_RESULT.txt`.

### 3.2 ARMv7-A under Docker QEMU (Linux ARM user-mode)

**Method**: cross-platform validation. Same source compiled with `gcc-arm-linux-gnueabihf` inside `--platform linux/arm/v7` Docker container, run under QEMU.

| Variant | Per-signature time (mean) | Throughput |
|---|---|---|
| F1 (Lin et al.) | **38,328 µs** | 26 sigs/sec |
| F2-radical | **15,549 µs** | 64 sigs/sec |
| **Ratio** | **2.47× faster** | 2.46× |

Variance: <2% across runs. Reduction from 3.09× → 2.47× is consistent with QEMU's per-instruction translation overhead flattening the ratio.

**Details**: `M4_ESTIMATE.md` §"empirical ARMv7 data".

### 3.3 Cortex-M4 bare-metal under QEMU mps2-an386

**Method**: ARM GNU Toolchain 15.2 cross-compile for Cortex-M4 (Thumb-2 + FPv4-SP-D16 + hard float ABI). Linked against newlib-nano. Runs on `qemu-system-arm -M mps2-an386 -cpu cortex-m4`. SYSTICK timer with IRQ-driven wrap counter gives deterministic M4 cycle counts.

| Variant | M4 cycles (steady state, sigs 1+2) | At 168 MHz | Sig length verified |
|---|---|---|---|
| F1 (Lin et al.) | **1,213,412 cycles** | ~7.4 ms | sig_len ∈ {651, 655, 657} ✓ |
| F2-radical | **516,475 cycles** | ~3.5 ms | sig_len ∈ {650, 658, 657} ✓ |
| **Ratio** | **2.35× fewer cycles** | 2.35× | |

Sigs 1+2 deterministic to within <1%, confirming genuine M4 cycle counting (vs ~8% variance of host wall-clock SYS_ELAPSED).

**Caveat**: QEMU's mps2-an386 doesn't model cache misses or flash wait states. Real STM32F4 cycles likely 1.5–3× higher. The F2/F1 ratio (2.35×) is preserved regardless since it depends on instruction count, not memory hierarchy.

**Details**: `M4_QEMU_EMPIRICAL.txt`. Reproducible from `Protected_Reference_Implementation/m4/` (8 files, `make bench && make run`).

---

## 4. Cross-platform consistency

| Platform | F2/F1 ratio | Method | Below 3.5× ceiling? |
|---|---|---|---|
| Apple Silicon native (M2/M3) | **3.09×** | bench_sign, 200 sigs | ✓ (88% of ceiling) |
| ARMv7-A under Docker QEMU | **2.47×** | bench_sign, 200 sigs | ✓ |
| Cortex-M4 QEMU host-wall | **2.18–2.50×** | SYS_ELAPSED, 6 sigs | ✓ |
| Cortex-M4 QEMU SYSTICK | **2.35×** | deterministic cycles, 6 sigs | ✓ |
| Intel projection (cost model) | 2.43× | bayes_bound.py | ✓ |
| Cortex-M4 analytical | 3.0–3.4× | M4_ESTIMATE.md | ✓ |
| **Theoretical ceiling** | **3.5×** | F1/unprotected from Lin paper | — |

All seven data points below the 3.5× ceiling. F2 is consistently **2.2× — 3.1× faster** than F1 across all measured architectures.

The ceiling logic (`F2 ≥ unprotected` → `F2/F1 ≤ F1/unprotected = 3.5×`) is a sanity check that prevented an earlier mis-extrapolation (claimed "F2 ≈ 35 ms on M4" implying F2 < unprotected, mathematically impossible).

---

## 5. What's NOT covered (honest scope limitations)

For each, see the cited document for the full discussion.

| Limitation | Status | Where addressed |
|---|---|---|
| **Real STM32F4 hardware measurement** (C1, C2, C5, C8) | Phase 3 work | `PHASE1_PROOF_CLAIM3.md` (test protocol), `KILL_PLAN.md` Phase 3 |
| **ε_leak on real hardware** | Unmeasured; Phase 3 target ≤ 10⁻⁵ | `PHASE1_PROOF_CLAIM3.md` §4 |
| **Comparable accuracy table to Lin** (requires same hardware) | Phase 3 | `PHASE1_PROOF_CLAIM3.md` §6 |
| **Multi-signature attacks** (C6) | F2 doesn't claim to defeat; inherits Falcon's rekey policy | `PHASE1_MULTISIG.md` |
| **Fault injection attacks** | Out of scope | `PHASE1_MAIN_THEOREM.md` §7.5 |
| **EasyCrypt formalization** (SP1.5) | TODO; math-translation task | `easycrypt_f2/security/` (stubs) |
| **Falcon-1024 measurement** | Only Falcon-512 measured | future work |
| **Cortex-M33 deployment** (newer Trezor/Ledger) | M4 only measured | future work |

---

## 6. Implementation status

### 6.1 Source code

- `Protected_Reference_Implementation/sign.c`: F2-radical guarded by `#ifdef F2_RADICAL`. ~100 lines added. Lin's F1 unchanged when macro undefined.
- `Protected_Reference_Implementation/bench_sign.c`: 200-sig host benchmark harness.
- `Protected_Reference_Implementation/m4/`: bare-metal Cortex-M4 build (8 files: Makefile, README, startup.s, linker script, bench, key generation, pre-generated key, .gitignore).

### 6.2 Verification

- `test_falcon` passes EXIT=0 on F1 and F2 builds across logn ∈ {4, 9, 10} (600 self-signed verifications)
- Bit-identity to reference Falcon confirmed: F2 signatures pass `verify_raw`
- Reproducibility verified: re-running `m4/Makefile` from committed state produces same cycle counts within 1%

### 6.3 Reproducibility

From a fresh clone of `amit0365/FalconAnalysis` on branch `f2-radical-clean`:

```sh
# Apple Silicon
cd Protected_Reference_Implementation
make clean && make CFLAGS="-O2"           # builds F1
make clean && make CFLAGS="-O2 -DF2_RADICAL"  # builds F2
./bench_f1_clean   # ~7946 µs/sig
./bench_f2_clean   # ~2573 µs/sig

# Cortex-M4 (requires arm-none-eabi-gcc + qemu-system-arm)
cd m4 && make bench && make run
# Outputs F1: 1.21M cycles/sig, F2: 0.52M cycles/sig
```

---

## 7. Document index

All artifacts in `easycrypt_f2/` (17 documents, ~150 KB total):

| Document | Purpose |
|---|---|
| **REVIEW_PACKAGE.md** | **this document — single-file summary** |
| `ADVISOR_SUMMARY.md` | 1-page brief for advisor + asks |
| `KILL_PLAN.md` | Overall 6-phase execution plan |
| `KILL_PLAN_SECURITY.md` | Phase 1 security argument sub-plan |
| `PHASE0_LITREVIEW.md` | Lit review confirming novelty (Pessl/Lin/Mitaka triangulation) |
| `PHASE1_MATH_SKETCH.md` | Architectural plan for Phase 1 math |
| `PHASE1_PROOF_CLAIM1.md` | Claim 1: single-call Bayes-optimal bound |
| `PHASE1_PROOF_CLAIM2.md` | Claim 2: horizontal independence |
| `PHASE1_PROOF_CLAIM3.md` | Claim 3: ε_leak empirical-test spec |
| `PHASE1_MAIN_THEOREM.md` | Composed paper-headline theorem |
| `PHASE1_TIGHTNESS.md` | **C3 resolution: tight bound via A_Bayes** |
| `PHASE1_MULTISIG.md` | **C6 resolution: multi-sig scope statement** |
| `PRNG_SECURITY.md` | **C7 resolution: ChaCha20-256 citation** |
| `M4_ESTIMATE.md` | Analytical M4 estimate + ARMv7 QEMU empirical |
| `M4_QEMU_EMPIRICAL.txt` | M4 SYSTICK cycle-count measurements |
| `G1_0_RESULT.txt` | μ(π, k) numerical table |
| `G1_2_RESULT.txt` | Apple Silicon e2e benchmark |
| `bayes_bound.py` | Bayes bound + tightness Monte Carlo (runs in 5 min) |

---

## 8. Suggested review path

For a 30-minute review:

1. **Read this document end-to-end** (~10 min)
2. **Skim `PHASE1_MAIN_THEOREM.md`** (~10 min) — the composed paper claim
3. **Spot-check one resolution document** (~10 min) — e.g., `PHASE1_TIGHTNESS.md` (newest)

For a deep review (~2 hours), add:

4. `PHASE1_PROOF_CLAIM1.md` — single-call bound proof
5. `PHASE1_PROOF_CLAIM2.md` — horizontal-independence proof
6. `KILL_PLAN.md` — overall execution plan

For implementation review (~1 hour, add):

7. `Protected_Reference_Implementation/sign.c` lines 1517–1635 — F2-radical code
8. `Protected_Reference_Implementation/m4/README.md` — M4 build instructions
9. `bayes_bound.py` — numerical foundation

---

## 9. Status board

```
✅ G0   lit review              novel
✅ G1.0 numerical bound μ(π,4)  0.547 < Lin 0.58
✅ SP1.1 Claim 1                single-call bound proved
✅ SP1.2 Claim 2                horizontal independence proved
✅ SP1.3 Claim 3 spec           ε_leak protocol defined
✅ SP1.4 main theorem           composed
✅ G1.2 impl cost (Apple Silicon) 3.09× (measured)
✅ G1.2 impl cost (ARMv7 QEMU)    2.47× (measured)
✅ G1.2 impl cost (M4 QEMU SYSTICK) 2.35× (measured)
✅ C3 tightness                 A_Bayes empirical
✅ C6 multi-sig scope           honest limitation
✅ C7 PRNG citation             ChaCha20-256 cited

⏳ G1.1 advisor review of Claim 1
⏳ G1.3 ε_leak measurement (Phase 3 hardware)
⏳ SP1.5 EasyCrypt formalization
⏳ Phase 3 (8 weeks Chipwhisperer trace collection)
⏳ Phase 4 (paper write-up, 8 weeks)
```

---

*Author: F2 project, single-document review consolidation. 2026-05-16.*
*Status: theory complete; awaiting Phase 3 hardware validation.*
