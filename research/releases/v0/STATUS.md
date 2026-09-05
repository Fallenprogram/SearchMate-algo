# SearchMate v0 release status

**6 September 2026 SGT: prepared for the user's manual competition upload.**
The v0 champion is the original tested player; no engine changes were needed
during release preparation. No competition upload or v1 experiment has occurred.

| Item | Verified result |
|---|---|
| Implementation commit | `45ab093835c5fd1f77dd523869c76a59e7ce8e0c` |
| Release commit checked in Linux | `efc6643ae2cf32e40962c723623ef75aaee6bf1b` |
| Review | [Draft PR #1](https://github.com/Fallenprogram/SearchMate-algo/pull/1), branch `codex/searchmate-v0` |
| Champion | [v0 approval and provenance](../../champions/v0/approval.json) |
| Original local gate | [Pass](../../runs/v0-01/gate.json); 120 games, no runtime failures |
| GitHub CI | [Pass](https://github.com/Fallenprogram/SearchMate-algo/actions/runs/33977425361); Linux gate and Windows/macOS smoke jobs |
| Restricted Linux check | [Pass](https://github.com/Fallenprogram/SearchMate-algo/actions/runs/33977425446); 96 timed fixtures, 2 fresh-process calls, 2 full-clock games |
| Container restrictions | Verified effective CPU, memory, network, filesystem, process and user settings |
| Container memory | Peak 40,103,936 bytes for the combined checker/player/opponent workload; no OOM event |
| Manual upload file | `submission.zip` in the repository root, 7,456 bytes |
| ZIP contents | Exactly `agent.py` at the root, 7,342 uncompressed bytes |
| Platform acceptance | Pending the user's manual upload and the dashboard's validation result |

ZIP SHA-256:
`2fd30951173a967e3394c59df62844e1d5a15514b853458c8c7de0c306fc1c84`

Player SHA-256:
`ff94c0620c916490a70d429a4f764a46cb30a9a02be3b1ba4147a9621fde1352`

The Linux check rebuilt the deterministic archive and required its complete ZIP
hash to match the local release. It inspected the members, extracted the player,
and ran that extracted source. Root independently compared the downloaded
results, source and package hashes, release-metadata hash, all successful fixture
records, and effective container restrictions. Both full-clock games ended by
checkmate, so neither relied on the starter's different ply cap.

The Docker image and CPU are not the organiser's exact environment. The harness
and opponent shared the constrained container with the player. Passing these
checks is evidence of compatibility; the competition dashboard remains the
authority for acceptance. The unchanged starter uses a different long-game cap,
as recorded in [platform observations](../../PLATFORM_OBSERVATIONS.md).

[release.json](release.json) is the immutable creation record and correctly says
the container check was pending when the ZIP was created. The subsequent
[completion record](completion.json) and
[raw container report](linux-compatibility/report.json) establish its later pass.
The original campaign's candidate-only report likewise remains historical.

After manually uploading this exact ZIP, save the validation status/log and the
site's submission identifier. Then provide all available PGNs and own-team logs
for a stated observation interval using the
[feedback template](../../COMPETITION_FEEDBACK.md#what-to-bring-back-to-this-task).
Those results can guide later development; they are not an untouched final test
once used to change the player or researcher memory.
