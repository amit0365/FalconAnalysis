# Study Plan: SCA Foundations + F2-Radical Verification (4-level ladder)

**Goal**: build the Bayesian + side-channel-analysis foundation needed to evaluate F2's claims, then read Lin et al. PKC 2025, the shuffling literature, and our F2 docs fluently.

**Total time**: ~6-8 hours focused reading. Spread over a week or follow the 10-day daily schedule at the bottom.

**Structure**: 4 levels, each builds on the previous.
- **Level 1** (~1.5 h): SCA basics — what is a trace, why Bayes shows up, MAP estimator
- **Level 2** (~2 h): Falcon + Lin et al. — what F2 protects, what F1 does
- **Level 3** (~2 h): Shuffling framework — existing theory we generalize
- **Level 4** (~2 h): F2 itself — read our claims with full context

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

Levels 2-4 reference materials NOT in this kit — see each level for where to find them.

---

# Level 1: SCA basics (~1.5 hours)

You need to understand **what a template attack is** and **why Bayes shows up in SCA**.

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

### 📖 Reading 3: Mangard, Oswald, Popp. "Power Analysis Attacks" Ch. 4 §4.5 (30 minutes)

**File**: not in this kit (copyrighted textbook, 2007). If you have access via your library, read Ch. 4 §4.5 "Statistical Methods" (~30 pages). Otherwise use **Standaert-Malkin-Yung 2009** as a free substitute (see Optional Reading below).

**What you're learning**:
- SNR, hypothesis testing, Hamming-weight model
- The vocabulary of "leakage" beyond template attacks
- Foundational concepts every SCA paper assumes

**Sections to focus on**:

| Topic | Time | What to take away |
|---|---|---|
| Signal-to-Noise Ratio (SNR) | 10 min | How "leakage strength" is quantified. SNR = var(signal) / var(noise). |
| Hypothesis testing on traces | 10 min | t-tests, correlation. The basis of TVLA. |
| Hamming-weight / Hamming-distance models | 10 min | The standard leakage abstraction. Used in every SCA paper. |

**Connection to F2**: Phase 3 reports SNR per leakage source. Lin et al. Table 5 implicitly uses an HW model. Recognizing "the bus leaks HW(addr)" or "the register leaks HW(value)" is essential vocabulary.

---

### 📖 Optional Reading 4: TVLA Methodology (15 minutes)

**File**: `tvla_methodology.pdf` (Becker et al., eprint 2016/517 or similar)

**What you're learning**: How real SCA evaluation labs use Welch's t-test to detect leakage. Phase 3 will use TVLA on Chipwhisperer.

**Why optional**: theoretical work for F2 doesn't require TVLA. Read only if you want to understand what Phase 3 measurement actually looks like in practice.

---

**After Level 1 you can read the rest with proper vocabulary**: "trace," "template," "posterior," "MAP estimator," "SNR."

---

# Level 2: Falcon and Lin et al. (~2 hours)

Now learn **what F2 is protecting** and **what Lin et al. PKC 2025 (F1) does**.

| Read | Section | Time | Key takeaway |
|---|---|---|---|
| **Falcon spec (Pornin et al. 2020 NIST submission)** | §3.9 "Sampler over the integers" | 30 min | What `gaussian0_sampler` is, what z₀ is, what the RCDT table encodes. |
| **Falcon spec** | Algorithm 11 (SamplerZ pseudocode) | 15 min | The actual algorithm being protected: BaseSampler + BerExp + reject loop. |
| **Lin, Zhang, Yu, Wang. PKC 2025 (eprint 2025/351)** | §3 "Falcon's Integer Gaussian Samplers and Their Leakages" | 30 min | What sources of leakage exist (5 of them). Why z₀ leaks. |
| **Lin et al. PKC 2025** | §6.1 "Countermeasures" + Algorithm 6 | 30 min | The F1 algorithm: 19-row constant-time enumeration. This is what F2 replaces. |
| **Lin et al. PKC 2025** | §6.2 Table 5 | 15 min | The 0.58 baseline accuracy. Where the number we beat comes from. |

**Where to find materials**:
- Falcon spec: `https://falcon-sign.info/falcon.pdf` (NIST PQC submission, public)
- Lin et al. PKC 2025: `~/Desktop/masked falcon.pdf` (local copy) or `eprint.iacr.org/2025/351`

**After Level 2 you can read the F2 sign.c diff and follow it**: F1 vs F2 are the `#ifdef F2_RADICAL` switch.

---

# Level 3: Shuffling framework (~2 hours)

Now learn **how existing papers analyze shuffled SCA**.

