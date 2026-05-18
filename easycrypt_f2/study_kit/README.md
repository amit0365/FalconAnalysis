# Level 1 Study Kit: SCA Foundations for F2-radical

**Goal**: build the Bayesian + side-channel-analysis foundation needed to evaluate F2's claims.

**Total time**: 1.5–2 hours focused reading. After this kit, you'll have the vocabulary and math to read Lin et al. PKC 2025, Pessl 2016, Azouaoui 2022, and our `PHASE1_PROOF_CLAIM1.md` fluently.

---

## What's in this kit

```
study_kit/
├── README.md                       (this file — your guided tour)
├── chari_template_2002.pdf         (16 pages, 589 KB)
├── bishop_prml.pdf                 (758 pages, 17 MB — read only §1.5)
├── standaert_unified_2009.pdf      (32 pages, 1.1 MB)
└── tvla_methodology.pdf            (free SCA evaluation tutorial, optional)
```

All four downloaded from open sources (Microsoft Research / IACR ePrint / Springer open access).

---

## Reading plan (ordered, ~90 minutes total)

### 📖 Reading 1: Chari, Rao, Rohatgi. "Template Attacks." CHES 2002 (30 minutes)

**File**: `chari_template_2002.pdf` (16 pages, 589 KB)

**What you're learning**:
- What a "side-channel sample" / "trace" actually is
- How an attacker can use ONE trace + chosen-input profiling to recover a secret
- Why Bayesian classification is the optimal attack
- The multivariate Gaussian noise model

**Sections to focus on**:

| Section | Pages | Time | What to take away |
|---|---|---|---|
| Abstract + §1 Introduction | 13–14 | 5 min | Why "template attacks are the strongest form of SCA possible in an information-theoretic sense" |
| §2 Theory | 15–16 | 10 min | The maximum-likelihood attack. Key sentence: "The best guess is to pick the operation such that the probability of the observed noise in S is maximized." |
| §2.1 Multivariate Gaussian Model | 16–17 | 10 min | The Gaussian template formula (Eq. 1). This is what Lin et al. and Phase 3 use. |
| §3 RC4 application | optional | skip | Concrete attack example; useful but not needed for F2 |

**After this reading you should be able to**:
- Define what a "template" is (mean signal + noise covariance per operation)
- Explain why an attacker prefers max-likelihood over averaging
- Recognize Eq. (1) — multivariate Gaussian noise PDF — when it appears elsewhere

**Connection to F2**: Lin et al. PKC 2025 uses exactly this template-attack methodology to measure 58% accuracy on their F1. Our Phase 3 plan uses the same setup on Chipwhisperer. The "ε_leak" in our Theorem C1 is precisely the residual leakage that survives a template attack.

---

### 📖 Reading 2: Bishop, "Pattern Recognition and Machine Learning" §1.5 (30 minutes)

**File**: `bishop_prml.pdf` (full textbook; jump to §1.5 only — **pages 38–45**)

**What you're learning**:
- The mathematical justification for "argmax of posterior" as optimal classification
- Why Bayes' theorem gives the right answer
- Decision-theoretic optimality

**Sections to focus on**:

| Section | Pages | Time | What to take away |
|---|---|---|---|
| §1.5 Decision Theory (intro) | 38–40 | 10 min | The classification problem: given observation, output a guess. Optimal strategy minimizes expected error. |
| §1.5.1 Minimizing the misclassification rate | 39–41 | 15 min | **Key result**: argmax_v P(class = v \| x) is optimal. This is the "MAP estimator" theorem F2's Lemma 5.2 uses. |
| §1.5.4 Inference and decision | 42–45 | 5 min | The three approaches (generative, discriminative, discriminant). Template attacks are generative. |

**After this reading you should be able to**:
- State the Bayes-optimal decision rule for classification
- Explain why ties in the posterior don't affect expected accuracy
- Recognize when a problem is "Bayesian classification"

**Connection to F2**: Our Lemma 5.2 says `Pr[z₀ = v | M] = c_v(M)/k`. By Bishop §1.5.1, the optimal guess is argmax_v of this posterior — which is just "pick the most-frequent value." That's the 3-line `bayes_optimal_guess` function in our `bayes_bound.py`.

---

