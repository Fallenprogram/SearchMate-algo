# Final submission and closed research window

**Internal v39-01 is the user-confirmed final competition submission. Further development stopped at the user's request on 11 September 2026.** The original goal of eliminating all major weaknesses was not achieved; no later build is recommended or queued.

[Exact final source, model, assets and ZIP](releases/final-internal-v39-01/README.md) · [Latest rated observations](rated-results/UPDATE_2026-09-11.md) · [Current state](CURRENT_STATE.md)

## Release lineage and evidence

V37 was the last broadly qualified combined build against submitted v16.1: **13.5/16 short points and 7.5/8 full-clock points**, zero candidate faults and passed exact-package checks. It uses the original CPU-trained residual described in its [model card](releases/competition-v6-internal-v37-01/MODEL_CARD.md). Its earlier neural-only and other failed studies remain historical failures; the result cannot be attributed to one component or to memory alone.

V38 added the bounded two-bishop-versus-king tablebase repair. Exhaustive defending-reply checks completed for four roots over 515 states, with 23/11-ply maximum proof paths for earlier/later roots. All 51 winning seeded cases converted; 13 drawn cases remained drawn. V38's two full-clock smoke games were 2W/0D/0L. This was a maintenance gate, not an additional strength campaign.

V39 then repaired the premature fifty-move draw shortcut demonstrated in round 99. It selects Nb6 in the original-clock trials; all 19 opposing replies reach the observed draw boundary. R97 defense stayed unchanged. Its two clean smoke games against v38 scored **0W/1D/1L**; targeted checks and exact-package checks passed. V39 inherits the original model and both covered endgame selectors unchanged. These narrow maintenance results do not establish that v39 reproduces v37's local match score or solves every loss.

The earlier dated [11 September update](PROGRESS_2026-09-11.md) is a preserved v37-era snapshot. This record supersedes its pending next-action and current-submission statements.

## Later experiments retained as unsuccessful

All scored follow-ups compared their frozen candidate with exact v39. Their mandatory short gate was 12/16 points, followed by 6/8 full-clock points. A mathematically unreachable short gate stopped play; no thresholds were lowered. None reached its full-clock screen or produced a qualified replacement ZIP.

| Internal study | Focus | Outcome |
|---|---|---|
| v40 | Shallow checked-node extension | 6W/2D/4L, 7/12; short gate unreachable |
| v41 | PV-only check extension | Target decision unchanged; no games |
| v42 | Queen-present check extension | 1W/3D/3L, 2.5/7; short gate unreachable |
| v43 | Wider original CPU neural residual | Assessment MAE worsened 0.323%; no games |
| v44 | Capture/pawn-check extension | 1W/0D/5L, 1/6; short gate unreachable |
| v45 | Quiet queen-pin threat in quiescence | Target decision unchanged; no games |
| v46 | Additional checks against an advanced king | 0W/3D/3L, 1.5/6; short gate unreachable |
| v47 | Precomputed identical hash constants | Technical equivalence passed; target decision unchanged; no games |
| v48 | Iteration forecast using two-depth growth | 3W/3D/3L, 4.5/9; short gate unreachable |

[Machine-readable outcomes and source/review hashes](studies/final-window-v40-v48.json). Raw private studies, failed attempts and receipts remain local; unreleased sources and models are not in the final submission.

The strongest selected-position lead was v48. The first six iterations matched v39 in moves, scores and nodes; revised forecasting allowed a seventh iteration to complete within the same request cap. It selected **Qc5** in both round-103 move-35 trials, with a matched reference estimate of **-35 instead of -726 cp**. Nevertheless, its short match result failed the fixed gate, and an earlier move-32 weakness remained. A proposed separate maintenance review was not executed; the user chose final v39 and stopped work. Selected-position progress was real evidence for a mechanism, but insufficient evidence for a stronger overall replacement.

## Research memory and unresolved questions

- **M1-P001:** preserve exact identities, startup/reset/timing and cleanup records. Retain observer or controller failures and distinguish their correction from player changes or retries.
- **M1-P002:** separate model error, nodes, selected-position quality, targeted maintenance and competitive results. A local diagnostic improvement cannot substitute for the frozen game gate.
- **M1-P003:** retain negative outcomes, winning/drawing controls and unresolved alternatives. Trace the continuation before claiming a cause; do not infer an evaluation defect merely because longer search fails.

Recuris is the record of retrieved evidence and changed decisions. No controlled memory-versus-no-memory comparison was performed, so a causal strength benefit is unmeasured. The engine does not automatically learn new weights from rated wins.

Remaining weaknesses include exposed-king defense, quiet coordination threats and some long tactical continuations. The original training sample and small runtime model have limitations. Endgame selectors cover specific material classes and retain fallback cases. Local timing and the platform differ. The final engine is frozen; these are recorded open questions, not instructions to start another campaign.
