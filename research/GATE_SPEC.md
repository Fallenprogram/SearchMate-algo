# SearchMate gate specification

Gate version: **searchmate-v0-safety.1**. Protocol: **searchmate-v0.1**.
Recorded: **2026-09-05**. Scope: v0 local completion only.

This specification implements the approved v0 plan and the user's removal of its
three-hour cutoff. It is not an active v1 champion-admission gate. The run manifest
must record the hashes of this document, the protocol, decision code, candidate,
reference opponents, and test inputs before evaluation.

## Fixed game allocation

Freeze 32 distinct, varied legal opening positions before evaluating the
candidate. Record FENs, position IDs, and provenance. Every pair plays the same
position twice with SearchMate's color reversed. All positions are evolution
evidence; predefined subsets may overlap across opponent groups.

| Opponent and purpose | Opening pairs | Games | Base / increment per side |
|---|---:|---:|---:|
| Random safety | 32 | 64 | 10,000 / 100 ms |
| Greedy comparison | 12 | 24 | 10,000 / 100 ms |
| Minimax comparison | 8 | 16 | 10,000 / 100 ms |
| Numba comparison | 4 | 8 | 10,000 / 100 ms |
| Greedy full-clock safety | 2 | 4 | 120,000 / 500 ms |
| Minimax full-clock safety | 2 | 4 | 120,000 / 500 ms |
| **Total** | **60** | **120** | **112 short; 8 full-clock** |

Run sequentially. Calibration is the first pair against each of random, greedy,
and minimax at the short clock, followed by one full-clock greedy pair. These
eight games count within the table. Use their measured duration to estimate
remaining runtime; estimates do not change required counts. Additional diagnostic
games never replace or silently enlarge the fixed comparison sample.

Preflight on the unchanged starter was completed during environment setup and is
separate from these 120 v0 games. Preserve its provenance; do not label it v0
evidence. Run the official lint/type and two-game smoke gate for the implemented
candidate, using equivalent explicit commands if `make` is unavailable.

## Required checks

| Check | Required result |
|---|---|
| Interface and imports | Supported imports; callable `get_move(fen: str, time_left_ms: int) -> str`; successful fresh initialization |
| Legal fixtures | 24 declared nonterminal FENs, each at 20, 100, 1,000, and 10,000 ms; all 96 replies are legal UCI strings |
| Fixture breadth | Checks, forced moves, promotions, castling, en passant, and varied game phases are represented |
| Terminals | Correct internal scoring for checkmate and draws; official referee terminal behavior checked; no demand for a legal move when none exists |
| Runtime safety | No candidate illegal/malformed replies, crashes, initialization failures, memory failures, or flags in the designated suite |
| Source quality | Ruff and strict mypy pass for the player and new research Python tooling; required official checks pass |
| Dependency/provenance review | Only allowed runtime dependencies and original readable player code; no prohibited engine, model, binary, network, or subprocess dependency |
| Proposed package | Manifest and uncompressed byte count prepared for intended single-file `agent.py`; no archive is created |
| Campaign completeness | All 120 declared game slots have resolved, attributable evidence with PGNs and per-game records |
| Evidence integrity | Frozen input hashes match, commands/configuration preserved, raw counts reconcile with summaries, and `harness/` is unchanged |

Record elapsed response times for legal fixtures and available game timing. A
fixture's clock input is a stress condition, not a promise of identical Windows
scheduler latency on the competition host. Any observed deadline overrun must be
investigated and reported; a candidate flag is a gate failure. Do not hide an
overrun by averaging it with faster calls.

## Decision rules and failures

There is **no minimum v0 win rate**. Wins, draws, losses, and pair scores describe
the baseline; they are not an improvement test or champion comparison.

- **Local tests passed:** every required check and game slot completed, all
  required checkers passed, and there are zero observed candidate runtime
  failures in that candidate's designated verification.
- **Failed:** a candidate runtime failure or other required check failure remains
  for the evaluated candidate. A fix creates a new candidate version and requires
  its full designated verification; preserve the failed version's evidence.
- **Incomplete:** any mandatory evidence is missing, a broken attempt is
  unresolved, or a required check cannot be executed. Elapsed time alone no
  longer ends the batch.

Opponent or infrastructure failures remain visible, with affected side,
termination, diagnostic evidence, and resolution recorded. Retain original
attempts and link any rerun. An opponent crash cannot be silently counted as a
normal strength win, and a broken run cannot be censored from the history. Report
both all-attempt observations and the resolved fixed-slot campaign.

Interrupted/resumed runs must verify their frozen manifests and preserve completed
games. If candidate or decision code changes, create a new version rather than
mixing results under one hash. Measurement corrections must explain which prior
results are invalidated and rerun them as necessary.

## What a pass does not authorize

**Platform checks pending** remains a separate status for Linux compatibility and
enforced platform resource restrictions. **Champion approved** requires explicit
human approval. **Submission-ready** additionally requires the approved archive
and runtime checks. **Platform accepted** requires successful validation after a
separately authorized upload. A local pass supplies none of those statuses.

## v1 admission gate: not approved

No v1 candidate work or automatic promotion is authorized. Use measured v0
throughput to recommend, for approval, exact opening counts, clocks, candidate
limits, a conservative paired confidence calculation, regression thresholds,
targeted repair metrics, and treatment of inconclusive results. Freeze those
numbers and the executable gate before v1 begins. Require fresh disjoint gate
blocks per formal candidate and keep the final test reserved until selection
ends. Never add games merely because a candidate narrowly missed a threshold.
