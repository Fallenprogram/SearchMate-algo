# Current SearchMate state

Updated 11 September 2026. Public evidence cutoff: rated round 109. Earlier dated status statements are historical.

**Final user-confirmed competition submission: internal v39-01. Engine development is stopped.** This documentation update launched no engine workload and authorizes no candidate, game campaign or upload.

| Identity | Value |
|---|---|
| Final archive | [SearchMate-next-submission-internal-v39-01.zip](releases/final-internal-v39-01/SearchMate-next-submission-internal-v39-01.zip) |
| ZIP SHA-256 | `bad3347ceae0fed3a09397641f90b4789224e4e7d23206c1fc2c04d0aba8b83f` |
| Source SHA-256 | `c3a03de24e3aa9c9caa1ac1323f4955146ee12a6ace3ef4b18d074eb1e8f8bc5` |
| Original model SHA-256 | `c3c9b7f815e920c88d87974b8a0f63b66c0527c9b52525040ab7b0f20c0b7263` |
| Earlier submitted rollback | [v16.1 / internal v16-01](releases/competition-v5-internal-v16-01/README.md) |

V39 inherits v37's neural/search combination, KQK conversion and v38's KBBK policy, then repairs premature fifty-move draw evaluation. It passed targeted maintenance and package checks. Its two full-clock smoke games scored **0W/1D/1L against v38**. The broader predecessor v37 screen scored **13.5/16 short and 7.5/8 full against exact v16.1**. These are different evidence sets. [Final release](releases/final-internal-v39-01/README.md).

Neural research began at **v29**. **V31 trained the exact 592-parameter network retained in v37–v39**. V16.1 was classical. The model does not learn during competition play. [Model card](releases/competition-v6-internal-v37-01/MODEL_CARD.md).

The saved public profile through 109 shows **1723, 182/465, 35W/18D/30L**, plus one void. User history attributes rounds 107–109 to v39: **2W/1D**. Round 80 remains v14/v16 uncertain; round 106 remains unassigned. No per-game build hashes are available. The live rating is fitted to the current build according to the rules; cumulative results and the historical graph span submissions. [Rated inventory](rated-results/README.md).

Remaining weaknesses include king safety and longer tactical/quiet continuations, the unresolved round 103 case, uncovered endings, imperfect history recovery and finite low-clock fallbacks. No later v40–v48 payload qualified or entered this archive. [Retrospective](RETROSPECTIVE.md), [closed development record](FINAL_SUBMISSION_2026-09-11.md).

Root player/build commands remain v0. Accepted releases, harness and historical studies are preserved. Private logs, bulk corpora, sealed inputs and unqualified payloads remain local. Research lessons M1-P001–003 are documented in [process memory](EXPERIENTIAL_MEMORY.md); their causal benefit is unmeasured.
