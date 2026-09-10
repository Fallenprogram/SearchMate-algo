# Submitted build: internal v16-01

The user confirmed this exact filename was uploaded. Rated81–90 are attributed to it; rated80 is uncertain. Its earlier qualification recorded deadline-related history recovery resets, including a concrete missed repetition-visibility case. A different move was not proved winning.

[Exact preserved ZIP](SearchMate-competition-v5-internal-v16-01.zip) · [source](player/agent.py) · [attribution](player/TABLEBASES.txt) · [manifest](release.json) · [evidence summary](evidence-summary.json).

Source SHA-256: `fdcdea36ad030dd534c2607408b399673d0fee728aeafc0ea456f96871f8f787`.
ZIP SHA-256: `00f244998b54c1d116a4af99ef9c3a2caf1eba262b3c5b59a19d0ae8e73b9084`.
The original ZIP is copied byte-for-byte, not rebuilt. It contains exactly agent.py, TABLEBASES.txt and two KQvK table files; 21694 compressed / 75399 unpacked bytes.

## Changes and measured qualification

Ordinary killer/history ordering, legal position-only move hints, between-request history recovery, specialized quiescence move generation and adaptive clocks. Evaluation and KQK are inherited from v14. The interface remains `get_move(fen, time_left_ms) -> str`. No foreign engine, neural weights, runtime network, new GPU training, LMR or null-move pruning is shipped.

| Saved games against exact v14 | W / D / L | Points |
|---|---:|---:|
| Short,16 games | 13 / 2 / 1 | 14.0/16 |
| Full,20 games | 17 / 3 / 0 | 18.5/20 |

Both original gates and the exact-package checks passed. The original game sets differ between v16 and v20; these figures do not show which is stronger. Review the [current state](../../CURRENT_STATE.md) before uploading anything. The root-level repository player remains historical v0.

The finite package checks covered cold import, memory, offline assets, ten persistent requests per source, four KQK cases and250/100/50/10-ms legal replies. They do not guarantee every clock or startup. The local claimable-fifty draw policy differed by one ply from the observed round80 ending; existing historical results retain that limitation.

## Verify the archive

Run `python research/releases/competition-v5-internal-v16-01/verify_artifacts.py` from the repository root. This standard-library verifier checks CRCs, exact payload bytes, source syntax and declared rollback hashes. It performs no engine imports or new games. Recuris records evidence and decisions; its causal strength benefit remains unmeasured.
