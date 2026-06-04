# easycrypt_f2 Staleness Audit

Status: stale as of 2026-06-04.

This directory does not currently contain machine-checked EasyCrypt proofs. It contains proof sketches, planning notes, numerical scripts, and benchmark summaries. No `.ec` or `.eca` files exist under `easycrypt_f2/`.

## Current Verdict

The old proof target is no longer valid as the main F2 security claim:

```text
accuracy <= mu(pi, k) + epsilon
```

That target assumes the leakage trace reduces to the unordered candidate multiset, up to a single permutation-invariance error term. Current selector and integrated-proxy experiments show the observation model must be richer.

The proof target should be rewritten as an oracle-conditioned bound:

```text
accuracy <= BayesOracle(pi, k, O) + epsilon
```

where `O` explicitly models the observations available in the experiment, including some subset of:

- candidate multiset;
- accept vector;
- accept/reject event;
- selected/opened value;
- implementation leakage windows.

## Stale or Unsafe Claims

The following claims should not be reused without rewriting:

- `PHASE1_MAIN_THEOREM.md`: the paper-ready theorem bounding full traces by `mu(pi,k)+epsilon`.
- `PHASE1_PROOF_CLAIM1.md`: Lemma 5.1 / information reduction from trace to multiset.
- `PHASE1_PROOF_CLAIM2.md`: horizontal bounds that depend directly on the old Claim 1 target.
- `PHASE1_TIGHTNESS.md`: tightness of `mu(pi,k)` as a full-trace security bound.
- `ADVISOR_SUMMARY.md` and `REVIEW_PACKAGE.md`: claims that F2 is strictly stronger than Lin based only on `0.547 vs 0.580`.
- `G1_0_RESULT.txt`: conclusion that `F2(k=4)` is strictly stronger than Lin and faster.

These documents may remain useful as archival records of the earlier model, but they should not be treated as current proof state.

## Still Useful

The pure multiset calculation remains useful:

- `bayes_bound.py` computes `mu(pi,k)` for the idealized multiset-only game.
- The posterior formula `Pr[z0 = v | M] = count_M(v) / k` remains valid when the only observation is the multiset `M`.
- `mu(pi,k)` is still a valid baseline oracle component, not the final implementation security bound.

## Current Experimental Interpretation

The current evidence supports this narrower claim:

```text
Targeted d2 ASM masking removes direct z0_idx selector leakage in the ELMO selector/integrated proxy windows.
```

It does not yet prove:

```text
F2+d2 has Lin-equivalent or Lin-better z0_real leakage end-to-end.
```

The performance result currently supported by the ELMO proxy is:

```text
Lin protected BerExp path:      325,947 cycles
F2 BerExp4 + d2 selector path:   35,480 cycles
Speedup:                          9.19x
```

This is a protected-BerExp-path result, not automatically a full-signing result.

## Required Rewrite

Before any EasyCrypt formalization, rewrite the proof stack around these pieces:

1. `MultisetOracle`: pure `mu(pi,k)` bound, keeping the existing Bayes calculation.
2. `SelectorSecurity`: d2 ASM selector hides direct `z0_idx` leakage under tested windows.
3. `ObservationOracle`: formalizes `O = multiset + accept-vector/event + selected-value observations`.
4. `ExcessLeakage`: empirical statement comparing measured trace leakage against `BayesOracle(pi,k,O)`.
5. `Performance`: compares Lin protected BerExp path against F2 BerExp4 + d2 selector path.

Do not translate the current Markdown theorem into EasyCrypt. Formalizing it would formalize a stale claim.
