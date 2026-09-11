# Current SearchMate state — 11 September 2026

**Final user-confirmed competition submission: internal v39-01. Development is stopped by user request.** No further candidate, game campaign or upload is queued; the temporary overnight follow-up remains paused.

[Final release and exact ZIP](releases/final-internal-v39-01/README.md)

- Source SHA-256: `c3a03de24e3aa9c9caa1ac1323f4955146ee12a6ace3ef4b18d074eb1e8f8bc5`
- ZIP SHA-256: `bad3347ceae0fed3a09397641f90b4789224e4e7d23206c1fc2c04d0aba8b83f`

V39 inherits the original CPU-trained model and v37 search, the KQK selector and v38's KBBK repair, then corrects premature fifty-move draw evaluation. It passed targeted maintenance and exact-package checks. V39 smoke: **0W/1D/1L** against v38; no broad-strength claim. Historical v37 strength screen against v16.1: **13.5/16 short and 7.5/8 full**. [Lineage, unsuccessful v40-v48 studies and limits](FINAL_SUBMISSION_2026-09-11.md).

The user reports v39 **1W/1D**. Public rounds 107 (draw, Fork 72) and 108 (win, berserker) match that report. At 2026-09-11 10:13:35 UTC, the overall profile showed **1647**, **215/465**, **34W/18D/30L**. These overall numbers span builds. Per-game hashes are unavailable; round106 is left unassigned. [Rated update](rated-results/UPDATE_2026-09-11.md).

Root `agent.py` and `make zip` remain historical v0. All prior releases, harness and private studies are preserved. V20 and later unqualified payloads remain unpublished. Earlier working-memory/protocol files and dated updates are historical snapshots, not live work instructions. M1-P001–003 remain the decision lessons; the Recuris causal strength benefit is unmeasured.
