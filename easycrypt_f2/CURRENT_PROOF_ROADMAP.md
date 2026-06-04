# Current F2 Proof Roadmap

Status: current working roadmap as of 2026-06-04.

This file replaces the old proof narrative as the entry point for future formalization. The older `PHASE1_*` documents are archival until rewritten.

## Current Experimental Facts

The current ELMO proxy supports the following engineering facts:

1. A clear F2 selector leaks `z0_idx`.
2. Naive C masking of `z0_idx` leaks through control-flow and transition effects.
3. A stackless, branchless d2 ASM selector removes direct `z0_idx` leakage in selector-only and integrated-proxy windows.
4. Accept/reject conditioning can still improve posterior recovery when the accept vector is observable.
5. Opening the selected value leaks if that value encodes the selected lane.
6. The remaining unresolved target is `z0_real`, not `z0_idx`.

The current performance fact is:

```text
Lin protected BerExp path:      325,947 cycles
F2 BerExp4 + d2 selector path:   35,480 cycles
Speedup:                          9.19x
```

This supports a protected-BerExp-path performance claim, not a full end-to-end security claim.

## Claim A: Pure Multiset Oracle

Keep the original Bayes calculation, but scope it narrowly.

### Game

Sample:

```text
z0       <- pi
d1..d{k-1} <- pi
M        = multiset(z0, d1, ..., d{k-1})
```

The adversary observes only `M`.

### Theorem

For every value `v` appearing in `M`:

```text
Pr[z0 = v | M] = count_M(v) / k
```

Therefore the Bayes-optimal multiset-only success rate is:

```text
mu(pi,k) = E_M[max_v count_M(v) / k]
```

### Status

Valid. This is the part that `bayes_bound.py` still computes.

### Non-Claim

This does not bound implementation traces unless the trace observation is restricted to `M` or proven reducible to `M`.

## Claim B: Selector Security

### Target

Show that the d2 ASM selector removes direct leakage of the real-lane selector:

```text
z0_idx
```

### Evidence

Current ELMO selector/integrated-proxy tests show:

- clear selector: `z0_idx` recoverable;
- d2 ASM equality/selector: `z0_idx` recovery near oracle/noise baseline;
- random accept vectors: no extra direct selector recovery beyond conditioning;
- distinct selected values: leakage appears when the selected value is opened, not while selector shares remain closed.

### Formal Shape

The formal statement should not be:

```text
trace independent of z0_idx
```

It should be window- and observation-scoped:

```text
I(z0_idx ; Trace_selector | O_selector) <= epsilon_selector
```

where `O_selector` includes allowed public or modeled observations such as accept/reject event and accept-vector class.

### Status

Experimentally supported in the proxy. Not yet machine formalized.

## Claim C: Observation-Conditioned Oracle

The main security bound should be parameterized by an explicit observation variable `O`.

Examples:

```text
O_multiset      = M
O_accept        = M, A, event
O_value_open    = M, A, event, selected_z
O_window        = metadata visible in the chosen trigger window
```

For each observation model:

```text
BayesOracle(pi,k,O) = E_o[max_v Pr[z0_real = v | O=o]]
```

The empirical goal is then:

```text
Measured(trace -> z0_real) <= BayesOracle(pi,k,O) + epsilon_excess
```

This avoids overclaiming that `mu(pi,k)` remains the right target when accept-vector/event/value observations are present.

## Claim D: Excess Leakage

For each window and variant, report:

```text
excess_accuracy = measured_accuracy - oracle_accuracy
excess_MI       = measured_MI - oracle_MI
```

Required variants:

- Lin F1 protected path;
- F2 clear selector;
- F2 d2 ASM selector.

Required trigger windows:

- `candidate_generation`;
- `protected_berexp` / `berexp4`;
- `selector_dispatch` / return;
- `full_attempt`.

Required targets:

- `z0_idx`;
- `z0_real`;
- returned/selected `z`;
- accept vector where relevant.

Minimum experimental table:

| Variant | Window | `z0_real` measured | `z0_real` oracle | Excess | Interpretation |
|---|---|---:|---:|---:|---|
| Lin F1 protected path | each required window | TBD | TBD | TBD | baseline |
| F2 clear selector | each required window | TBD | TBD | TBD | shows unmasked selector/value leakage |
| F2 d2 ASM selector | each required window | TBD | TBD | TBD | decisive F2 result |

Decision rule:

| Result | Interpretation |
|---|---|
| F2 d2 `z0_idx` excess near zero | selector claim holds |
| F2 d2 `z0_real` excess comparable to Lin | F2 security/performance thesis plausible |
| F2 d2 `z0_real` excess much larger than Lin | F2 is a tradeoff or negative result |
| measured below oracle | classifier likely weak; do not claim security from accuracy alone |

## Claim E: Performance

The performance claim should be separated from security.

Currently supported:

```text
F2 BerExp4 + d2 selector is about 9.19x faster than Lin protected BerExp path in the ELMO proxy.
```

Not yet automatically supported:

```text
F2 is 9.19x faster for full signing.
```

Full-signing performance must be measured separately in the implementation being discussed.

## What Not To Formalize Yet

Do not formalize these old claims:

```text
accuracy <= mu(pi,k) + epsilon
F2(k=4) is strictly stronger than Lin because 0.547 < 0.580
trace information reduces to multiset M
```

Those statements are too coarse for the current implementation evidence.

## Next Formalization Order

1. Formalize the pure multiset posterior theorem.
2. Define an abstract observation variable `O`.
3. Define `BayesOracle(pi,k,O)`.
4. Prove that the multiset theorem is the special case `O = M`.
5. Add empirical obligations for `epsilon_selector` and `epsilon_excess`.
6. Only then map F2 implementation windows to specific `O` values.
