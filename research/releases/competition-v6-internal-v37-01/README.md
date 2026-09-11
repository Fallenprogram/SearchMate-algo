# Competition upload v6 / internal v37-01

**Locally qualified against exact v16.1.** This record preserves the tested CPU engine, original model, release archive and qualification evidence. The [v16.1/internal v16-01 archive](../competition-v5-internal-v16-01/README.md) remains available as the rollback reference.

[Download the exact reviewed ZIP](SearchMate-next-submission-internal-v37-01.zip). Its original filename is preserved even though the platform attempt is labelled v6.

ZIP SHA-256: `6cdee0bee1f877e5af1df0aa19b2444cfebc5163515872debb33c53b8cc8ecd3`

Source SHA-256: `e93e1b7a788cdd92237853621c219fab2c1d14fd85d5e034dd09b0c1c6e46953`

Model SHA-256: `c3c9b7f815e920c88d87974b8a0f63b66c0527c9b52525040ab7b0f20c0b7263`

| Local screen versus exact submitted v16.1 | W / D / L | Points | Required |
|---|---:|---:|---:|
| 16 games, 10s + 0.1s | 12 / 3 / 1 | **13.5/16** | 12/16 |
| 8 games, 120s + 0.5s | 7 / 1 / 0 | **7.5/8** | 6/8 |

Zero recorded faults; 3,004 played plies passed the recorded legality audit. All scheduled games completed. Sources, openings, order and criteria were frozen before scoring; there were no scored retries or source changes. Short games used validated warmed processes with new referee history/clocks. Full games used fresh processes. [Game records](games.json) link all 24 unchanged PGNs. Results are finite release screens after many candidate attempts; they do not establish Elo, predict ladder win rate, or isolate any single component's contribution.

## Build and model

The original Numba engine now combines a small CPU-trained neural residual, guarded late-move reductions, exact caching of its own runtime static evaluations, a revised iteration forecast, and reversible-history score-table context. The incremental change from v36 only removes in-search history preceding the latest capture/pawn move from the score-table context; relevant reversible history, halfmove counters, depth/bounds and mate normalization remain. The inherited KQK selector and verified assets are unchanged.

The 592-parameter model is our original eight-unit residual, not an imported chess network. It was fitted on CPU and evaluated by Numba; the original `evaluation.npz` ships in the ZIP. [Model card](MODEL_CARD.md), [training recipe](training-recipe.json), [historical accuracy](model-accuracy.json), and [readable player](player/agent.py) explain the design. Teacher engines, answer corpora and training data are not included in the package. The runtime cache starts empty and stores only values computed by the player itself, with full board/side equality checks.

## Package evidence and limits

Exact-archive checks passed locally: root layout, CRC and source/model/asset hashes; offline loading and dependency review; cold import; persistent requests; four inherited KQK roots; fixed 250/100/50/10-ms legal replies; memory and cleanup. V37 imported in 28.593s and peaked at 263.836 MiB job memory, versus 20.689s / 216.644 MiB for the contemporary v16 comparison. Ten requests per source passed. [Evidence summary](evidence-summary.json) preserves precise measurements and verification scope.

The original package controller stopped on a static cleanup-schema reader error before any archive or package API call. A separate continuation verified the frozen writer's process-exit semantics and completed the first package checks within the original deadline. No player, scored result or admission standard changed and no measured attempt was repeated.

R82's defensive choice remains unresolved. A two-bishop conversion failure observed in v36 has not been specifically repaired or proved absent in v37. Low-clock KQK checks establish legal, timely replies, not conversion guarantees. Existing referee draw/ply-policy interpretation and local hardware/timing differences remain limitations. Actual platform validation and review are still required.

## Verify and use

```sh
python research/releases/competition-v6-internal-v37-01/verify_artifacts.py
```

This verifies archive/payload/rollback hashes and Python syntax without importing either engine or running games. Upload the named ZIP unchanged; root `make zip` still builds historical v0. [Release manifest](release.json) records identities and rollback. Tablebase redistribution information is in [TABLEBASES.txt](player/TABLEBASES.txt).

The user performs uploads and confirms acceptance. Recuris supports the evidence and decision record; its causal strength benefit remains unmeasured. Private runtime logs, machine paths, bulk corpora, reference tools and sealed inputs remain outside this publication.
