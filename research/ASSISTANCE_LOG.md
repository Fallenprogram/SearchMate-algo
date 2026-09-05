# SearchMate assistance log

This records AI assistance and external sources so the team's implementation can
be explained and disclosed. Append substantive entries; corrections must identify
what they supersede. Do not infer unobserved model settings or source provenance.

## A-0001 — Planning and environment preparation

Date: **2026-09-05**. Phase: preparation, before measured RSI experiments.
Source task: **Review SearchMate competition plan**,
`01a070b7-89fe-7212-bef2-9cc9d58913be`.

The user supplied the initial SearchMate protocol. Codex reviewed the competition,
repository, harness, and Recuris-inspired methodology, then helped establish the
approved v0 scope, fixed 120-game allocation, evidence separation, approval
boundaries, and deferred numeric v1 gate. The user selected Codex as Researcher,
Windows-first verification, and clear evidence requirements for later promotion.

The previous task prepared the locked `.venv` and reported successful imports,
linting, typing, and two unchanged-starter smoke games while leaving tracked
source unchanged. Its artifacts are in
`C:/Users/cheej/.codex/tmp/searchmate-preflight/`, including
`starter-white.pgn` and `starter-black.pgn`. These are setup provenance, not v0
results or evidence of a memory effect. The original checkout was recorded as
`main` at `8b5b08b` before implementation.

## A-0002 — Current implementation authorization and configuration

Date: **2026-09-05**. Phase: v0 setup.
Current task: `01a070e7-c24b-77d3-a38b-e77b75990948`.

The user authorized implementation and the full test campaign while away. The
user expressly allowed testing beyond three hours; the fixed pass criteria and
sample sizes remain unchanged. Routine authorized actions may proceed under the
task's automatic approval review. No champion promotion, submission ZIP creation,
or upload was authorized by this instruction.

Observable researcher configuration is **Codex, `gpt-6-astra`, reasoning effort
`ultra`**. Root verified those fields in this task's local rollout `turn_context`.
The same record reports `approval_policy=on-request` and
`sandbox=workspace-write`; current runtime instructions additionally specify
`approvals_reviewer=auto_review`. These describe the observed client setup, not a
guarantee that backend model weights can be pinned. Backend version pinning remains
a research-validity limitation. Record configuration changes explicitly.

The task uses the approved repository workspace and locked local dependencies.
Instructions include repository `AGENTS.md` (`CLAUDE.md` points to it), user-approved
protocol decisions, inherited task instructions, and managed workspace permissions
with automatic review for eligible escalations. Available work uses local shell,
file editing, read-only source browsing/task recovery, and bounded subagents.

Delegation during setup: the root Researcher coordinates three bounded subtasks
for player implementation, resumable research runner, and research markdown
records. Subagents inherit the parent model/configuration; no model override was
requested. Root integration, checks, campaign execution, and final review remain
centralized. This delegation policy is disclosed setup assistance, not an
unrecorded change to a measured experimental arm.

## A-0003 — External material and source boundaries

Date checked: **2026-09-05**.

