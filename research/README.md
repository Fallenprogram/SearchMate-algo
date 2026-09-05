# SearchMate research records

This directory records the approved v0 implementation and local evaluation. The
player is the repository's `agent.py`. Research code and evidence stay outside
`harness/`; the official harness must remain unchanged.

The tested v0 is now an approved baseline champion, with a single-file release
ZIP and restricted Linux container checks pending. The user requested the
repository/release sequence after local verification; the competition upload
remains a manual user action. See [release preparation](RELEASE_V0.md).
Routine implementation and the complete test campaign were authorized on
2026-09-05, including testing beyond three hours.

| Record | Purpose |
|---|---|
| [RESEARCH_PROTOCOL.md](RESEARCH_PROTOCOL.md) | Approved outer procedure, versioning, evidence boundaries, and future control |
| [GATE_SPEC.md](GATE_SPEC.md) | Fixed v0 completion criteria; v1 numeric gate remains unapproved |
| [WORKING_MEMORY.md](WORKING_MEMORY.md) | Compact current state and pending work |
| [EXPERIENTIAL_MEMORY.md](EXPERIENTIAL_MEMORY.md) | Evidence-backed reusable lessons only |
| [INVOCATION_POLICY.md](INVOCATION_POLICY.md) | Routes observed failures to diagnostics |
| [CHECKERS.md](CHECKERS.md) | Definitions and limits of evidence checks |
| [ASSISTANCE_LOG.md](ASSISTANCE_LOG.md) | Researcher configuration, preparation, sources, and implementation assistance |
| [PLATFORM_OBSERVATIONS.md](PLATFORM_OBSERVATIONS.md) | Live contract observations and later platform evidence |

`EXPERIMENT_LEDGER.jsonl` stores append-only structured history. Each
`runs/<run-id>/` preserves a frozen manifest, candidate/reference hashes, PGNs,
per-game records, timings, commands, and summaries. A resumed run must verify its
frozen inputs before doing more work. Preserve failed attempts as evidence.
`candidates/<candidate-id>/` is for isolated candidate snapshots; creating such a
snapshot does not promote a champion. Only separately approved versions belong in
`champions/<version>/`.

Read the final run report for actual results. A planned check in these documents
does not imply that it ran or passed. The v0 games are development evidence, and
neither v0 improvement nor a saved notebook establishes a causal benefit from
evolving memory.

## Completed v0 baseline

[REPORT.md](runs/v0-01/REPORT.md) contains the completed 120-game results and
limitations; [gate.json](runs/v0-01/gate.json) records the automatic local pass.
The tested candidate snapshot is `runs/v0-01/candidate/agent.py`;
`champions/v0/agent.py` preserves the identical approved baseline. The original
report and gate retain their candidate-only status at the time they were written.
[The v1 gate proposal](V1_GATE_PROPOSAL.md) is a recommendation only.

## Running the local tools

Run from the repository root using its existing environment. Choose a new run ID
for a new frozen candidate; `prepare` refuses an existing directory.

```powershell
.venv\Scripts\python.exe -m research.checks --out research/runs/v0-checks.json
.venv\Scripts\python.exe -m research.runner prepare --run-dir research/runs/v0-campaign
.venv\Scripts\python.exe -m research.runner run --run-dir research/runs/v0-campaign --max-games 8
.venv\Scripts\python.exe -m research.runner run --run-dir research/runs/v0-campaign
.venv\Scripts\python.exe -m research.runner summary --run-dir research/runs/v0-campaign
```

The eight-game pause measures calibration within the fixed allocation. Repeating
`run` resumes remaining work after verifying frozen inputs; it does not reset the
sample or discard previous attempts. Use a unique check-output filename because
completed check evidence must not be overwritten. Inspect the declared gate as
well: these commands alone do not replace source review, lint/type checks, or the
official smoke gate.

The runner's `manifest.json` defines the immutable schedule, positions, input
hashes, and environment. `candidate/agent.py` is its source snapshot. `games/`
contains resolved game records and PGNs; `attempts/` retains per-attempt evidence,
including interruptions. `summary.json` is a derived progress/result summary.
Baseline random seeds are not controlled by the unchanged reference processes,
so exact replay of their move choices is not promised.

In the original Windows workspace and interpreter, the recorded final decision
can be reproduced with a new output filename:

```powershell
.venv/Scripts/python.exe -m research.gate --run-dir research/runs/v0-01 --validation research/runs/v0-validation-01.json --out research/runs/v0-gate-recheck.json
```

The validation file links exact lint, typing, unit-test, fixture, and official
smoke commands/results. A gate check never promotes, packages, or uploads.

The historical manifest binds absolute workspace/interpreter paths, installed
dependencies, and source bytes. A fresh clone or a different operating system
must run fresh checks in separate outputs; it cannot claim a replay of the
original environment. Git preserves the raw evidence bytes through
`.gitattributes`. The inherited harness remains untouched, including its existing
Git line-ending policy. Do not rewrite the historical manifest to fit a new host.

## Competition feedback

[COMPETITION_FEEDBACK.md](COMPETITION_FEEDBACK.md) explains how to record manual
upload validation and bring your own game results back for later development.
Feedback used to choose or change v1 is development evidence, not an untouched
final test of the research method.
