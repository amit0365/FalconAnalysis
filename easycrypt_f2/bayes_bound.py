#!/usr/bin/env python3
"""
F2 Phase 1, week-1 deliverable.

Numerically compute μ(π, k) = Bayes-optimal multiset-predictor accuracy
for shuffling-with-dummies under Falcon's non-uniform half-Gaussian prior.

This is the *correct* replacement for the symmetric-crypto "1/k" bound;
see PHASE1_MATH_SKETCH.md §4 for derivation.

Mathematical content:
  Given a real z₀ ~ π and (k-1) dummies d_i ~ π i.i.d., the optimal
  adversary observes the multiset M = {z₀, d_1, ..., d_{k-1}} and
  outputs the Bayes-optimal estimator
      g(M) = argmax_v Pr[z₀ = v | M] = argmax_v c_v(M)
  where c_v(M) = #{i : M_i = v}, with ties broken by max π.
  Accuracy:
      μ(π, k) = E[c_{g(M)}(M) / k]

Numerical method:
  - k ≤ 5:  exact enumeration over 19^k tuples
  - k ≥ 6:  Monte Carlo with 10M samples (3-decimal precision)

Run:
    python3 bayes_bound.py
"""

import math
import sys
import random
from collections import Counter
from itertools import product
from pathlib import Path

# Pull π from the H2 precision artifact — same RCDT, single source of truth.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "easycrypt_h2" / "precision"))
from berexp_rows import prob_z0_equals, Z0_MAX, RCDT_ROWS  # noqa: E402

N_VALUES = Z0_MAX + 1   # 19


def make_pi():
    """Return π as a list of 19 floats, indexed by z₀ ∈ {0..18}."""
    return [prob_z0_equals(i) for i in range(N_VALUES)]


def bayes_optimal_guess(candidates, pi):
    """
    Bayes-optimal estimator for the real value given the observed multiset.
    Returns argmax_v c_v(M); ties broken by larger π(v).
    """
    counts = Counter(candidates)
    max_count = max(counts.values())
    best = [v for v, c in counts.items() if c == max_count]
    return max(best, key=lambda v: pi[v])


def mu_exact(pi, k):
    """Exact μ(π, k) by enumeration. Tractable for k ≤ 5."""
    total = 0.0
    for real in range(N_VALUES):
        p_real = pi[real]
        for dummies in product(range(N_VALUES), repeat=k - 1):
            candidates = [real] + list(dummies)
            g = bayes_optimal_guess(candidates, pi)
            if g == real:
                p = p_real
                for d in dummies:
                    p *= pi[d]
                total += p
    return total


def mu_monte_carlo(pi, k, n_samples=10_000_000, seed=42):
    """Monte Carlo estimate of μ(π, k). Used for k where exact is too slow."""
    random.seed(seed)
    indices = list(range(N_VALUES))
    correct = 0
    for _ in range(n_samples):
        real = random.choices(indices, weights=pi)[0]
        dummies = random.choices(indices, weights=pi, k=k - 1)
        g = bayes_optimal_guess([real] + dummies, pi)
        if g == real:
            correct += 1
    return correct / n_samples


def prior_floor(pi):
    """Trivial-adversary accuracy: always guess argmax π."""
    return max(pi)