### 📖 Reading 3: Standaert, Malkin, Yung. "A Unified Framework for the Analysis of Side-Channel Key Recovery Attacks." EUROCRYPT 2009 (~30 minutes)

**File**: `standaert_unified_2009.pdf` (32 pages, 1.1 MB)

**What you're learning**:
- The standard SCA evaluation framework (mutual information + success rate)
- How to bound an attack's success probabilistically
- Where the "data complexity" notion comes from

**Sections to focus on**:

| Section | Pages | Time | What to take away |
|---|---|---|---|
| Abstract + §1 Intro | 1–3 | 5 min | The two metrics: success rate (SR) and guessing entropy (GE). These are the "outputs" of SCA evaluation. |
| §3 The Framework | 6–10 | 15 min | Definitions of leakage random variables, target intermediate value. Notation used by every subsequent SCA paper (including Azouaoui 2022). |
| §4 Information-Theoretic Metrics | 10–14 | 10 min | Mutual information `MI(K; L)` between key and leakage. Why `MI` determines data complexity. |
| Rest | optional | skip | Application examples and proofs |

**After this reading you should be able to**:
- Read "MI(Y; L)" and understand it as "mutual information between secret and leakage"
- Distinguish "data complexity" (number of traces) from "per-trace accuracy"
- Recognize the Bayes-optimal classifier in their framework

**Connection to F2**: This is the framework Veyrat-Charvillon 2012 and Azouaoui 2022 build on. Their "data-complexity bounds" use MI notation from this paper. Our μ(π, k) is a different metric (per-trace accuracy of optimal classifier) but uses the same probabilistic vocabulary.

---

### 📖 Optional Reading 4: TVLA Methodology (15 minutes)

**File**: `tvla_methodology.pdf` (Becker et al., eprint 2016/517 or similar)

**What you're learning**: How real SCA evaluation labs use Welch's t-test to detect leakage. Phase 3 will use TVLA on Chipwhisperer.

**Why optional**: theoretical work for F2 doesn't require TVLA. Read only if you want to understand what Phase 3 measurement actually looks like in practice.

---

## After Level 1: where to go next

You're now equipped for Level 2 (Falcon + Lin et al.):

1. Read **Lin et al. PKC 2025** §3 (samplers + leakages) — `~/Desktop/masked falcon.pdf`
2. Read **Lin et al. PKC 2025** §6.1 Algorithm 6 (the F1 countermeasure)
3. Read **Lin et al. PKC 2025** Table 5 (the 0.58 baseline)

See `../REVIEW_PACKAGE.md` §8 ("Suggested review path") for the full sequence.

---

## Vocabulary check

After Level 1, you should recognize these terms:

| Term | Means | Where it appears in F2 |
|---|---|---|
| Trace τ | The power waveform from one cryptographic operation | F2 Theorem C1: `Pr[A(τ) = z₀]` |
| Template | Mean signal + noise covariance per operation | Phase 3 protocol |
| MAP estimator | argmax_v of the posterior | F2 `bayes_optimal_guess` |
| Posterior P(secret \| obs) | Bayes-derived belief about secret given observation | Lemma 5.2: P(z₀=v \| M) = c_v(M)/k |
| Mutual information MI(Y; L) | Information about secret in leakage | Implicit in our ε_leak bound |
| Success rate (SR) | Probability attacker wins | Our μ(π, k) is the optimal-attacker SR |
| Guessing entropy (GE) | Expected guesses to find secret | Different from our per-trace bound, but related |

---

## What was NOT included and why

| Not included | Reason | Free alternative |
|---|---|---|
| **Mangard, Oswald, Popp. "Power Analysis Attacks" textbook (2007), Ch. 4-5** | Copyrighted; can't redistribute | Standaert-Malkin-Yung 2009 covers the same material |
| **Bishop full textbook, all chapters** | Only §1.5 is needed; reading the rest is great for ML in general but not for F2 | (Section 1.5 only) |
| **Quisquater & Samyde 2001, Kocher 1999** | Foundational SCA but predates Bayesian framework; superseded for our purposes | Chari 2002 cites them |

---

*Author: F2 project, Level 1 study kit. Last updated: 2026-05-18.*
*All PDFs downloaded from open access sources.*
