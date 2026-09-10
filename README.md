# SearchMate

SearchMate is an original CPU chess engine and a Recuris-inspired research project for [AI Chessathon](https://aichessathon.com/).

**Current user-confirmed submission: internal v16-01**, called v16.1 by the team. The [submitted-build record](research/releases/competition-v5-internal-v16-01/README.md) preserves its exact source, ZIP, tablebases and qualification summary. Supplied rated81–90 are attributed to this build; round80 is uncertain. No match log carries a build hash.

**V20-01 is a qualified local alternative, not an established improvement over v16.** Its source and ZIP remain private pending the direct comparison, at the user's request. Both builds won17/20 full-clock games against v14 on different openings. A direct v20-versus-v16 comparison is authorized after this publication; no result is claimed yet.

Root `agent.py` and root `make zip` remain historical v0. Use an exact named archive; the modern builds also require the two table files and attribution notice.

## Results and version history

The [rated inventory](research/rated-results/README.md) covers65 supplied records, rounds26–90, preserving the round30 void/export discrepancy and uncertain version boundaries.

| Supplied rounds | User-attributed internal build | W / D / L | Points |
|---|---|---:|---:|
| 54–75 | v7-01 | 9 / 6 / 7 | 12/22 |
| 76–79 | v14-01 | 2 / 2 / 0 | 3/4 |
| 80 | v14 or v16, uncertain | 0 / 1 / 0 | 0.5/1 |
| 81–90 | v16-01 | 5 / 1 / 4 | 5.5/10 |

The newest15 games contain1,508 legal plies and754 matching own runtime rows, with no recorded illegal reply or time forfeiture. None reached exact queen-versus-king, so this batch does not exercise v14's narrow repair. These different-opponent ladder samples do not establish a controlled strength change.

| Local qualification against v14 | v16-01 | v20-01 |
|---|---:|---:|
| Short,16 games | 13W / 2D / 1L | 15W / 0D / 1L |
| Full,20 games | 17W / 3D / 0L | 17W / 2D / 1L |
| Exact-package gate | Passed | Passed |

These finite results qualify alternatives against v14; they do not rank v20 over v16 or predict ladder Elo. [Current state](research/CURRENT_STATE.md), [10 September review](research/PROGRESS_2026-09-10.md), and [study summaries](research/studies/strength-development-2026-09-10.json) retain failures, limitations and next questions.

## Engine and research

The API is `get_move(fen: str, time_left_ms: int) -> str`. The original Numba engine uses a numeric board, legal move generation, make/unmake, iterative deepening, PVS, quiescence and bounded history-aware score caching. V16 adds move ordering, verified legal move hints, game-history recovery, specialized quiescence generation and adaptive clocks. V20 advances history recovery, context handling and incremental hashing. Evaluation and the KQK repair remain inherited.

The current priorities are king defense in rated82/88, correctly assessing the drawing alternatives in rated87, and comparing prospective replacements against the build actually submitted. A saved loss does not identify its cause, and an extra pawn does not prove a missed win.

Recuris inspires the evidence and decision record: retrieve narrow lessons, freeze a question, measure, and retain failures and uncertainty. The player does not learn automatically from uploaded games. A causal memory benefit remains unmeasured. See the [research index](research/README.md).

Private runtime logs, machine identifiers, reference engines, bulk corpora and sealed inputs remain local. Publication preserves summaries and the exact submitted v16 artifacts; it is not a competition upload. Historical sources/reports and `harness/` remain unchanged. Generic repository CI exercises root v0, not these archived builds. The starter and license come from [advitrocks9/aichessathon-starter](https://github.com/advitrocks9/aichessathon-starter); the packaged tablebase data has its own attribution.
