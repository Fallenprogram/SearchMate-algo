# SearchMate

SearchMate is an original CPU chess engine and a Recuris-inspired research project for [AI Chessathon](https://aichessathon.com/).

**Final submitted engine: internal v39-01, confirmed by the user on 11 September 2026. Development is stopped.** [Download the exact final ZIP and see its source, model and validation record](research/releases/final-internal-v39-01/README.md).

V39 contains our original CPU-trained neural residual and Numba search, covered queen-versus-king and two-bishop-versus-king tablebase selectors, and the round-99 fifty-move draw-boundary repair. The source and archive are frozen. Later v40-v48 experiments did not qualify and are not included.

The user reports **1 win and 1 draw** with v39; the public profile's latest rounds 107 and 108 match this. At 2026-09-11 10:13:35 UTC, the profile showed **rating 1647, rank 215 of 465**. This overall rating spans engine versions; two games do not establish a strength gain. [Rated results and attribution](research/rated-results/UPDATE_2026-09-11.md).

V39 qualified as targeted maintenance. Its clean two-game smoke against v38 scored **0W/1D/1L**. The broader local strength evidence belongs to predecessor v37:

| Historical v37 screen against exact submitted v16.1 | W / D / L | Points |
|---|---:|---:|
| Short, 16 games at 10s + 0.1s | 12 / 3 / 1 | 13.5/16 |
| Full, 8 games at 120s + 0.5s | 7 / 1 / 0 | 7.5/8 |

[V37 qualification PGNs](research/releases/competition-v6-internal-v37-01/games.json), [original model card](research/releases/competition-v6-internal-v37-01/MODEL_CARD.md), and [final research record](research/FINAL_SUBMISSION_2026-09-11.md) distinguish broader qualification, maintenance and failed experiments. No Elo forecast or claim to resolve every weakness follows from these screens.

Root `agent.py` and root `make zip` remain historical v0. Use the exact named v39 archive; it includes its weight file, six tablebase files and attribution notice. The API remains `get_move(fen: str, time_left_ms: int) -> str`.

## Results and version history

The preserved [rated inventory through90](research/rated-results/README.md) covers 65 supplied records. The [new update through108](research/rated-results/UPDATE_2026-09-11.md) adds later verified-batch summaries and public observations, retaining uncertain version boundaries.

| Supplied rounds | User-attributed internal build | W / D / L | Points |
|---|---|---:|---:|
| 54–75 | v7-01 | 9 / 6 / 7 | 12/22 |
| 76–79 | v14-01 | 2 / 2 / 0 | 3/4 |
| 80 | v14 or v16, uncertain | 0 / 1 / 0 | 0.5/1 |
| 81–90 | v16-01 | 5 / 1 / 4 | 5.5/10 |

The 15 games added in the 10 September snapshot contain1,508 legal plies and754 matching own runtime rows, with no recorded illegal reply or time forfeiture. None reached exact queen-versus-king, so this batch does not exercise v14's narrow repair. These different-opponent ladder samples do not establish a controlled strength change.

| Local qualification against v14 | v16-01 | v20-01 |
|---|---:|---:|
| Short,16 games | 13W / 2D / 1L | 15W / 0D / 1L |
| Full,20 games | 17W / 3D / 0L | 17W / 2D / 1L |
| Exact-package gate | Passed | Passed |

These finite results qualify alternatives against v14; they do not rank v20 over v16 or predict ladder Elo. [Current state](research/CURRENT_STATE.md), [10 September review](research/PROGRESS_2026-09-10.md), and [study summaries](research/studies/strength-development-2026-09-10.json) retain failures, limitations and next questions.

## Engine and research

V37 combines the original Numba board/search core with a small symmetric neural correction, guarded late-move reductions, exact runtime static-evaluation caching, revised iteration forecasting and reversible-history score-table context. V39 inherits that core and adds the documented KBBK and draw-boundary maintenance changes after v37. There is no runtime GPU, external engine, network call or automatic learning from uploaded matches.

[Current state](research/CURRENT_STATE.md), [final research record](research/FINAL_SUBMISSION_2026-09-11.md) and [research index](research/README.md) distinguish local qualification, deployment, historical failures and open questions. V20 source/ZIP remain private under the prior publication boundary; its older against-v14 results above are historical, not a recommendation over the final v39.

Recuris inspires the evidence and decision record: retrieve narrow lessons, freeze a question, measure, and retain failures and uncertainty. Its causal strength benefit remains unmeasured. Private runtime logs, machine identifiers, bulk training/reference corpora and sealed inputs remain local. Publication is not a competition upload.

Historical releases and `harness/` remain unchanged. Generic repository CI exercises root v0, not the archived v39 player; its artifact verifier checks the preserved final release separately. The starter and license come from [advitrocks9/aichessathon-starter](https://github.com/advitrocks9/aichessathon-starter); packaged tablebase data has its own attribution.
