# SearchMate v0 baseline report

Date: **5 September 2026**. Candidate: **v0-candidate-001**.
Branch: **codex/searchmate-v0**. Decision: **LOCAL TESTS PASSED**.

The original classical player completed the entire approved Windows campaign and
all required checks. The frozen [automatic gate](gate.json) returned `pass`, with
no failure or incomplete reasons. This is a tested candidate awaiting review;
there is no approved champion, submission ZIP, upload, or platform acceptance.

## Results

| Opponent | Clock per side | Games | Wins | Draws | Losses | Score | Mean game duration |
|---|---|---:|---:|---:|---:|---:|---:|
| Random | 10 s + 0.1 s | 64 | 63 | 1 | 0 | 99.22% | 4.09 s |
| Greedy | 10 s + 0.1 s | 24 | 24 | 0 | 0 | 100.00% | 4.18 s |
| Minimax | 10 s + 0.1 s | 16 | 8 | 6 | 2 | 68.75% | 8.95 s |
| Numba | 10 s + 0.1 s | 8 | 5 | 3 | 0 | 81.25% | 11.04 s |
| Greedy, full clock | 120 s + 0.5 s | 4 | 4 | 0 | 0 | 100.00% | 18.28 s |
| Minimax, full clock | 120 s + 0.5 s | 4 | 4 | 0 | 0 | 100.00% | 53.48 s |
| **Total** | Mixed | **120** | **108** | **10** | **2** | **94.17%** | **7.34 s** |

Score awards one point for a win and half a point for a draw. The pooled score is
dominated by the random-opponent safety allocation; it is not an Elo estimate or
a prediction of ladder performance. v0 has no minimum win-rate requirement.

The schedule used **32 distinct, hand-authored development openings**, 60 reversed-
color pairs, and 60 games per color. All 120 slots have PGNs, startup and per-move
observations, source/configuration hashes, and result records. There were **zero
candidate or opponent runtime failures, zero void games, and zero interrupted
attempts**. Of 120 games, 110 ended by checkmate and 10 by repetition. The two
losses were ordinary checkmates against minimax.

Game execution, including per-game startup, totaled **14.68 minutes**.
Elapsed time from the first game to the last was **16.69 minutes**,
including the calibration pause and evidence processing. The initial eight
calibration games counted inside the fixed 120. No sample counts or clocks were
changed. The user-authorized removal of the three-hour cutoff did not require
using the entire original estimate. Development and quality-check time are
separate from these game timings.

## Player and verification

The approximately 200-line player uses python-chess and the standard `time`
module. It implements iterative-deepening negamax, alpha-beta pruning, material
plus small original positional terms, basic deterministic move ordering, terminal
scoring, and conservative deadlines. A legal fallback is chosen first, and a
partial iteration cannot replace the last completed result. Fixed-depth choices
are deterministic; wall-time stopping can change the depth achieved.

The verified checks were:

- **96 timed wire calls:** 24 nonterminal positions at 20, 100, 1,000, and 10,000 ms.
  Coverage includes checks, forced moves, promotions and underpromotion options,
  castling, en passant, and varied game phases. Every reply was legal and timely.
- **10 internal rule/search checks:** mate for both colors, mate/draw precedence,
  stalemate, insufficient material, fifty-move and repetition handling, unchanged
  referee terminal behavior, expired deadlines, score orientation, and determinism.
- **34 automated tests:** nested timeout restoration, fallback/result retention,
  draw boundaries, fixed scheduling, failure attribution, evidence integrity,
  interruption recovery, and gate rejection of incomplete or failed evidence.
- **Ruff and strict mypy passed**, with typing checked across 17 source files.
- **Two additional official smoke games passed**, one per color, against random.
  These are separate from the fixed 120. Original starter preflight artifacts are
  also preserved separately in [starter-preflight](../starter-preflight/provenance.json).
- The harness is unchanged, root source equals the tested snapshot, dependency
  and proposed-package checks passed, and the frozen manifest was reverified.

All commands, exit codes, and output hashes are linked from
[validation evidence](../v0-validation-01.json). The detailed fixture evidence is
[here](../v0-checks-01.json); completed game evidence is in [games](games/).

Across **2,513 SearchMate replies** and
**4,975 recorded plies**:

| Timing observation | Value |
|---|---:|
| Mean / maximum candidate initialization | 173.1 / 457.2 ms |
| Longest observed candidate reply | 1500.95 ms |
| Lowest input clock supplied to candidate in campaign | 5,489 ms |
| Lowest estimated clock immediately after reply, before increment | 5377.56 ms |
| Slowest 20 ms fixture reply | 0.572 ms |

Reply measurements use a high-resolution timer. Post-reply clocks are estimates
that exclude small observation/referee overhead; incoming integer clocks and the
unchanged referee's decisions are authoritative. No platform-resource guarantee
is inferred from these Windows observations.

## Representative weaknesses

The [Black minimax draw from opening o01](games/short-minimax-o01-black.pgn)
repeated queen checks and rook replies while SearchMate was eight nominal material
points ahead. Its clock was still ample. This shows a repetition outcome with a
material advantage; it does not establish that the draw was avoidable or that the
position was objectively won. v0 has no pre-FEN repetition history.

The Slav o21 pair produced both losses. As
[Black](games/short-minimax-o21-black.pgn), SearchMate faced `24.Nf7+`, which forked
its king, queen, and rook; it subsequently lost its queen and both rooks. As
[White](games/short-minimax-o21-white.pgn), late material losses preceded mating
queen-and-rook checks. Both games retained more than six seconds on the recorded
input clocks. These are tactical and king-safety observations, not timeout events
or proof of a particular repair. No source change was made in response.

## Proposed package and status

| Proposed member | Bytes | SHA-256 |
|---|---:|---|
| `agent.py` | 7,342 | `ff94c0620c916490a70d429a4f764a46cb30a9a02be3b1ba4147a9621fde1352` |

Only [the tested player](candidate/agent.py) is proposed. Research files, openings,
opponents, and the harness are excluded. **No archive was created.** The candidate
contains no third-party engine, neural network, move lookup data, native code,
network access, or external binary invocation. Source assistance is disclosed in
[the assistance log](../../ASSISTANCE_LOG.md).

The test manifest hash is `1f7325ef5125527219e142724db1c9f9f92d54e39af04a721cf274fb8048fe7c`. The frozen gate is
`searchmate-v0-safety.1`. Detailed statistics are in [analysis.json](analysis.json),
and raw counts are in [summary.json](summary.json).

Status remains **platform checks pending**: Linux compatibility and enforced CPU,
memory, filesystem, and network limits were not emulated by the local harness.
The official [documentation](https://aichessathon.com/docs) and
[rules](https://aichessathon.com/terms) were checked on 5 September; the canonical
`.md` endpoints were unavailable. Platform acceptance can only follow a separately
authorized upload and its validation result.

## Review recommendation

The declared Windows v0 milestone is complete. This candidate is suitable for
human review as the initial local baseline. Promotion and ZIP creation remain
separate approval decisions; extracted-archive and additional runtime checks
would follow approved packaging. Upload also requires explicit authorization.

A [numeric v1 gate proposal](../../V1_GATE_PROPOSAL.md) is provided for later review,
including the candidate budget, paired comparison, regression margin, and updated
runtime estimate. **No v1 implementation has begun.** v0 is setup/evolution
evidence, not a held-out final evaluation or evidence that evolving memory caused
improvement. No causal memory-effect claim or automatic promotion is made.
