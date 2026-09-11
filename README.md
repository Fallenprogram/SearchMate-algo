# SearchMate

SearchMate is an original CPU chess engine and a Recuris-inspired research project for [AI Chessathon](https://aichessathon.com/).

**V37 is locally qualified against submitted v16.1:** 13.5/16 short-clock points and 7.5/8 full-clock points, with zero recorded faults. [Download the exact ZIP and read its release record](research/releases/competition-v6-internal-v37-01/README.md). The build includes our original CPU-trained neural residual and search improvements; [the model card](research/releases/competition-v6-internal-v37-01/MODEL_CARD.md) documents its provenance and limitations.

| V37 local screen against exact submitted v16.1 | W / D / L | Points |
|---|---:|---:|
| Short, 16 games at 10s + 0.1s | 12 / 3 / 1 | 13.5/16 |
| Full, 8 games at 120s + 0.5s | 7 / 1 / 0 | 7.5/8 |

[All 24 qualification PGNs and game metadata](research/releases/competition-v6-internal-v37-01/games.json) are published. These finite screens after multiple candidate attempts do not establish Elo or predict ladder results. R82 defense and the uncovered two-bishop conversion question remain unresolved. The prior neural-only v31 and full-clock v36 failures are retained in the [11 September research update](research/PROGRESS_2026-09-11.md).

Root `agent.py` and root `make zip` remain historical v0. Use the exact named modern release archive; v37 also requires its weight file, tablebase assets and attribution notice. The API remains `get_move(fen: str, time_left_ms: int) -> str`.

## Results and version history

The [rated inventory](research/rated-results/README.md) covers65 supplied records, rounds26–90, preserving the round30 void/export discrepancy and uncertain version boundaries.

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

V37 combines the original Numba board/search core with a small symmetric neural correction, guarded late-move reductions, exact runtime static-evaluation caching, revised iteration forecasting and reversible-history score-table context. The KQK ending repair is inherited unchanged. There is no runtime GPU, external engine, network call or automatic learning from uploaded matches.

[Current state](research/CURRENT_STATE.md), [11 September progress](research/PROGRESS_2026-09-11.md) and [research index](research/README.md) distinguish local qualification, deployment, historical failures and open questions. V20 source/ZIP remain private under the prior publication boundary; its older against-v14 results above are historical, not a recommendation over v37 or v16.

Recuris inspires the evidence and decision record: retrieve narrow lessons, freeze a question, measure, and retain failures and uncertainty. Its causal strength benefit remains unmeasured. Private runtime logs, machine identifiers, bulk training/reference corpora and sealed inputs remain local. Publication is not a competition upload.

Historical releases and `harness/` remain unchanged. Generic repository CI exercises root v0, not the archived v37 player. The starter and license come from [advitrocks9/aichessathon-starter](https://github.com/advitrocks9/aichessathon-starter); packaged tablebase data has its own attribution.
