# Final submitted SearchMate: internal v39-01

The user confirmed **v39 as the final competition submission on 11 September 2026** and stopped further development. The exact archive is preserved here without rebuilding it.

[Download SearchMate-next-submission-internal-v39-01.zip](SearchMate-next-submission-internal-v39-01.zip)

- ZIP SHA-256: `bad3347ceae0fed3a09397641f90b4789224e4e7d23206c1fc2c04d0aba8b83f`
- `agent.py` SHA-256: `c3a03de24e3aa9c9caa1ac1323f4955146ee12a6ace3ef4b18d074eb1e8f8bc5`
- [Machine-readable release and all nine payload hashes](release.json)
- [Original submitted source](player/agent.py), [model provenance](../competition-v6-internal-v37-01/MODEL_CARD.md), [tablebase attribution](player/TABLEBASES.txt)

## What this final version contains

V39 inherits v37's original CPU-trained neural residual, Numba search and board core, guarded late-move reductions, evaluation cache and history-aware score table. The trained neural component first appeared in internal v31. V31 itself did not qualify, but the same model was retained in the later qualifying v37 combined build. The preceding submitted v16.1 used handcrafted evaluation without a trained network. V39 therefore replaces that classical-only submission with a hybrid classical/neural evaluator. The neural file is unchanged from v31: 72 inputs, eight hidden units, 592 trained parameters. No later experimental model or search change is included.

The inherited KQK selector handles the covered queen-versus-king ending. V38 added a tablebase selector for two opposite-coloured bishops versus a bare king, covering both players and either turn, with safe fallback paths. Its four-root exhaustive defending-reply traversal completed over 515 states; 51 seeded winning cases converted and 13 drawn cases were preserved. V39 reuses that evidence through verified helper and asset identity.

V39 fixes premature draw evaluation at halfmove 99. The earlier search could return a draw before considering a capture or pawn move that resets the counter. At that boundary, quiescence now examines every legal move without stand pat. The premature terminal shortcut is removed, and the root checks a reached fifty-move boundary. Actual-boundary draw handling, mate priority, other search policy and clock formulas remain unchanged from v38.

## What was demonstrated

In the round-99 diagnostic, both original-clock v39 trials chose **111...Nb6** instead of v38's **111...Nb4**. The old line allowed `cxb4`. All **19 legal White replies** after Nb6 reach an actual 100-halfmove draw without checkmate under the observed referee policy. Matched-history reference estimates were 0 versus -435 cp from Black's perspective. This is specific decision evidence, not an Elo estimate.

| Evidence | Result | Meaning |
|---|---|---|
| Historical v37 vs submitted v16.1, short | 12W / 3D / 1L, 13.5/16 | Broader predecessor strength screen |
| Historical v37 vs submitted v16.1, full | 7W / 1D / 0L, 7.5/8 | Broader predecessor strength screen |
| V38 vs v37, two full-clock smoke games | 2W / 0D / 0L | Clean maintenance screen; no points gate |
| V39 vs v38, two full-clock smoke games | 0W / 1D / 1L | Clean maintenance screen; no points gate |
| V39 technical and package checks | Passed locally | Targeted regression and packaging evidence |

The v37 scores belong to its exact build; they are not a repeated v39 strength campaign. [V39 smoke PGNs](games.json) and [portable evidence](evidence-summary.json) retain the weaker result rather than implying a broad improvement.

Four ordinary depth-three comparisons matched v38's move, score, nodes and TT statistics; four TT-on/off depth-four score comparisons passed. Boundary captures, pawn moves, promotions, mate/stalemate, repetition and timeout restoration were covered. Original-clock R97 defense remained unchanged; R103 remained unresolved.

The exact ZIP passed its recorded CRC, identity, dependency, offline loading, persistent-request and low-clock checks. V39 cold import was **27.93 seconds**, with **256.6 MiB** peak job memory. Fourteen requests per source included ordinary play, inherited KQK/KBBK roots and 250/100/50/10-ms inputs. All 40 protected historical identities remained unchanged. These are finite local checks, not an all-platform or all-clock guarantee. No new engine calls were made for this publication.

## Early rated observations and remaining limits

The user reports **1 win and 1 draw** for v39. The public profile shows round 107 drawn against Fork 72 and round 108 won against berserker, consistent with that report. Attribution follows user submission history because no per-game build hash is visible. Round 106 is left unassigned. [Timestamped rated snapshot](../../rated-results/snapshot-2026-09-11-through108.json).

King safety and longer tactical continuations remain weaknesses; round 103 is not claimed fixed. Near-boundary/probe-failure and low-clock endgame fallbacks may not convert. Historical platform wording did not precisely resolve prospective-claim versus reached-boundary semantics; the repair follows the recorded continuation. Neither two rated games nor maintenance smoke games establish a ranking gain.

Later internal v40-v48 experiments did not qualify and were never included in this ZIP. The user retained v39 and ended development. [Final research record](../../FINAL_SUBMISSION_2026-09-11.md). Recuris remains the evidence and decision process; its causal strength benefit has not been measured.

## Verify the preserved artifact

Run `python verify_artifacts.py` from this release directory. It verifies bytes, archive members and syntax without importing the player or running chess searches. Root repository `agent.py` and `make zip` remain historical v0; this version is the named archive above.