- [Competition homepage](https://aichessathon.com/),
  [technical documentation](https://aichessathon.com/docs), and
  [rules](https://aichessathon.com/terms): contract and participation authority.
  The `.md` endpoints named in `AGENTS.md` were unavailable through browsing; the
  official HTML documentation and rules were retrieved. See the dated constraint
  record in [PLATFORM_OBSERVATIONS.md](PLATFORM_OBSERVATIONS.md).
- [Official starter repository](https://github.com/advitrocks9/aichessathon-starter):
  supplied harness, baseline opponents, starter interface, and workflow. Supplied
  opponents are evaluation references. The original `harness/` remains unchanged.
- [Recuris paper](https://arxiv.org/abs/2608.24876) and
  [implementation](https://github.com/Gen-Verse/Recuris): methodological inspiration
  for external memory/control around a fixed researcher. SearchMate does not
  claim a literal reproduction or copy an existing chess engine from these works.
- `python-chess` / the locked `chess` package: position representation, legal move
  generation, and standard chess rules. Remaining runtime dependencies must be
  recorded from the final player import/source review.

SearchMate v0 is to be an original readable implementation. No third-party chess
engine, published chess network, lookup table of engine evaluations/moves, or
external game-time inference is part of the approved design. Record any additional
external material actually incorporated into code before final review.

## A-0004 — v0 construction and pre-campaign review

Date: **2026-09-05**. Candidate: **v0-candidate-001**.
The player was written for this project using only `chess` and `time`. Its small
arithmetic evaluation is original; no existing engine, piece-square table,
network, or move database was copied. Supplied baselines remain unchanged as
opponents. The 32 common-opening SAN lines are hand-authored local development
inputs and are not part of the player or proposed package.

Root independently checked 96 timed wire calls and 10 rule/search cases. A player
review added controlled nested-timeout and draw-boundary tests. Runner review
checked the fixed schedule, failure attribution, durable evidence, and recovery.
A separate completion gate was written and tested with deliberately incomplete
and failed evidence. Synthetic broken agents used by tooling tests are temporary
test fixtures; they are not SearchMate campaign candidates.

Windows `time.monotonic()` was observed to have coarse increments. The player and
observational timings use `time.perf_counter()` for precise deadlines; the supplied
referee and its clock remain untouched. Search order/evaluation are deterministic
at fixed depth; wall-time stopping means selected depth can vary with host load.
Only repetition visible within the reconstructed search history is available.

Before campaign freeze, review identified that retained interrupted attempts made
the initial gate permanently incomplete even after a documented retry. The tooling
was corrected to distinguish explicitly resolved infrastructure interruptions from
unresolved or observed candidate failures while preserving original evidence.
This was an initial measurement implementation correction, not a change based on
candidate strength or a relaxation of the approved reliability criteria.

A-0004 status clarification: at entry time, the interruption correction was still being implemented and checked. The campaign has not yet been frozen or started; final verification will be recorded separately.

A-0004 completion: the interruption correction passed its additional tests and independent review before the campaign freeze. Combined quality verification passed 34 unit tests, Ruff, and strict typing over 17 files. The frozen campaign began after those checks.

## A-0005 — Completed v0 evidence and review

The unchanged candidate completed120 games with108 wins,10 draws,and2 losses;
all runtime checks passed. The automatic gate returned pass. Root preserved the
original starter PGNs/logs under `research/runs/starter-preflight/`, recorded exact
quality commands/output hashes, and wrote the report from saved raw evidence.
Read-only review inspected representative draws/losses without using an external
engine or changing the candidate. A separately labeled v1 numeric proposal was
provided; no v1 implementation, control experiment, or memory-effect claim began.
No champion promotion, ZIP creation, upload, or GitHub push occurred.

## A-0006 — Repository and release preparation

On 2026-09-05 the user requested the recommended repository/release sequence,
including a descriptive commit and push for review, and reserved the competition
upload for manual action. A bounded assistant updated GitHub CI and implemented
an opt-in Linux container compatibility checker. Another verified the official
feedback rules and wrote the platform-results intake guide. Root reviewed the
changes, preserved frozen inputs, added evidence line-ending protection and
release documentation, and rechecked the original v0 gate.

The current official documentation differs from the inherited referee at the
ply cap; the difference is recorded without editing the harness. The player and
its candidate hash remain unchanged. GitHub authentication and remote execution
are separate from local check results; planned workflows are not recorded as
completed compatibility evidence. No v1 implementation or accepted RSI memory
lesson is introduced by this preparation.

## A-0007 — GitHub review and v0 release verification

The user completed the requested GitHub sign-in. Root committed and pushed the
implementation with a descriptive commit message and opened draft PR #1 for
review. GitHub CI passed on Linux, Windows, and macOS. Root then recorded the
user's release-sequence authorization, froze the exact v0 player as the initial
champion, and created its deterministic single-file ZIP. An independent read-only
review checked the archive against the root, tested candidate, champion, source
commit and preserved evidence.

The separate restricted Linux workflow passed. Root downloaded its raw artifact
and independently checked the package/source/release hashes, 96 fixture results,
fresh-process checks, full-clock games, and effective container settings. Source
code was not changed during release preparation. The completed campaign and
release-creation metadata remain unchanged; subsequent evidence was added in new
records. Raw logs retain their original whitespace and byte hashes.

No competition upload or v1 experiment was performed. The feedback guide
distinguishes permitted development feedback, the platform's acceptance evidence,
and the research protocol's untouched final evaluation. Memory remains
m0-bootstrap with no accepted RSI lesson or causal memory-effect claim.
