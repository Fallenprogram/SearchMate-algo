# Study chronology and unsuccessful experiments

This is an index of the development history, not a ladder ranking of versions. “Failed” means the declared screen was not satisfied; “incomplete” means the work did not yield a valid completed qualification. A later study can ask a new question about unchanged code without erasing an earlier failure. See the [retrospective](../RETROSPECTIVE.md) for mechanisms and interpretation.

## Early classical and compiled work

| Internal study | Recorded outcome |
|---|---|
| v0 | Setup campaign 108W/10D/2L against its original baseline opponents; not a comparison with later engines |
| v1 / v2 | V1 diagnostic gate failed. Identical source entered a later v2 campaign: 86.5/128 short and 26/32 full vs v0; qualified |
| v3 | Passed-pawn evaluation: 61.5/128 head-to-head short points; failed |
| v4 | First-ply quiet checks: 60/128 head-to-head short points; failed |
| v5 | Efficiency proxy improved in completed cells; initial validation gate failed. Separate game review stopped incomplete |
| v6 | PVS-only bridge; runner failure before scored games; incomplete |
| v7 | Original compiled core: 20/24 short, 3.5/4 full vs v2; qualified |
| v8 | Unchanged-v7 budget diagnosis; no qualifying decision repair |
| v9 | Initial low-clock gate failed; separate practical screen 9/16 short, 1/2 full vs v7; failed |
| v10 | King-shelter term: 7.5/16 short, .5/2 full vs v7; failed |
| v11 | Specialized quiescence ordering: 9/16 short, 1.5/2 full; combined gate failed. Separate confirmation 1/4, also failed |
| v12 | Seven CPU-fitted classical corrections; original decision gate failed. Separate unchanged-source game study 2.5/7 short vs v7; failed |
| v13 | Doubled-pawn correction changed selected recapture; 4/9 short vs v7; failed |
| v14 | KQK repair; exhaustive defending replies on four roots and seeded coverage, two clean full-clock draws vs v7; maintenance-qualified |
| v15 | Bounded checking-move quiescence: 0.5/5 short vs v14; failed |
| v16.1 | Classical ordering/history/time work: 14/16 short, 18.5/20 full vs v14; qualified and submitted |
| v17–v19 | V17/v19 initialization/infrastructure limits left studies incomplete; v18 failed its game criterion |
| v20 | Qualified vs v14 at 15/16 short, 18/20 full. Later direct comparison vs submitted v16.1 stopped at 1.5/6 short; failed; payload private |

Sources: [8 September](../PROGRESS_2026-09-08.md), [9 September](../PROGRESS_2026-09-09.md), [10 September](../PROGRESS_2026-09-10.md), [portable earlier summaries](strength-development-2026-09-10.json), [retained report identities](retrospective-source-identities.json).

## Later search and original neural work

Unless noted, the game screens below used exact submitted v16.1 as comparator, 10s + 0.1s for short and 120s + 0.5s for full; later admission required 12/16 and 6/8 points. Some earlier exploratory studies had their own declared gates and reused development openings. Their results are not pooled.

| Study | Change/question | Outcome |
|---|---|---|
| v21–v23 | Internal cycles and a cost guard | Reused-development screens fell below their declared 13-win criterion; no submission |
| v24 | Queen-conditioned king pressure | R82 selected choice changed; 3W/2D/4L, 4/9 short; failed |
| v25 | Guarded one-ply LMR | 8W/5D/2L, 10.5/15 short; failed |
| v26 | Guarded null move with verification | 1W/4D/3L, 3/8 short; failed |
| v27 | Guarded null move without verification | 9W/1D/4L, 9.5/14 short; failed; no general zugzwang-safety claim |
| v28 | Null move plus LMR | 5W/3D/3L, 6.5/11 short; failed despite higher median completed depth |
| v29 | First neural model, piece-square, 32 hidden | Training fit improved; validation/test worsened. Accuracy rejection; no games |
| v30 | Piece-square, 8 hidden, stronger regularization | Validation/test improvements 0.39%/0.62%, below 2%; no games |
| v31 | Relational/geometric, 8 hidden, 592 parameters | Validation/test error fell 14.37%/13.04%; 3W/1D/4L, 3.5/8 short; failed alone |
| v32 | V31 network plus guarded LMR | 6W/1D/4L, 6.5/11 short; failed |
| v33 | Exact static-evaluation cache | Completed phase 6W/0D/5L, 6/11 short; failed; earlier tooling partials retained |
| v34 | Reusable neural workspace | Cost screen failed; no games; not part of final build |
| v35 | Iteration-forecast diagnosis | One selected continuation improved when another depth completed; no candidate/games |
| v36 | Forecast multiplier 1.25→1.0 | 11W/2D/3L, 12/16 short passed; 3W/3D/1L, 4.5/7 full failed |
| v37 | Reversible suffix for score-table context | 12W/3D/1L, 13.5/16 short; 7W/1D/0L, 7.5/8 full; qualified |
| v38 | Covered opposite-colored KBBK conversion | Targeted proof/seeded checks; 2W smoke vs v37; maintenance-qualified |
| v39 | Fifty-move decision boundary | R99 targeted repair; 0W/1D/1L smoke vs v38; maintenance-qualified and final submitted |

The final model is the unchanged v31 network. The final search includes guarded LMR, not the earlier null-move candidates. V37's component bundle was not an ablation of the neural network. See [model card](../releases/competition-v6-internal-v37-01/MODEL_CARD.md), [v37 qualification evidence](../releases/competition-v6-internal-v37-01/evidence-summary.json), [final v39 evidence](../releases/final-internal-v39-01/evidence-summary.json).

## Closed final window

| Study | Outcome |
|---|---|
| v40 | Shallow checked extension; 7/12 short, failed |
| v41 | PV-only checked extension; target unchanged, no games |
| v42 | Queen-present extension; 2.5/7 short, failed |
| v43 | Wider 32-hidden neural model; reused-assessment error worsened; no games |
| v44 | Capture/pawn-check extension; 1/6 short, failed |
| v45 | Quiet queen-pin threat; target unchanged, no games |
| v46 | Advanced-king quiet checks; 1.5/6 short, failed |
| v47 | Equivalent precomputed hash constants; microcost improved, no strength qualification |
| v48 | Two-depth iteration forecast; R103 selected estimate improved, 4.5/9 short, failed |

[Final-window machine-readable summaries](final-window-v40-v48.json) and the [closed record](../FINAL_SUBMISSION_2026-09-11.md) retain limits and stopping decisions. None of v40–v48 entered the final v39 archive. No fresh game campaign was run to write this index.