| Read | Section | Time | Key takeaway |
|---|---|---|---|
| **Veyrat-Charvillon, Medwed, Kerckhof, Standaert. ASIACRYPT 2012** | §1 (intro) + summary in §5-6 | 30 min | The standard data-complexity bound for shuffled AES (uniform secret). Bayesian framework for shuffled SCA. |
| **Azouaoui, Bronchain, Grosso, Papagiannopoulos, Standaert. TCHES 2022(2) (eprint 2021/951)** | §2.1-2.2 (notations + IT metrics) | 30 min | The masking + shuffling framework. Read Eq. (4) carefully — the uniform-Y assumption we generalize. |
| **Pessl. INDOCRYPT 2016 (eprint 2017/033)** | §1, §3, §5.4-5.5 | 45 min | The cautionary tale on BLISS polynomial shuffling. §5.5 is the closest math neighbor — read carefully. |
| **(Optional) Standaert, Malkin, Yung. EUROCRYPT 2009** | §1-2 | 15 min | The "unified framework" for SCA. Defines mutual information vs success rate. (Free substitute for Mangard textbook in Level 1.) |

**Where to find materials**:
- Veyrat-Charvillon 2012: `https://perso.uclouvain.be/fstandae/PUBLIS/121.pdf`
- Azouaoui 2022: `eprint.iacr.org/2021/951`
- Pessl 2016: `eprint.iacr.org/2017/033`
- Standaert-Malkin-Yung 2009: in this kit as `standaert_unified_2009.pdf`

**After Level 3 you understand**: why existing bounds assume uniform secrets, why Pessl's BLISS attack matters, what's missing for Falcon (non-uniform π).

---

# Level 4: F2 itself (~2 hours)

Now read **our F2 claims** with full context.

| Read | Section | Time | Key takeaway |
|---|---|---|---|
| **`easycrypt_f2/REVIEW_PACKAGE.md`** | All | 20 min | Single-page summary of everything F2 claims |
| **`easycrypt_f2/PHASE1_PROOF_CLAIM1.md`** | §1-5 (theorem + lemmas) | 45 min | The main bound. Lemma 5.2 (posterior `c_v(M)/k`) is the load-bearing math. |
| **`easycrypt_f2/PHASE1_PROOF_CLAIM1.md`** | §10 (novelty discussion) | 20 min | The verified novelty position — why F2's bound is distinct from prior work. |
| **Run `bayes_bound.py --tightness`** | (5 min runtime) | 10 min reading output | Empirical evidence that the bound is tight. |
| **`easycrypt_f2/PHASE1_PROOF_CLAIM2.md`** | §1-4 (per-call rate) | 25 min | The horizontal independence theorem. Why the per-call bound carries to M-call signatures. |
| **`easycrypt_f2/PHASE1_PROOF_CLAIM2.md`** | §6 (implementation requirements IR1-IR7) | 15 min | Why per-call independence requires specific implementation discipline. |

**After Level 4 you can verify F2's claims line-by-line against the prior work and our novel contributions.**

---

## ★ Insight notes

- **Level 1 is the most important investment.** If template attacks and Bayesian decision theory don't click, nothing in Levels 2-4 will. Spend the full hour on Chari 2002 + Bishop §1.5 if needed; the ROI is huge.
- **Level 3 is the differentiator.** Most people who claim to "know SCA" stop at Level 2 (Falcon + Lin). Reading Veyrat-Charvillon + Azouaoui + Pessl is what makes you actually qualified to evaluate F2's novelty.
- **Don't skip Pessl §5.5.** It's the single closest prior result to our Lemma 5.2. If you understand the difference between Pessl's attacker-side likelihood matrix and our defender-side accuracy bound, you've understood F2's core contribution.
- **You can run `bayes_bound.py` BEFORE reading PHASE1_PROOF_CLAIM1.md.** Seeing the numbers (μ(π, 4) = 0.547, empirical = 0.546) makes the theorem more concrete. The math is what the program is computing, not the other way around.
- **Skip the Bishop reading if you already know MAP estimation**. The Chari 2002 paper covers enough Bayesian SCA to follow F2's argument.

---

## Suggested daily schedule (10 days, ~30 min/day)

| Day | Read | Time |
|---|---|---|
| 1 | Chari 2002 §1-3 | 30 min |
| 2 | Bishop §1.5 + Mangard 4.5 | 30 min |
| 3 | Falcon spec §3.9 + Alg 11 | 45 min |
| 4 | Lin §3 + §6.1 (Alg 6) | 45 min |
| 5 | Lin §6.2 Table 5 + Veyrat-Charvillon §1 | 30 min |
| 6 | Azouaoui §2.1-2.2 (Eq. 4!) | 30 min |
| 7 | Pessl §1, §3, §5.4-5.5 | 45 min |
| 8 | F2 REVIEW_PACKAGE.md + run bayes_bound.py | 30 min |
| 9 | PHASE1_PROOF_CLAIM1.md §1-5 | 45 min |
| 10 | PHASE1_PROOF_CLAIM1.md §10 + PROOF_CLAIM2.md §1-4 | 45 min |

By day 10 you can evaluate every F2 claim with the proper context.

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

*Author: F2 project, 4-level study plan. Last updated: 2026-05-26.*
*Level 1 PDFs in this kit; Levels 2-4 reference external materials.*
