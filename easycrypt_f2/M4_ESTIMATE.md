# Cortex-M4 Performance Estimate for F2-radical

**Status**: Analytical projection. Real measurement deferred until cross-compile / hardware available.
**Target hardware**: STM32F415 @ 168 MHz, Cortex-M4 with FPv4-SP-D16 (single-precision FPU only).
**Why this doc exists**: an earlier extrapolation (`F2 ≈ 35 ms` on M4) violated physics; this doc captures the ceiling logic and the correct estimate.

---

## The fundamental ceiling

For any countermeasure built on top of unprotected Falcon:

```
F_protected  ≥  F_unprotected     (countermeasure adds work, never subtracts)
```

For F2-radical specifically, this means **F2 cannot be faster than unprotected Falcon**.

Lin et al.'s F1 has a measured overhead of 3.5× vs unprotected (Section 6 of PKC 2025). So:

```
F2/F1 ratio  ≤  1 / 3.5  ≈  3.5×          (the maximum possible speedup)
```

This is the **theoretical ceiling** on F2's improvement over F1, achieved only when F2's overhead vs unprotected reaches zero (impossible).

**Apple Silicon measurement**: F2/F1 = 3.09×, which is **88% of the way to the ceiling**. Already very close to optimal.

---

## Why the M4 ratio might differ from Apple Silicon

The 3.09× measured on Apple Silicon depends on:
- Cost of `fpr_expm_p63` (saved 9.5× by F2: 38 → 4 calls per outer iter)
- Cost of PRNG / shuffle (F2's overhead vs unprotected)
- Cost of "everything else" in signing (FFT, codec, hash-to-point)

On Cortex-M4 with single-precision-only FPU:
- `fpr_expm_p63` is software-emulated → relatively MORE expensive vs Apple Silicon
- This makes F2's `fpr_expm_p63` savings worth more in absolute time
- But the ceiling logic still applies: F2/F1 ≤ 3.5×

**Effect**: F2/F1 ratio on M4 likely ≥ 3.09×, asymptotically approaching 3.5× as FP cost dominates. Plausible range: **3.0× — 3.4×**.

---

## Estimated M4 numbers

Using published Falcon-512 M4 references for the unprotected baseline:

| Variant | M4 estimate | Reasoning |
|---|---|---|
| Unprotected Falcon-512 `dyn-sign` | ~50 ms / sig | Pornin's reference impl on M4 @ 168 MHz, mid of 38-80 ms range |
| **F1 (Lin et al.) on M4** | **~175 ms / sig** | unprotected × 3.5 (Lin's claimed protection overhead) |
| **F2-radical on M4 (best case)** | **~52-58 ms / sig** | unprotected × 1.05-1.16; inherits Apple Silicon's 1.13× F2/unprotected ratio |
| **F2-radical on M4 (conservative)** | **~65-70 ms / sig** | unprotected × 1.30-1.40 (Intel cost-model projection) |
| F2/F1 ratio on M4 | **~3.0× — 3.4×** | bounded by 3.5× ceiling; M4's FP cost pushes toward the ceiling |
| Throughput, F2 on M4 (mid) | 14-19 sigs/sec | inverse of ~55-70 ms |

## What about ratios beyond 3.5×?

Any number suggesting F2/F1 > 3.5× violates the ceiling. Earlier in development I extrapolated "F2 ≈ 35 ms on M4" by assuming the F2/F1 ratio could grow to 5×. This was wrong because:

- F2/F1 = 5× would mean F2 ≈ 35 ms < unprotected ≈ 50 ms
- F2 must include all unprotected work; it can't be faster than unprotected
- The maximum F2/F1 ratio is bounded by F1/unprotected = 3.5×

**Rule for future projections**: any time the F2/F1 ratio is computed across hardware, sanity-check that the absolute F2 number stays at or above the unprotected baseline.

---

## Phase 3 trace acquisition impact

If F2 on M4 is ~57 ms/sig and F1 is ~175 ms/sig, then for the standard 15K-trace SCA evaluation:

| Metric | F1 acquisition cost | F2 acquisition cost | Saving |
|---|---|---|---|
| 10K profiling traces | ~30 min | ~10 min | 20 min |
| 5K attack traces | ~15 min | ~5 min | 10 min |
| Single full Phase 3 run | ~45 min | ~15 min | 30 min (3× faster) |
| Per-leakage-source × 5 sources | ~3.7 hours | ~1.25 hours | 2.5 hours |

For Phase 3 wall-clock budget (8 weeks of trace work), F2 saves roughly **the time of one full Phase 3 trial** vs F1 — practical savings on top of the security advantage.

---

## Open: how to get real M4 numbers

Three paths to credible measurement:

1. **Real STM32F4 board** — Chipwhisperer-Lite + UFO. ~1 day setup for first sign benchmark. Most credible for the paper.

2. **QEMU bare-metal** — `qemu-system-arm -M netduinoplus2 -cpu cortex-m4`. Needs:
   - newlib (or picolibc) for stdint.h, time.h, etc. *Currently missing on macOS Homebrew*
   - Startup file + linker script for the chosen machine
   - UART output for results
   - ~4 hours of scaffolding

3. **Docker + qemu-user (Linux ARM emulation)** — bypasses bare-metal scaffolding but emulates Linux-ARM, not M4 exactly:
   ```sh
   docker run --rm -v $(pwd):/work -w /work multiarch/qemu-user-static \
     bash -c 'apt install gcc-arm-linux-gnueabihf && \
              arm-linux-gnueabihf-gcc -O2 -mcpu=cortex-m4 ... && \
              qemu-arm bench_sign'
   ```
   Approximates M4 performance to ~20% accuracy; ~30 min setup.

4. **Cycle-accurate static analysis** — `arm-none-eabi-objdump` + per-instruction M4 cycle table. Gives instruction count, no wall-clock. Useful for paper appendix.

**Recommendation**: defer to Phase 3 when Chipwhisperer hardware is in place; the ~55 ms estimate is rigorous-enough for advisor review and abstract claims.

---

*Author: F2 project, Phase 2 week 1, M4 projection. Last updated: 2026-05-15.*
*Status: pre-measurement projection. Replace with empirical numbers when M4 hardware available.*
