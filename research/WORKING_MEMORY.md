# SearchMate working memory

Updated: **2026-09-06 SGT**. Memory: **m0-bootstrap**. Phase: **v0 release preparation**.

| Field | Current state |
|---|---|
| Champion | v0; exact tested baseline frozen under the user's requested release sequence |
| Candidate | v0-candidate-001; local tests passed |
| Source SHA-256 | `ff94c0620c916490a70d429a4f764a46cb30a9a02be3b1ba4147a9621fde1352` |
| Branch | `codex/searchmate-v0` |
| Status | Implementation pushed; GitHub CI passed; ZIP created; container verification pending |
| Current objective | Finish the authorized v0 release; user performs competition upload manually |
| Observed weaknesses | Two minimax checkmate losses in the Slav pair; ten repetition draws; see representative evidence |
| Active hypothesis | None selected for v1; original setup reliability criterion passed |
| Retrieved lessons | None; no accepted RSI lessons or memory-effect claim |
| Researcher | Codex `gpt-6-astra`, `ultra`; backend weight pin unavailable |

The fixed campaign completed **120/120**: **108 wins, 10 draws, 2 losses**, with
zero candidate/opponent runtime failures, voids, or interruptions. It used the
same frozen player throughout. All eight full-clock games finished cleanly.
Game execution totaled **14.68 minutes**, with **16.69 minutes** elapsed across
the campaign, including the calibration pause and evidence processing.

Other checks passed: 96 timed wire fixtures, 10 internal rule/search checks,
34 unit tests, Ruff, strict typing across 17 source files, and two additional
official smoke games. The unchanged starter's original preflight was preserved
separately. No harness edits were made.

Evidence:

- [Baseline report](runs/v0-01/REPORT.md).
- [Automatic gate: pass](runs/v0-01/gate.json).
- [Frozen manifest](runs/v0-01/manifest.json) and [raw counts](runs/v0-01/summary.json).
- [Validation commands and hashes](runs/v0-validation-01.json).
- [Representative draw](runs/v0-01/representative_notes.json) and [losses](runs/v0-01/representative_losses.json).
- [Proposed v1 gate: not approved](V1_GATE_PROPOSAL.md).

All v0 games are evolution/setup evidence. No accepted experiential lesson was
created, no matched control ran, and no untouched final-test result is claimed.
The user removed the three-hour cutoff before implementation; the declared test
counts and pass criteria stayed fixed.

Open limitations: GitHub CI passed on Linux, Windows, and macOS, but restricted
container execution and platform acceptance remain pending. Baseline random choices were uncontrolled.
Tactical and repetition observations are diagnosis inputs, not proof of a repair.

The user subsequently requested the complete repository/release sequence. The
baseline champion is recorded in `champions/v0/approval.json`; package and CI
evidence are in `releases/v0/`. `submission.zip` contains only the tested
`agent.py` (7,342 bytes); its archive hash identifies the upload artifact.
No competition upload or v1 implementation has occurred. The numeric v1 gate
remains unapproved. See [competition feedback](COMPETITION_FEEDBACK.md) for
bringing later platform observations into the development lineage.
