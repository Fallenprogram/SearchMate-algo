# Competition v3: internal v7-01

This directory preserves the exact build submitted on 7 September 2026 and
confirmed ACTIVE in the authenticated dashboard on 8 September. The user reports
submitting after rated round 53 had started. This publication copies the existing
delivered archive without rebuilding or modifying it.

| Identity | Value |
|---|---|
| Competition label | v3, dashboard ACTIVE |
| Internal candidate | v7-01 |
| Source | [player/agent.py](player/agent.py) |
| Delivered ZIP | [SearchMate-competition-v3-internal-v7-01.zip](SearchMate-competition-v3-internal-v7-01.zip) |
| Source SHA-256 | `768f9112d2740a8a6704f41c5f59e5b7cc7a401fb893f72c904a5fb585848e33` |
| ZIP SHA-256 | `0053272feb11a4a6f1595a10baa8591bd33d524ac15f01790be87e61c3ee2a7d` |
| Contents | One root `agent.py`; 37,624 uncompressed bytes; ZIP 8,698 bytes |

**Root `agent.py` and root `make zip` still identify historical v0.** Historical
internal v3 was a different, rejected experiment. See the
[version mapping](../../PROGRESS_2026-09-08.md#version-mapping).

The authenticated dashboard was observed at approximately 03:14 UTC on 8 September:
competition v3 was ACTIVE, with SHA prefix `0053272feb11`, matching the exact local
archive above. Its displayed submission time was 7 September 2026, 15:29; the UI
timezone was not independently recorded, so exact upload UTC remains unknown.
The visible validation-log export ends `valid` at 14:32:02Z, records 37,624
uncompressed bytes, and reports two smoke-game initializations of 20.8 and 26.1
seconds, with a slowest reply of 1.5 seconds in each.

[platform-acceptance.json](platform-acceptance.json) preserves sanitized observation
fields; the raw log remains private. Only the displayed hash prefix was observed,
not a remotely returned full archive digest. Per-game source hashes remain absent.
The original delivery record correctly retains its earlier unconfirmed state.
This publication performs no upload or competition replacement.

The [rated rounds 54-60 review](rated-games-54-60.md) confirms four wins and
three losses, all board-supported checkmates. Its
[machine-readable companion](rated-games-54-60.json) preserves public URLs and
each archived PGN hash. The submission transition and displayed startup times
corroborate association with this build, while exact per-game hashes remain absent.
No new local engine analysis was run for that intake.

## Implementation

An original numeric 0x88 board and reversible make/unmake replace recursive
Python board operations. Numba compiles legal generation, evaluation, ordinary
PVS and quiescence. PVS uses full-window first-child searches, narrow-window
later probes and full re-search for an in-window improvement. Only completed
iterations replace the legal fallback.

Evaluation retains v2's material, positional formulas, bishop-pair term, phase
threshold and score sign. Ordering retains preferred-move, capture/promotion and
UCI tie priorities. The time formula retains the 1.5-second cap and 80%
next-iteration threshold; deadline observation now occurs every 64 visited nodes.
A 262,144-slot score table requires matching position and conservative known-path
and halfmove-context hashes, adequate depth and correct bounds. Mate distance
is normalized; aborted nodes publish no scores; the table resets before searched
requests. Early fallback and forced-move exits skip that reset. It does not contain
v9's later move-order hint.

The source uses NumPy, Numba and python-chess, warming JIT at import with caching
disabled. No external engine port, GPU, neural training, null-move pruning or
late-move reductions entered this build. The API is unchanged.

## Existing qualification

These results predate this publication; no engine calls or games were rerun.

| Stage against released v2 | Clock per side | Games | W / D / L | Points | Required |
|---|---|---:|---|---:|---:|
| Short | 10 s + 0.1 s | 24 | 18 / 4 / 2 | 20 | 18 |
| Full | 120 s + 0.5 s | 4 | 3 / 1 / 0 | 3.5 | 2.5 |

All 28 attempts completed with 1,731 legal plies, zero observed player faults or
clock violations, and no retries. The sequential campaign lasted 24.28 minutes.
Source was frozen before opening allocation was revealed. The first-hour delivery
target was missed: this build arrived about 76 minutes after execution began,
following v6's incomplete attempt.

Local validation covered 2,000 seeded legal positions, 34 special/draw fixtures,
53,004 legal make/unmake pairs, 97 shallow perft cases and 17 fixed-depth cases
with matching v2, TT-on and TT-off scores. Five exact-ZIP persistent wire requests
passed. A separate deadline probe restored state after abort. Ruff and strict
mypy passed. Original ZIP initialization measured 18.473 seconds and peak
validation working set was 254,435,328 bytes on Windows. Selected decision fields
and original report hashes are in [evidence-summary.json](evidence-summary.json).

## Limits and rollback

The historical games used a referee that can terminate when a third repetition
is claimable by the next move. Later public draws ended on the actual third
occurrence. Those results retain their original policy, without a claim of exact
platform equivalence. A later external adapter was prepared, but no v9 game
exercised it. The harness remains unchanged.

Cold startup of unchanged v7 later took roughly 72-84 seconds locally. The
subsequently retrieved platform smoke log records 20.8 and 26.1 seconds, which
supports acceptance of this build but does not explain local variation or bound
every future initialization. This finite screen does
not establish an Elo gain, isolate the contribution of each feature or resolve
all rated-game weaknesses. Evaluation, quiescence membership and the time formula
remain inherited. Draw history is limited to the supplied FEN and known search
path; rare untested cases and nonzero hash-collision risk remain.

Rollback is [v2-01](../v2-01/STATUS.md), with
[source](../v2-01/player/agent.py) SHA-256
`1bec488584769b1d58e9e9d38851d696c5285379e96390b468689131fc8b4cee`.
Its retained archive `submission-v2-01.zip` has SHA-256
`278d9818bbe5ac82427e5a483e4acbfde9cb98569f49aec74c2c99bac0bd9bde`;
the historical notes identify its local and Actions provenance. Neither released
build changed during the research continuation.

Recuris-inspired decision records continue. No controlled comparison has measured
a causal benefit from evolving research memory.
