# Evidence behind the standalone report

The article is an engineering case study, not a common-opponent Elo study. This guide maps its claims to public records and makes unavailable evidence explicit.

| Report section | Primary evidence |
|---|---|
| Competition setting | [Agent contract](https://aichessathon.com/docs/agent-contract.md) and [rules](https://aichessathon.com/docs/rules.md), retrieved 11 September 2026 |
| V0 and v2 | [V0 campaign](../research/runs/v0-01/REPORT.md), [v2 release](../research/releases/v2-01/README.md) |
| Original compiled core | [V7 release](../research/releases/competition-v3-internal-v7-01/README.md) |
| Last classical submission | [V16.1 release](../research/releases/competition-v5-internal-v16-01/README.md), [10 September review](../research/PROGRESS_2026-09-10.md) |
| Neural architecture and fitting | [Model card](../research/releases/competition-v6-internal-v37-01/MODEL_CARD.md), [frozen accuracy](../research/releases/competition-v6-internal-v37-01/model-accuracy.json) |
| V37 combined qualification | [Games](../research/releases/competition-v6-internal-v37-01/games.json), [evidence summary](../research/releases/competition-v6-internal-v37-01/evidence-summary.json) |
| KQK and final maintenance | [V14 release](../research/releases/competition-v4-internal-v14-01/README.md), [v39 release](../research/releases/final-internal-v39-01/README.md) |
| Unsuccessful alternatives | [Study chronology](../research/studies/README.md), [historical retrospective](../research/RETROSPECTIVE.md) |
| Rated record | [Per-round JSON](../research/rated-results/rated-results-26-109.json) |
| Qualification Swiss | [Per-game JSON](../research/tournament-results/swiss-110-122.json), [official standings](https://aichessathon.com/leaderboard?stage=final) |
| Research memory | [M1-P001–003](../research/EXPERIENTIAL_MEMORY.md), [append-only ledger](../research/EXPERIMENT_LEDGER.jsonl) |

## What can be reproduced publicly

The final player, trained weights, covered tablebase files and artifact verifier are public. So are training recipes, frozen metrics, selected qualification PGNs, result inventories and figure scripts. Plot data is derived from those records; no new reference searches were used for the publication.

Bulk teacher labels, private runtime logs, sealed inputs and unqualified engine/model payloads remain local. The public repository therefore supports source inspection and result checking, but is not a complete recreation of every training run. A fresh run also depends on hardware, dependencies and workload timing. This documentation update makes no stronger reproduction claim.

## Reading the evidence correctly

Local screens compare particular frozen candidates, opponents, opening roots and clocks. Repeated candidate selection and early stopping limit inference about general win rate. V37's combined qualification is distinct from v39's narrow maintenance screen. Static model MAE is distinct from game strength. Public Swiss outcomes establish the score and placing but do not diagnose the cause of individual losses.

Submission attribution follows available user history and platform observations. Round 80 and round 106 remain uncertain; no Swiss game displays a source hash. Final Swiss rank 103/334 and rating 1872 are separate from the end-of-ladder rank 182/465 and rating 1723.
