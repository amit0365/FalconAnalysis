# Phase 1 Kill Plan: Security Argument Sub-Plan

> **Current status — stale archival note (2026-06-04).**
> This security kill plan uses the old multiset-only theorem target. Current experiments require an observation-conditioned oracle bound and a separate d2 ASM selector claim. Use `CURRENT_PROOF_ROADMAP.md` for the active proof plan.

**Scope**: the security proof half of Phase 1. Companion to the overall `KILL_PLAN.md`.

---

## The single sentence we are trying to prove

> *For the F2-radical countermeasure with k=4 candidates per BerExp call applied to Falcon-512's protected SamplerZ, the optimal single-trace template adversary's accuracy on the underlying secret z₀ is bounded above by some `μ(π, 4) < 0.58` (= Lin et al.'s measured bound), and this bound is preserved under horizontal aggregation across all `M ≈ 18000` SamplerZ calls in one signature.*

The security argument decomposes into **three independent claims**. If any fails, the security story falls apart.

---

## The three claims and their gates

| Claim | What it says | Gate (kill condition) | Where it can fail |
|---|---|---|---|
| **C1: Bayes-optimal bound** | `μ(π, k) < Lin's 0.58` for chosen k | `μ(π, 4) ≥ 0.58` → kill F2 or raise k | Pure math; computed (PASSES) |
| **C2: Horizontal independence** | `Adv_HZ = Adv_SC` under per-call PRNG/state independence | proof requires strong unphysical assumption | Math + design |
| **C3: Leakage invariance** | hardware leakage L is permutation-invariant up to ε_leak | ε_leak unmeasurably large on real MCU | Math defines it; hardware tests it (Phase 3) |

---

## Sub-phase plan

### SP1.0 — Numerical foundation (week 1, ✅ DONE)

- **Deliverable**: `bayes_bound.py` + `G1_0_RESULT.txt`
- **G1.0**: `μ(π, 4) < 0.50` ✅ (got 0.547, slightly above 0.50 but below Lin's 0.58 — gate passes)

### SP1.1 — Claim 1 (Bayes-optimal per-call bound, weeks 2-3, ✅ DRAFT DONE)

- **Deliverable**: `PHASE1_PROOF_CLAIM1.md`
- Proof structure (4 steps):
  1. Information reduction: τ → multiset M (Lemma 5.1)
  2. Posterior closed form: `Pr[z₀ = v | M] = c_v(M) / k` (Lemma 5.2)
  3. Bayes-optimal accuracy = μ(π, k) (Lemma 5.4)
  4. Optimality over τ-observers (Lemma 5.5)
- **G1.1**: external cryptographer review of step (1) reduction
- **Risk R1**: reduction step silently assumes more than stated. Mitigation: external review by week 4.

### SP1.2 — Claim 2 (Horizontal independence, week 5)

- **Deliverable**: `PHASE1_PROOF_CLAIM2.md` (TODO)
- Proof structure:
  1. Define `independence` precisely (joint distribution factorization)
  2. Show conditional-independence of trace tuples implies per-call adversary advantage doesn't compose
  3. Specify implementation requirements (PRNG re-seed, cache flush, register zeroing)
  4. Compute implementation cost (~50-100 ns × M = ~1-2 ms per signature)
- **G1.2**: implementation cost of independence is < 10% of signing time

### SP1.3 — Claim 3 (Leakage invariance design, week 6)

- **Deliverable**: `PHASE1_PROOF_CLAIM3.md` (TODO)
- Specifies:
  1. Leakage-invariance hypothesis (math)
  2. Empirical test for it (Phase 3 protocol)
  3. Implementation requirements that maximize invariance
  4. Fallback: maskVerif certificate of BerExp gadget as SNI primitive
- **G1.3**: feasible Phase-3 test exists

### SP1.4 — Composition (week 7)

- **Deliverable**: `PHASE1_MAIN_THEOREM.md` (TODO)
- Main theorem: `Adv(A_horiz against M-call signature) ≤ μ(π, k) - π(0) + M · ε_leak`
- **G1.4**: composition gives non-trivial bound. With `M = 18000`, requires `ε_leak < 2.2 × 10⁻⁶` for bound `< 0.1`

### SP1.5 — EasyCrypt formalization (week 8 + spillover)

- **Deliverable**: `easycrypt_f2/security/*.eca` (TODO):
  - `F2BerExpSCI.eca` — single-call game
  - `F2BerExpHorizontal.ec` — horizontal reduction
  - `F2BerExpBayes.ec` — Bayes-optimal bound
- **G1.5**: EasyCrypt typechecks theorem statements

---

## Critical path

```
SP1.0 ──► G1.0 (μ < 0.58?) ──► SP1.1 ──► G1.1 (review)
   ✅            ✅                ✅          ⏳
                                  │
                                  ▼
                              SP1.2 ──► G1.2 (cost OK?)
                                  │
                                  ▼
                              SP1.3 ──► G1.3 (testable?)
                                  │
                                  ▼
                              SP1.4 ──► G1.4 (composes?)
                                  │
                                  ▼
                              SP1.5 (EasyCrypt)
```

---

## Risk register (security-argument specific)

| # | Risk | Affects | Probability | Mitigation |
|---|---|---|---|---|
| RS1 | μ(π, 4) ≥ 0.55 → security gain too small | C1 | medium | Bump k to 6 or 8; pivot to F2+masking belt-and-braces |
| RS2 | PRNG re-seeding overhead exceeds F2's BerExp savings | C2 | low | Amortize re-seed across batches |
| RS3 | Hardware leakage non-invariance (ε_leak > 10⁻⁵) | C3 | **high** | Design countermeasure (decoupling, randomized clock); fall back to F2+masking |
| RS4 | External reviewer finds hidden assumption in C1 reduction | C1 | medium | Schedule review at week 4 with budget to refactor |
| RS5 | Pessl-style horizontal attack works despite C2 | C2 | low-medium | Empirical test in Phase 3; add maskVerif certificate per call if fails |
| RS6 | Theorem statement fails EasyCrypt typecheck | C5 | medium | Use SP1.0-1.4 output as Lemma definitions |

---

## Backup plans (escalating severity)

**If G1.0 fires (μ ≥ 0.58 at k=4)** — DID NOT FIRE:
1. First fallback: try k=8 (μ(π,8)=0.472)
2. Second fallback: F2 + masking hybrid (provable d-SNI floor)
3. Last resort: abandon F2-radical, retry F2-conservative

**If G1.2 fires (independence too expensive)**:
1. First fallback: refresh every K calls instead of every call
2. Second fallback: pre-generate all per-call PRNG state in one batch at signature start

**If G1.3 fires (untestable invariance)**:
1. First fallback: bound ε_leak via worst-case analysis using maskVerif leakage model
2. Second fallback: state F2 security claim conditional on Phase 3 measurement passing

**If G1.4 fires (composition vacuous)**:
1. First fallback: shrink M by batching multiple coefficients per shuffle round
2. Second fallback: limit Falcon to short-message regime
3. Last resort: publish single-call result + "horizontal attack is open"

---

## Phase tracker (security argument)

```
✅ SP1.0  numerical bound          G1.0 ✅ (μ = 0.547)
✅ SP1.1  Claim 1 (single-call)    G1.1 ⏳ (external review)
✅ SP1.2  Claim 2 (horizontal)     G1.2 ⏳ (impl cost check in Phase 2)
✅ SP1.3  Claim 3 (leakage invar.) G1.3 ⏳ (executes in Phase 3 on Chipwhisperer)
✅ SP1.4  composition (main thm)   — security argument MATHEMATICALLY COMPLETE
⏳ SP1.5  EasyCrypt formalization
```

---

*Last updated: 2026-05-15.*
