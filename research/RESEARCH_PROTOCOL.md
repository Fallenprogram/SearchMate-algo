# SearchMate research protocol

Protocol: **searchmate-v0.1**. Recorded: **2026-09-05**. Phase: **v0 setup**.
Authority: the approved revision in task `01a070b7-89fe-7212-bef2-9cc9d58913be`
("Review SearchMate competition plan"), followed by the current task's explicit
implementation authorization and removal of the three-hour testing cutoff.

## Objective and boundaries

Build a reliable, readable classical chess player and preserve enough evidence
for later bounded improvement experiments. The longer-term question is whether a
fixed LLM researcher with evolving memory can repeatedly improve a separate chess
program. This is **Recuris-inspired**, an adaptation of the
[paper](https://arxiv.org/abs/2608.24876) and
[implementation](https://github.com/Gen-Verse/Recuris), rather than a reproduction.

The Player receives FEN and remaining clock time and returns a legal UCI move. It
uses no remote inference, external engine, or persistent learning between games.
The Researcher is Codex operating outside competition games. Research records and
tooling are not part of the proposed single-file player submission. The original
source must remain explainable; preserve provenance for all external assistance.

Use the actual fork on `codex/searchmate-v0`. Preserve user work and never edit
`harness/`. Follow the current official contract, with dated observations recorded
in [PLATFORM_OBSERVATIONS.md](PLATFORM_OBSERVATIONS.md).

## v0 scope and completion

Implement deterministic iterative-deepening negamax or minimax, alpha-beta search,
simple material and modest positional evaluation, terminal scoring, basic move
ordering, conservative time allocation, frequent deadline checks, and an early
legal fallback. Use `python-chess` for positions and legal moves. Cover special
moves and terminal positions explicitly.

Keep neural models, opening books, tablebases, pondering, external services,
third-party engines, native code, transposition tables, quiescence search, Numba
optimization, and speculative heuristics outside this v0 scope. They may become
separately diagnosed future hypotheses.

Finish the fixed campaign and checks in [GATE_SPEC.md](GATE_SPEC.md). The former
three-hour cap was removed by the user before implementation. Duration does not
alter the declared sample sizes or pass criteria. Save results after each game so
the batch can resume without losing completed evidence. Stop only for a real
blocker or upon completing the authorized milestone; report incomplete work
honestly if it cannot finish.

v0 construction, environment preparation, and calibration are setup. They do not
constitute an RSI candidate experiment or evidence that evolving memory caused
an improvement. v0 has no minimum win-rate requirement.

The milestone ends with a tested candidate, results, proposed package manifest,
known limitations, and a proposed numeric v1 gate informed by measured throughput.
Do not begin v1, promote a champion, create a submission ZIP, or upload as part of
this authorization. A passing check does not supply human approval.

## Researcher and memory versions

Record the observable model identifier, reasoning configuration, instructions,
tools, permissions, delegation policy, and evidence bundle in each formal
experiment. Do not invent settings the client does not expose. Configuration
pinning limitations belong in both the trace and assistance log. A material model
or protocol change begins a new documented lineage.

Use one clean researcher session per measured experiment, initialized from its
explicit evidence bundle. This setup task may use the bounded assistance policy
in [ASSISTANCE_LOG.md](ASSISTANCE_LOG.md). Carry that policy forward only if frozen
as part of the later experimental configuration.

Version the Player and memory independently. Initial memory is **m0-bootstrap**.
Each trace records player hash/version, memory version, lesson IDs retrieved,
evidence actually supplied, and whether the intervention changes player code or
memory. Accepted memory lessons require completed evidence, scope, limitations,
confidence, and active/superseded status. A code improvement does not by itself
validate its proposed explanation.

Working Memory stays compact. Experiential Memory stores supported reusable
lessons. The invocation policy routes diagnosis. Checkers assess evidence. Memory
patches require explicit versioned traces; failures may remain in history without
being admitted as accepted lessons.

## Evidence and measurement discipline

Before v0 evaluation, freeze 32 distinct legal opening positions and their
provenance. Run color-reversed pairs sequentially through the unchanged official
referee. All v0 positions, calibration, games, diagnostics, and repairs belong to
**evolution evidence** and may inform later work.

Freeze candidate source, opponents, test manifests, protocol, decision code,
seeds where controlled, and clock settings by hash/version. Preserve exact
commands and environment information. Where a random seed is not controlled,
state that limitation instead of implying reproducibility.

A failed, interrupted, void, or opponent-broken attempt remains in the trace.
Attribute failures to the player, opponent, or infrastructure using available
evidence. Document corrections and replacement attempts explicitly. Never remove
an inconvenient loss or silently count a broken attempt as a clean completed
fixture. A repaired player gets a new candidate hash and complete verification.

Do not rewrite append-only ledger entries or completed run artifacts. Append
corrections with references to their originals. Changes to measurement machinery
must identify which earlier results remain valid and which require rerunning.

Before v1, freeze disjoint evolution positions, unused gate blocks, and a final
test set. Each formal candidate receives a fresh, previously unused gate block.
Repeated deterministic games do not supply independent observations. Do not add
games until a borderline result passes. Final-test positions, games, and scores
remain unavailable to the Researcher until candidate selection ends; feedback
used for another patch is development evidence thereafter.

Short-clock strength, full-clock safety, and full-clock superiority are different
claims. Local Windows success does not establish platform compatibility,
resource-limit compliance, or upload acceptance.

## Later bounded iteration procedure

v1 is blocked until the user approves a numeric admission gate with exact counts,
clocks, candidate budget, paired statistical calculation, regression thresholds,
and rules for inconclusive results. Pin both its document and executable code.

For each later experiment:

1. Select permitted evolution evidence and retrieve relevant lesson IDs.
2. Diagnose exactly one primary subsystem: search, evaluation, move ordering,
   time management, game-state memory, reliability, packaging/runtime
   compatibility, or measurement infrastructure.
3. Before editing, record the hypothesis, target metric, bounded intervention,
   and evidence bundle. A second subsystem change requires a documented
   compatibility necessity.
4. Create an isolated candidate and run safety, targeted repair, champion
   comparison, and regression checks under the frozen gate.
5. Preserve raw results and calculate the predeclared decision. Inconclusive is
   not a pass; the Researcher cannot override the arithmetic.
6. Append a complete trace and present the decision for human review.
7. Only after explicit approval, freeze the champion. Admit justified memory
   lessons through a separate recorded memory patch.

The trace includes state before/after, selected evidence, retrieved lessons,
diagnosis, subsystem attribution, hypothesis, exact intervention, changed files
and behavior, configuration, raw and summarized results, checker decisions, gate
decision, and human decision. Rejected candidates leave the champion unchanged.

## Deferred matched control

Define the control before v1; running it is deferred. Both arms start with the same
approved v0, researcher configuration, permitted evidence, position splits,
candidate budget, game budget, and fixed gate. Freeze a snapshot of the initial
memory system for the control. Its clean researcher sessions must not receive the
evolving arm's learned lessons or adapted routing/checkers.

Freezing only Experiential Memory would test accumulated lessons alone. Testing
the whole evolving memory system requires holding its initial working-state
rules, invocation policy, and checkers fixed too. Without this comparison, report
observed player improvements without making a causal memory-effect claim.

## Approval and revision

Routine implementation, safe local repairs, and the fixed test batch are
authorized. Champion promotion and ZIP creation require human approval; upload
requires a separate explicit authorization. After authorized packaging, audit the
actual archive and its extracted player before any submission-ready claim.

This document and [GATE_SPEC.md](GATE_SPEC.md) implement the approved plan. After
they are frozen, material changes require an approved protocol revision, a new
version, and an appended explanation. Diagnostic memory changes cannot silently
change the outer admission criteria.
