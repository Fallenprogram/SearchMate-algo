# SearchMate v2-01 — ready for manual validation upload

The exact tested v2-01 candidate has passed its local gate and release compatibility checks. No competition upload has been performed. V0 remains the last user-associated live submission; formal local champion records have not been changed.

Upload **submission-v2-01.zip in this directory**. The old root submission.zip is still v0. The new archive contains only agent.py, is 8,658 bytes, and has SHA-256 `278d9818bbe5ac82427e5a483e4acbfde9cb98569f49aec74c2c99bac0bd9bde`.

After uploading manually, wait for the dashboard validation outcome, then retain its log and displayed version/submission identifier. Send those back to associate future rated games with the correct player. If validation fails, send the log before making or retrying changes. Upload timing for already queued or running games has not been established.

Checks completed:

- The archived and extracted source exactly matches the frozen v2-01 candidate (`1bec488584769b1d58e9e9d38851d696c5285379e96390b468689131fc8b4cee`).
- Local extracted-player checks: 96 fixtures and 10 internal checks passed.
- Restricted Linux check: 96 fixtures, two fresh-process calls and two full-clock games passed. Both games ended by checkmate, one with each colour. No runtime failure, timeout or memory failure; peak container memory was 40,042,496 bytes.
- GitHub's recreated archive is byte-identical to this local ZIP. Independent audit verified raw evidence, effective restrictions and legal full-game replays.
- Checker Ruff, strict mypy and seven focused packaging/metadata tests passed. Historical frozen inputs and v0 artifacts remain intact.

[Dedicated v2 Linux run](https://github.com/Fallenprogram/SearchMate-algo/actions/runs/34028612862) tests the actual v2 source. [Generic repository CI](https://github.com/Fallenprogram/SearchMate-algo/actions/runs/34028612856) also passed, but it tests the root v0 baseline. [Draft PR #2](https://github.com/Fallenprogram/SearchMate-algo/pull/2) records the release branch; no merge is needed to upload the verified local ZIP.

The Linux container is an approximation of the official runtime: its image and CPU differ, the opponent and checker share limits, and opponent-turn suspension is not simulated. Its two games terminated naturally, so the referee's differing cap adjudication was not exercised. Dashboard validation after manual upload remains the acceptance check; see the [competition documentation](https://aichessathon.com/docs).

This release contains no new player edits. V2's prior local head-to-head results were 70W/33D/25L at short clocks and 21W/10D/1L at full clocks. Those comparisons support trying v2; they do not predict its ladder rating. Private live-game feedback and the subsequent round-32 probe stay in the original workspace and did not alter the frozen evaluation or player.

Read completion.json for source/run identities, limits and evidence hashes. release.json preserves the initial preparation state; completion.json supersedes its pending-check status. Raw CI archives remain local and in the linked Actions artifacts; selected compatibility text records are also published on the release branch.
