# Rated results through round 109

Frozen public observation: **11 September 2026**. [JSON with per-round evidence](rated-results-26-109.json) · [CSV for analysis](rated-results-26-109.csv).

The complete observed record contains **84 rounds: 35 wins, 18 draws, 30 losses and one void**. That is 44/83 scored points. The saved profile showed 1723 and rank 182/465; this is a timestamped observation, not the current live ranking. These are ladder records, not final Swiss results.

| Rounds | Reported build | W / D / L | Points |
|---|---|---: |---: |
| 26–35 | v0, provisional; +1 void | 3 / 1 / 5 | 3.5/9 |
| 36–53 | v2 | 6 / 5 / 7 | 8.5/18 |
| 54–75 | v7 | 9 / 6 / 7 | 12/22 |
| 76–79 | v14 | 2 / 2 / 0 | 3/4 |
| 80 | v14/v16.1 uncertain | 0 / 1 / 0 | 0.5/1 |
| 81–105 | v16.1, reported timeline | 13 / 2 / 10 | 14/25 |
| 106 | Unassigned | 0 / 0 / 1 | 0/1 |
| 107–109 | v39, user report | 2 / 1 / 0 | 2.5/3 |

The user confirmed v39 as final. The newest public draw versus Fork 72 and wins versus berserker and Black Box match the user report of 2W/1D. Per-game build hashes are unavailable. Round 80 is unresolved between v14 and v16.1; round 106 is left unassigned. Earlier boundaries follow reported upload history, with v0 especially provisional.

![Rating series and reported build ranges](../figures/rated-history.png)

The graph and cumulative W/D/L span submissions. The rules describe live rating as fitted to the current build; a jump following a few new-build games cannot be read as a controlled Elo gain. Opponents, openings, field size and evidence quality differ between groups. [Interpretation in the retrospective](../RETROSPECTIVE.md).

## Evidence coverage

Rows retain their evidence level and public game URL. Rounds 26–90 inherit the preserved inventory. The verified rounds 93–104 batch contains 1,684 legal plies and 843 matching own runtime rows. Round 105 is a log-only supplied result corroborated publicly, without a supplied PGN. Public-only results do not imply replay validation. Hashes identify retained sources; they do not make private logs downloadable.

Round 30 remains dashboard-void; the historical exported draw is retained separately and excluded from points. Duplicate exports are not counted twice. No inferred build identity replaces a missing per-game hash.

## Preserved earlier snapshots

- [Rounds 26–75](rated-results-26-75.json), [rounds 26–90](rated-results-26-90.json).
- [Original through 90 README, unchanged text copy](../archive/pre-retrospective-2026-09-11/research__rated-results__README.md.txt).
- [Through-108 narrative](UPDATE_2026-09-11.md) and [snapshot](snapshot-2026-09-11-through108.json).

This consolidation ran no new engine analysis, fitted no weights and downloaded no new games. Private runtime logs, match/container identifiers and bulk move corpora remain local. [Publication audit](../DOCUMENTATION_AUDIT_2026-09-11.md).
