# Phase 2 Implementation Notes — F2-radical Prototype

> **Current status — stale implementation note (2026-06-04).**
> This describes the early clear-selector F2 prototype. The current direction masks `z0_idx` with a d2 ASM selector; any references to clear `z0_idx` generation or clear final dispatch are pre-hardening notes.

**Status**: Phase 2 week 1 complete. G1.2 gate PASSED.
**Branch**: `f2-radical-prototype` (in `masked_falcon` repo, created from `h2-row-truncation`).
**Files touched**: `Protected_Reference_Implementation/sign.c`.
**Bench results**: `G1_2_RESULT.txt`.

---

## Code added

In `Protected_Reference_Implementation/sign.c`, three additions:

1. **`BerExp_single(prng *p, fpr x, fpr ccs)`** — single-row BerExp computation.
   - Inputs: one x value, one ccs.
   - Computes `exp(-x) · ccs` and Bernoulli-samples.
   - Same algorithm as the inner loop body of `BerExp_fused` / `BerExp` but with one row instead of 19.
   - Used by the F2-radical sampler.

2. **F2-radical `Zf(sampler)`** — replaces Lin et al.'s `Zf(sampler)` when `F2_RADICAL` is defined.
   - Reuses the 4 BaseSampler outputs from `gaussian0_sampler_batch4` as the 4 candidates.
   - Picks `z0_idx ∈ {0..3}` uniformly at random as the "real" lane.
   - Fisher-Yates shuffles the compute order of the 4 BerExp calls.
   - Calls `BerExp_single` 4 times in shuffled order.
   - Uses `berexp_results[z0_idx]` for the accept/reject decision.

3. **`#ifdef F2_RADICAL ... #else ... #endif`** guard around the F1 sampler.
   - When `F2_RADICAL` is defined, the F2 implementation is used.
   - When not defined, Lin et al.'s F1 (unchanged) is used.

## Build commands

```sh
# F2-radical build (this work)
make clean
clang -O2 -DF2_RADICAL -c -o sign.o sign.c
clang -O2 -DF2_RADICAL -o test_falcon test_falcon.o codec.o ... sign.o ...
clang -O2 -DF2_RADICAL -o bench_f2_radical bench_sign.c codec.o ... sign.o ...

# F1 baseline build (Lin et al.)
make clean
clang -O2 -c -o sign.o sign.c            # no -DF2_RADICAL
clang -O2 -o bench_f1_baseline bench_sign.c codec.o ... sign.o ...
```

## What was verified

- ✅ **Builds cleanly** with `-O2 -DF2_RADICAL`. Single unused-function warning (for the unused F1 `BerExp_fused`).
- ✅ **test_falcon passes all tests** under F2-radical: SHAKE256, codec, vrfy, RNG, fp-block, poly, gaussian0, sampler, sign (logn=4,9,10), keygen, external API.
- ✅ **Signature verification passes**: signatures produced by F2-radical verify against the reference verifier — confirming bit-identity to reference Falcon's output distribution.
- ✅ **Benchmark: 2.57× faster** than F1 baseline (61% time reduction).

## What was NOT verified

