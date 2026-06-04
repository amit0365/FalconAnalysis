# easycrypt_f2

This directory is an archival proof workspace for the F2-radical security argument.

Read this first:

- `STALE_AUDIT.md` — identifies stale claims and why the old proof target should not be formalized.
- `CURRENT_PROOF_ROADMAP.md` — current replacement roadmap for the proof and experimental claims.
- `bayes_bound.py` — still-valid pure multiset Bayes calculation.

## Current Status

No machine-checked EasyCrypt proofs currently exist in this directory. The older Markdown files are proof sketches and planning notes, not verified `.ec` / `.eca` artifacts.

The old headline theorem

```text
accuracy <= mu(pi, k) + epsilon
```

is stale for the implementation-level F2 claim. It ignores observations that current experiments show matter: accept-vector information, accept/reject event conditioning, selected-value opening, and implementation leakage windows.

The current proof direction is oracle-conditioned:

```text
accuracy <= BayesOracle(pi, k, O) + epsilon
```

where `O` explicitly records what the adversary is allowed to observe.

Do not translate the old Markdown theorem into EasyCrypt without first rewriting the theorem statement.
