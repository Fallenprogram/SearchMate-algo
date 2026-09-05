# SearchMate v0 release preparation

Started: **2026-09-05**. Release player: `v0-candidate-001`.
Source SHA-256:
`ff94c0620c916490a70d429a4f764a46cb30a9a02be3b1ba4147a9621fde1352`.

The user requested the recommended sequence: repository housekeeping, a clear
commit and push for review, GitHub checks, v0 champion approval, packaging,
remaining compatibility checks, and a competition upload performed manually by
the user. This release preparation does not authorize v1 experiments or any
automated competition upload. The original campaign report remains an unchanged
record of its earlier candidate-only milestone.

## Repository changes

- Preserve the original player, 120-game campaign, 34 unit tests, fixtures,
  quality evidence, and research protocol in the user's GitHub fork.
- Extend the existing Linux CI gate with research typing and unit tests.
- Ignore disposable runner locks and preserve exact bytes in historical evidence.
- Document why a historical Windows gate replay requires its original workspace
  and interpreter. A new host runs new checks without rewriting old records.
- Provide a practical guide to manual-upload validation and subsequent
  competition feedback, including the separation of development and final tests.

The configured publishing target is
[`Fallenprogram/SearchMate-algo`](https://github.com/Fallenprogram/SearchMate-algo),
branch `codex/searchmate-v0`. `upstream` is the starter author and is not a
publishing destination for these changes. The public remote's `main` was checked
at `8b5b08bb4f612dd9127f2223b0e859bfc4da3b10` before this update.

## Release checks and their limits

The completed [v0 gate](runs/v0-01/gate.json) and
[baseline report](runs/v0-01/REPORT.md) establish local reliability for the tested
source. Fresh GitHub checks should establish that the committed source passes
on the runner environments. The separately dispatched compatibility workflow
will inspect a single-file archive and run its extracted player in a Linux
container with constrained CPU, memory, network, and filesystem access.

That container is a documented approximation: its CPU model and image are not
the organiser's exact runtime. The current live rules also differ from the
unchanged starter's ply-cap adjudication; see
[P-0003](PLATFORM_OBSERVATIONS.md#p-0003--release-preparation-and-current-referee-difference).
Only the dashboard's validation after the user's manual upload establishes
platform acceptance. Preserve its logs and version association.

## Review and feedback

The commit message should describe the original chess player, fixed evaluation
results, reproducible research records, CI coverage, and remaining platform
limitations. Record actual commit IDs, check URLs, champion decision, ZIP hash,
and compatibility results in a subsequent release record when those steps finish.
Do not present planned or blocked checks as passes.

After manual upload, follow [COMPETITION_FEEDBACK.md](COMPETITION_FEEDBACK.md).
The useful feedback includes the accepted submission version, validation log,
complete game results for a stated interval, PGNs, and own-team timing logs.
An improvement experiment still needs the separately approved v1 gate.