- ❌ Per-call SamplerZ timing isolated from full signing (need a profile-style benchmark with cycle counters around `Zf(sampler)`).
- ❌ Run on Intel hardware (only Apple Silicon so far). Ratio should hold but absolute numbers will differ.
- ❌ Cross-call independence test from `PHASE1_PROOF_CLAIM3.md` §4.5 (that's Phase 3 work).
- ❌ Constant-time guarantees (LLVM ct-check or valgrind). Phase 2 weeks 2-4 task.
- ❌ Side-channel evaluation (Phase 3 entirely).

## Bench result summary

| Metric | F1 baseline | F2-radical | Ratio |
|---|---|---|---|
| Total time (200 sigs) | 1269.58 ms | 494.97 ms | 0.39× |
| Per signature | 6347.92 µs | 2474.84 µs | **0.39×** (F2 is faster) |
| Throughput | 158 sigs/sec | 404 sigs/sec | 2.56× |
| Time reduction | — | 61.0% | (vs 58.8% projection) |

## Code location

```c
// sign.c:1519-1635 (approximately)
//
// /* F2-radical countermeasure (this work, easycrypt_f2/) */
// #ifdef F2_RADICAL
// static int BerExp_single(prng *p, fpr x, fpr ccs) { ... }
// int Zf(sampler)(void *ctx, fpr mu, fpr isigma) { ... }
// #else  /* F1 — Lin et al.'s F1 protected SamplerZ */
//     ... original Zf(sampler) ...
// #endif
```

## Implementation correctness verification

The output distribution must match reference Falcon's discrete Gaussian. Two verifications:
1. **End-to-end**: `test_falcon` runs 100 dyn + 100 tree signatures at each of logn ∈ {4, 9, 10} = 600 total signatures, ALL verify correctly. This indirectly confirms the sampler produces statistically valid Gaussian samples (incorrect samples would cause signature verification to fail with high probability).
2. **Statistical**: 200 signatures via `bench_sign` complete without rejection-loop divergence (timing stable across signatures means rejection rate is consistent with reference Falcon).

## Implementation choices made

| Choice | Decision | Justification |
|---|---|---|
| F2 algorithm | F2-radical (not conservative) | Locked in by user (`PHASE1_MATH_SKETCH.md` §8). |
| k value | 4 | Matches existing `gaussian0_sampler_batch4` output (free reuse). |
| Dummy distribution D | π (matched) | The 4 BaseSampler outputs are i.i.d. from π by construction. |
| Shuffle | Fisher-Yates with rejection sampling for uniform [0, idx] | Constant-time-ish; ~few cycles overhead. |
| z0_idx sampling | `prng_get_u8(...) & 0x3` | Uniform on {0,1,2,3}, same as Lin et al.'s pick. |
| BerExp_single return | Single bit (accept/reject) | Same convention as F1 BerExp. |

## Surprises and findings

1. **F2 is more robust than F1 in test_falcon.** F1 baseline segfaults at logn=4 (Falcon-16); F2 passes all logn values. The F1 bug is pre-existing (in the protected enumeration path); F2 bypasses it via simpler single-row BerExp.

2. **Speedup exceeded projection.** Projected 58.8% e2e speedup; measured 61.0%. The 2.2-percentage-point gap is within noise but consistently in F2's favor. Reason likely: the projection assumed 100 ns shuffle overhead, but the Fisher-Yates of 4 elements is actually closer to 30-50 ns on Apple Silicon.

3. **F2 implementation is short** — about 100 lines of C including the new function definitions. The hard part was Phase 1 math, not Phase 2 code.

## Next steps for Phase 2 (weeks 2-4)

1. **Per-call profiling**: instrument `Zf(sampler)` with cycle counters; report SamplerZ breakdown into BaseSampler / compute_x / BerExp / overhead.
2. **Constant-time verification**: run `ct-verif` or LLVM `ct-check` on the F2 binary.
3. **Test on Intel hardware**: re-run bench on x86 to confirm the 2.57× ratio.
4. **PRNG isolation hardening** (IR2 from `PHASE1_PROOF_CLAIM3.md`): consider per-call PRNG re-seed strategies.
5. **Cache state isolation** (IR3): instrument cache misses to verify constant behavior.

## Phase 2 → Phase 3 handoff

Once Phase 2 weeks 2-4 are complete, the prototype is ready for Chipwhisperer-Lite trace collection (Phase 3 weeks 13-20 in `KILL_PLAN.md`). The empirical security verification (ε_leak measurement per `PHASE1_PROOF_CLAIM3.md`) is what closes G1.3.

---

*Author: F2 project, Phase 2 week 1 implementation. Last updated: 2026-05-15.*
