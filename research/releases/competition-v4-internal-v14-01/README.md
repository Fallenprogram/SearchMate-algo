# Competition v4 candidate: internal v14-01

This release preserves the exact package locally qualified on 8 September 2026
as a **targeted KQK repair**. Competition v4 is the intended label; **platform
acceptance is unconfirmed**. The latest confirmed competition submission remains
[v3 / internal v7-01](../competition-v3-internal-v7-01/README.md). Publishing these
files does not upload or activate a replacement.

| Identity | Value |
|---|---|
| Internal candidate | v14-01 |
| Intended competition label | v4, acceptance unconfirmed |
| Source and assets | [player/agent.py](player/agent.py), [attribution](player/TABLEBASES.txt), `player/tables/` |
| Qualified ZIP | [SearchMate-competition-v4-internal-v14-01.zip](SearchMate-competition-v4-internal-v14-01.zip) |
| Source SHA-256 | `5664d65c91e8981f2980ecf7630f8231c2986d736d54c86a8d454085b6fcfc61` |
| ZIP SHA-256 | `466bebe215e1d93b2b97d41fec4d35f9f097eed00ac51ad44f7c5958db8591b8` |
| Size | 17,746 bytes compressed; 53,784 bytes uncompressed |

The archive contains exactly root `agent.py`, `TABLEBASES.txt`,
`tables/KQvK.rtbw` and `tables/KQvK.rtbz`. The two table assets total 5,664 bytes.
The original ZIP is preserved without rebuilding; payload sizes and SHA-256
identities are in [release.json](release.json).

**Root `agent.py` and root `make zip` still identify historical v0.** Use the exact
release archive above. Copying only `agent.py` would omit the required KQK data.

## What changed

The original v7 engine gains an exact king-and-queen-versus-king root selector.
It eagerly verifies and loads the shipped Syzygy WDL/DTZ data at import, examines
all legal children, preserves the best outcome and uses distance-based progress
with deterministic ties. DTZ is rounded distance-to-zero, not exact mate distance.
The original 35 functions other than the necessary `get_move` hook are
text-identical; ordinary search, evaluation, quiescence and general clock policy
remain inherited from v7.

Requests with at most 50 ms retain the existing legal fallback. Unsupported
material, missing/corrupt tables, unexpected scores, incomplete probing and an
insufficient conservative fifty-move margin fall back to v7 using the same
request deadline. No runtime downloads, third-party engine implementation or
neural network was added. Table-data provenance is retained in the packaged
attribution notice.

## Existing qualification

The retained checks and games are bound to the unchanged qualified source. Publication
adds no engine calls or new game results. [evidence-summary.json](evidence-summary.json)
records sanitized measurements and hashes of retained private receipts.

- Four ordinary depth-three comparisons matched v7's move, score and node counts;
  restoration checks passed.
- All 64 seeded KQK checks completed; the 61 initially winning cases reached mate
  in their recorded trajectories against distance-maximizing defense.
- An all-defense traversal from two rated-64 positions and their color mirrors
  (four roots total)
  covered 289 states and 179 selector calls. Maximum verified mate lengths were
  12, 12, 7 and 7 plies. This finite proof scope does not cover every KQK position
  or every clock.
- Two fresh-process standard-start games against v7, with reversed colors at
  120 s + 0.5 s, both drew: **0 wins, 2 draws, 0 losses**, 224 legal plies and no
  observed player faults. The gate required two clean games, with no score
  threshold. Neither game reached KQK, so these are compatibility observations.
- The exact ZIP passed offline loading, fresh import, persistent legal replies
  and the finite 250/100/50/10-ms clock screen alongside unchanged v7. Candidate
  package import measured 41.239 seconds; peak job memory was about 202 MiB.
  These local measurements do not guarantee every future initialization or clock.

## Limits and rollback

This qualifies a narrow conversion repair, not a broad strength increase or a
predicted ranking improvement. It does not address other material classes,
middlegame weaknesses or general reconstruction of repetition history between
requests. Conversion optimality is not promised when the helper falls back.
The local compatibility referee used actual threefold repetition, claimable
fifty-move and 600-ply draws; exact platform equivalence of its fifty-move
interpretation remains unverified.

Rollback is the exact [competition v3 / internal v7 ZIP](../competition-v3-internal-v7-01/SearchMate-competition-v3-internal-v7-01.zip),
SHA-256 `0053272feb11a4a6f1595a10baa8591bd33d524ac15f01790be87e61c3ee2a7d`.
Its source SHA-256 is
`768f9112d2740a8a6704f41c5f59e5b7cc7a401fb893f72c904a5fb585848e33`.

Recuris-inspired research records preserve evidence, decisions and unresolved
questions. A causal playing-strength benefit from memory evolution remains
unmeasured.

## Verify the published artifacts

Run `python research/releases/competition-v4-internal-v14-01/verify_artifacts.py`
from the repository root. This standard-library check verifies the archive,
payloads, recorded hashes and rollback identities. It does not import an engine
or rerun the completed qualification.