def report():
    pi = make_pi()
    pi_max = prior_floor(pi)

    print("F2 Bayes-optimal predictor bound for Falcon-512 gaussian0_sampler")
    print(f"  π = (Falcon RCDT-derived PMF on {{0..{Z0_MAX}}})")
    print(f"  prior floor π(0) = max π = {pi_max:.6f}")
    print(f"  Lin et al. F1 measured accuracy: ~58% (Table 5, paper)")
    print()

    print(f"{'k':>3}  {'method':<10}  {'μ(π, k)':>10}  {'Adv = μ - π(0)':>16}  {'vs Lin 0.58':>13}")
    print("-" * 70)

    # k = 1 is the unprotected case: adversary always sees the real, accuracy = 1.
    print(f"{1:>3}  {'analytic':<10}  {1.0:>10.6f}  {1.0 - pi_max:>16.6f}  "
          f"{'(unprotected)':>13}")

    for k in [2, 3, 4, 5]:
        mu = mu_exact(pi, k)
        adv = mu - pi_max
        delta_lin = mu - 0.58
        flag = "  (beats Lin)" if mu < 0.58 else "  (worse than Lin)"
        print(f"{k:>3}  {'exact':<10}  {mu:>10.6f}  {adv:>16.6f}  {delta_lin:>+13.6f}{flag}")

    for k in [6, 8, 12, 16, 19]:
        mu = mu_monte_carlo(pi, k)
        adv = mu - pi_max
        delta_lin = mu - 0.58
        flag = "  (beats Lin)" if mu < 0.58 else "  (worse than Lin)"
        print(f"{k:>3}  {'MC 10M':<10}  {mu:>10.6f}  {adv:>16.6f}  {delta_lin:>+13.6f}{flag}")

    print()
    print("Interpretation:")
    print(f"  - 'μ - π(0)' is the info gain over the trivial prior-guess attacker.")
    print(f"    This is the actual security advantage of an optimal F2 adversary.")
    print(f"  - μ vs 0.58 compares F2(k) to Lin et al.'s measured protected accuracy.")
    print(f"    F2(k) is *security-equivalent or better* to Lin when μ(k) ≤ 0.58.")
    print()
    print("Cost-vs-security tradeoff (using Table 6 of paper for per-call cost):")
    print()
    print(f"{'k':>3}  {'BerExp calls/sample':>20}  {'projected ns/SamplerZ':>22}  {'e2e speedup':>12}")
    print("-" * 70)
    # F2-radical: per BerExp call is the UNPROTECTED cost (~573 ns from Table 6),
    # since each call does only 1 real row. With shuffle overhead, estimate 700 ns/call.
    BEREXP_UNPROT_NS = 573
    SHUFFLE_OVERHEAD_NS = 100  # PRNG + permutation per call (estimate)
    OTHER_SAMPLERZ_NS = 2400 - 573  # everything in SamplerZ except BerExp
    LIN_SAMPLERZ_NS = 14428
    T_OTHER_PER_SIG_NS = 2411  # derived from 3.5× overhead claim (see chat math)

    for k in [2, 3, 4, 6, 8, 19]:
        cost_per_call = BEREXP_UNPROT_NS + SHUFFLE_OVERHEAD_NS
        samplerz_ns = OTHER_SAMPLERZ_NS + k * cost_per_call
        # E2E projection: per-sig signing time
        total_protected_ns = T_OTHER_PER_SIG_NS + LIN_SAMPLERZ_NS   # Lin baseline
        total_f2_ns = T_OTHER_PER_SIG_NS + samplerz_ns
        speedup = (total_protected_ns - total_f2_ns) / total_protected_ns * 100
        print(f"{k:>3}  {k:>20d}  {samplerz_ns:>22.0f}  {speedup:>11.1f}%")

    print()
    print("Combined verdict for k = 4:")
    mu4 = mu_exact(pi, 4)
    samplerz4 = OTHER_SAMPLERZ_NS + 4 * (BEREXP_UNPROT_NS + SHUFFLE_OVERHEAD_NS)
    speedup4 = (T_OTHER_PER_SIG_NS + LIN_SAMPLERZ_NS - T_OTHER_PER_SIG_NS - samplerz4) / \
               (T_OTHER_PER_SIG_NS + LIN_SAMPLERZ_NS) * 100
    print(f"  - security: μ(π, 4) = {mu4:.4f}  (Lin: 0.58, trivial prior: {pi_max:.4f})")
    print(f"  - cost:     SamplerZ = {samplerz4:.0f} ns  (Lin: {LIN_SAMPLERZ_NS} ns)")
    print(f"  - e2e:      {speedup4:.1f}% speedup vs Lin et al.")
    print()

    if mu4 < 0.58:
        print(f"  ✓ F2(k=4) is strictly stronger than Lin et al. AND faster — thesis holds.")
    else:
        print(f"  ⚠ F2(k=4) accuracy {mu4:.4f} is WORSE than Lin's 0.58. Thesis at risk.")


if __name__ == "__main__":
    report()
