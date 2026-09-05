# SearchMate platform observations

## P-0001 — Live contract check

Checked: **2026-09-05**. Rules version: **2026-08-31.v3**.
The requested
[agent-contract endpoint](https://aichessathon.com/docs/agent-contract.md) and
[rules endpoint](https://aichessathon.com/docs/rules.md) were unavailable through
the browsing tool. The official
[technical documentation](https://aichessathon.com/docs) and
[rules](https://aichessathon.com/terms) were retrieved instead. Recheck live
sources before relying on constraints for a later packaging/upload decision.

Material runtime constraints: top-level `agent.py` exposes
`get_move(fen: str, time_left_ms: int) -> str` and returns legal UCI. Python 3.12
runs on one CPU core with 2 GB RAM, no network/GPU, read-only storage except
256 MB `/tmp`. Initialization has 90 seconds; each side receives 120 seconds plus
0.5 seconds per move. State survives only within one game; execution pauses on
opponent turns. The uncompressed package limit is 50,000,000 bytes. Dependencies
are fixed; installation requests in a package are ignored. Legal runtime imports
include standard Python and chess 1.11.2, numpy 2.5.2, numba 0.67.0,
torch 2.13.0 CPU, and onnxruntime 1.29.0. Runtime failures lose games.
Native binaries, third-party engines, and published chess networks are prohibited.
Original classical source and AI coding assistance are permitted. Validation
plays both colors; its dashboard log determines platform acceptance.
[Source](https://aichessathon.com/docs)

The rules require entrants to operate their own reliable agent and respect the
published interface and resource limits. The latest dated competition rules take
precedence for competition matters. No organizer account interaction or upload
was performed during this source check.
[Source](https://aichessathon.com/terms)

## P-0002 — Local environment boundary

The user approved Windows-first testing with the repository's locked `.venv`.
Local referee results assess the declared local campaign. They do not establish
compatibility with the competition's Linux image or enforcement of its CPU,
memory, filesystem, process, and network restrictions. Preserve measured host and
runtime details in each run manifest.

No submission ZIP has been created under this implementation authorization. No
SearchMate v0 upload, platform validation, or ladder result has been observed.
Status: **platform checks pending**. Candidate local results belong in run records,
not in this section as inferred platform success.

For any later authorized upload, append candidate/champion version, package hash,
upload time, validation status/log, available PGN/timing evidence, and sufficiently
qualified ladder observations. Do not promote or reject from a single game or a
small rating change. If platform feedback informs a later intervention, label the
lineage platform-adaptive and treat that feedback as development evidence.

## P-0003 — Release preparation and current referee difference

Checked again: **2026-09-05**, during the user's requested repository/release
sequence. The canonical Markdown endpoints remained unavailable; the official
[documentation](https://aichessathon.com/docs) and
[rules](https://aichessathon.com/terms) were retrieved.

The current documentation specifies **600 plies, then a draw**. This starter's
unchanged `harness/rules.py` specifies **300 plies**, and `harness/referee.py`
uses material adjudication at that cap. A ply is one move by one side. The
120-game v0 campaign ended with 110 checkmates and 10 repetitions, so none of its
results depended on the cap. This is a limitation of local referee equivalence;
the submitted `agent.py` does not contain that referee or a ply-cap adjudicator.
Keep the completed evidence and harness unchanged. Future local results that
reach the cap must be identified and cannot be represented as platform-equivalent.

The current documentation also describes rated-game PGNs and private own-team
logs with initialization, move timing, and remaining clocks. See
[COMPETITION_FEEDBACK.md](COMPETITION_FEEDBACK.md) for recording those results
after the user's manual upload. No platform result is inferred from this source
check. Docker and WSL are unavailable on the local Windows host; Linux/container
verification is being prepared as a separate GitHub Actions workflow.

## P-0004 — Restricted Linux compatibility passed

Completed **2026-09-06 SGT** on GitHub Actions, release commit
`efc6643ae2cf32e40962c723623ef75aaee6bf1b`.
[Run 33977425446](https://github.com/Fallenprogram/SearchMate-algo/actions/runs/33977425446)
passed 96 timed fixtures, two fresh-process calls and two full-clock games using
the extracted release player. Both games ended by checkmate. The rebuilt ZIP's
hash matched the local artifact, and the source matched the approved v0 champion.

Effective Docker restrictions were checked from container inspection: one CPU
quota, 2,000,000,000-byte memory/swap ceiling, no network, read-only root and bind
mounts, 256,000,000-byte temporary scratch, 128 processes, an unprivileged user,
and dropped capabilities. Cgroup peak memory was 40,103,936 bytes for the combined
workload and no out-of-memory event occurred. See the
[raw report](releases/v0/linux-compatibility/report.json) and
[completion record](releases/v0/completion.json).

This uses Python 3.12 with chess 1.11.2 in a nonofficial image on a GitHub CPU;
the checker and opponent share the constrained container. The stated referee
differences remain. The result supplies compatibility evidence, not an exact
platform-runtime reproduction. **No upload, dashboard acceptance or rated
competition result has been observed.** The user will upload manually.
