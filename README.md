# SearchMate

SearchMate is an original CPU chess engine and a Recuris-inspired research project
for [AI Chessathon](https://aichessathon.com/).

**Latest prepared release: internal v14-01, intended competition v4.** It repairs
the exact queen-versus-king conversion failure observed in rated round 64.
The [release page](research/releases/competition-v4-internal-v14-01/README.md)
contains the unchanged qualified source, exact ZIP, tablebase data, attribution
and validation summary. Qualification is for this targeted repair; a large
overall strength improvement has not been demonstrated.

**Last confirmed competition entry: competition v3/internal v7-01.** The user
confirmed that all supplied rounds 65–75 used v7 and preceded any v14 upload.
Current v14 platform acceptance remains unconfirmed.
Use [current state](research/CURRENT_STATE.md) for the submission boundary.

Root `agent.py` and root packaging commands preserve historical v0. Use the
named release ZIP for a submission; do not recreate it with root `make zip`.

## Player and release identities

The public API stays `get_move(fen: str, time_left_ms: int) -> str`.
V7 uses an original numeric 0x88 board, reversible make/unmake, legal generation,
iterative deepening, PVS, quiescence and a bounded score transposition table.
Numba compiles its numeric core on the CPU. V14 adds a root selector for exactly
two kings and one queen, using the packaged Syzygy WDL/DTZ data through
python-chess. It retains v7's ordinary search, evaluation and clock policy,
including the documented fallback conditions. There is no runtime network call.

| Competition label | Internal source | Recorded status |
|---|---|---|
| v1 | v0 | Historical baseline; root source preserved |
| v2 | v2-01 | Historical release |
| v3 | v7-01 | Last confirmed accepted submission; supplied games through 75 |
| v4 (intended) | v14-01 | Targeted KQK qualification passed; acceptance unconfirmed |

V14's exact ZIP SHA-256 is
`466bebe215e1d93b2b97d41fec4d35f9f097eed00ac51ad44f7c5958db8591b8`.
The [v7 release](research/releases/competition-v3-internal-v7-01/README.md)
remains the preserved rollback. Historical internal v3 is a different experiment
from competition v3.

## Rated games and measured evidence

The [rated-results record](research/rated-results/README.md) covers supplied
rounds **26–75**, with source identities, version-attribution limits and the
round-30 void/draw discrepancy retained.

| Supplied v7 rounds | Wins | Draws | Losses | Points |
|---|---:|---:|---:|---:|
| 54–64 | 5 | 3 | 3 | 6.5/11 |
| 65–75 | 4 | 3 | 4 | 5.5/11 |
| 54–75 combined | 9 | 6 | 7 | 12/22 |

The newest batch has 1,073 legal plies and 537 matching SearchMate runtime rows.
No recorded position in rounds 65–75 is exact KQK. R71's king attack is a useful
next diagnostic case; the saved line does not prove a particular correction.
These ladder results and v14's two clean drawn smoke games are not Elo estimates.
The [9 September progress note](research/PROGRESS_2026-09-09.md) explains the
repair coverage, remaining weaknesses and evidence limits.

## Research process and provenance

The researcher collects evidence, defines a bounded question, freezes a candidate
and checks, evaluates it, and preserves failures and uncertainty. The player does
not learn automatically from rated games. The process is inspired by
[Recuris](https://github.com/Gen-Verse/Recuris); its causal memory benefit remains
unmeasured. See the [research index](research/README.md) and
[current research state](research/CURRENT_STATE.md).

Private runtime logs, withheld inputs, reference engines and the bulk corpus
remain local. The publication contains selected summaries and hashes. Earlier
dated reports retain their original statuses. The supplied `harness/` is
unchanged, and generic repository CI exercises root v0, not v14. This update
publishes the completed evidence without running a new engine campaign or
uploading to the competition.

The starter comes from
[advitrocks9/aichessathon-starter](https://github.com/advitrocks9/aichessathon-starter).
Its license is in [LICENSE](LICENSE). The v14 release includes separate
attribution for generated Syzygy tablebase data. SearchMate's original player
and research tooling were developed with Codex assistance.
