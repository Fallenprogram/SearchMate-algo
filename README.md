# SearchMate

SearchMate is an original CPU chess engine and a Recuris-inspired research project
for [AI Chessathon](https://aichessathon.com/). The active submission is
**competition v3, internal v7-01**, submitted on 7 September 2026. The authenticated
dashboard was checked on 8 September: its displayed archive hash prefix matches
the delivered ZIP, and its validation log ends valid.

The [current release](research/releases/competition-v3-internal-v7-01/README.md)
preserves the exact source, delivered ZIP and SHA-256 identities. **Root `agent.py`
and root packaging commands still refer to historical v0.** Use the named release
archive when identifying the competition entry.

## Current player

The [competition v3 source](research/releases/competition-v3-internal-v7-01/player/agent.py)
exposes `get_move(fen: str, time_left_ms: int) -> str`, returning a UCI move.
It uses an original numeric 0x88 board, reversible make/unmake, legal generation,
iterative deepening, principal variation search, quiescence and a bounded score
transposition table. Numba compiles the numeric core on the CPU. The evaluation
and time-allocation formulas retain released v2's behavior. The readable Python
source uses NumPy, Numba and python-chess, with no external engine port, neural
network or runtime network service.

The frozen local screen against v2 passed: **18 wins, 4 draws and 2 losses in
24 short games; 3 wins and 1 draw in four full-clock games**, with no observed
player faults or retries. This is a finite comparison, not an Elo estimate or
competition-rank forecast. The release notes distinguish local Windows checks,
the inherited draw policy, variable cold startup and platform acceptance.

The first seven newly archived rated games, rounds 54-60, confirm **4 wins and
3 losses**, all ending by checkmate. Their
[game-by-game review](research/releases/competition-v3-internal-v7-01/rated-games-54-60.md)
records legal continuations, clocks and the limits of build attribution. This
small rated sample is separate from the local comparison above.

## Versions and research

| Competition submission | Internal source | Status |
|---|---|---|
| v1 | v0 | Historical baseline; root player preserved |
| v2 | v2-01 | Previous release and rollback; identical source to internal v1-01 |
| v3 | v7-01 | Dashboard ACTIVE; archive hash prefix matches the exact preserved ZIP |

Historical internal v3 was a rejected passed-pawn experiment, separate from the
current competition v3. The [research progress record](research/PROGRESS_2026-09-08.md)
explains every internal outcome through v9 and the limits of the evidence.

The Researcher operates outside games: collect evidence, define a bounded
hypothesis, freeze the candidate and checks, evaluate it, and preserve outcomes
and limitations. The Player does not learn from rated games by itself. This
adapts ideas from [Recuris](https://github.com/Gen-Verse/Recuris); it is not a
replication or a measured demonstration that evolving research memory improves
chess strength. The causal memory-control study remains deferred.

## Evidence and maintenance

[research/README.md](research/README.md) is the public evidence index. Completed
reports retain their original dated status; current release/progress records
supersede earlier pending-upload descriptions. Private runtime logs, withheld
inputs, reference engines and the bulk corpus are outside this publication and
submission ZIP. Selected evidence identities are published for traceability.

The supplied `harness/` and root v0 remain unchanged. Generic repository CI
exercises that root baseline, not the current release. This update preserves
existing results and checks source/archive integrity without starting a new
engine campaign or uploading a player. Consult the current
[competition documentation](https://aichessathon.com/docs) and
[rules](https://aichessathon.com/terms) before future release work.

## Starter provenance

This fork retains supplied baselines and the harness from
[advitrocks9/aichessathon-starter](https://github.com/advitrocks9/aichessathon-starter).
The original license is in [LICENSE](LICENSE). SearchMate's player implementation
and research tooling were created with Codex assistance; research records separate
implementation, observations and unresolved causal explanations.
