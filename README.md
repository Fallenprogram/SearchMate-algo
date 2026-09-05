# SearchMate

SearchMate is a Recuris-inspired chess research project built on the AI Chessathon
starter. The first milestone is an original, readable classical player and an
honest local baseline. Candidate promotion, packaging, and upload are separate
human decisions.

**v0 local verification passed:** 120 campaign games, 108 wins, 10 draws, 2 losses,
and zero runtime failures. Read the [baseline report](research/runs/v0-01/REPORT.md)
and [automatic gate result](research/runs/v0-01/gate.json). The candidate awaits
human review; no champion, ZIP, or upload has been created.

The next milestone is tracked in [v0 release preparation](research/RELEASE_V0.md):
save the reviewed work to GitHub, complete CI and package compatibility checks,
and prepare the entry for the user's manual upload. See
[competition feedback](research/COMPETITION_FEEDBACK.md) for what to bring back
after validation and rated games.

## Player

`agent.py` is the entire intended player artifact. It exposes:

```python
def get_move(fen: str, time_left_ms: int) -> str:
    ...  # a legal UCI move
```

v0 uses python-chess, iterative-deepening negamax with alpha-beta pruning, material
and modest positional evaluation, and deterministic basic move ordering. It keeps
a legal fallback and retains the last completed search result when its deadline
expires. At 50 ms or less it immediately returns a legal fallback; otherwise its
search allowance is capped at 1.5 seconds and a conservative share of the clock.

This is intentionally a small baseline. It has no neural model, opening book,
tablebase, quiescence search, transposition table, or external game-time service.
A FEN cannot restore earlier repetition history; v0 recognizes repetition only
within its reconstructed search history. Fixed-depth behavior is deterministic;
wall-time stopping can produce different depths on different machines.

## Development and evidence

The approved environment is the locked `.venv` on Windows. No dependency changes
are needed. The official `harness/` remains unchanged. Research tooling invokes
its wire runner and referee, preserving the original clock and game rules.

Start with [research/README.md](research/README.md), the approved
[protocol](research/RESEARCH_PROTOCOL.md), and the fixed
[v0 completion criteria](research/GATE_SPEC.md). Current state is in
[Working Memory](research/WORKING_MEMORY.md). Source provenance and the recorded
researcher configuration are in [the assistance log](research/ASSISTANCE_LOG.md).

The v0 campaign contains 120 sequential games over 32 frozen development
positions. Results, PGNs, per-move timings, source hashes, and attempts are saved
under `research/runs/`. The first eight games calibrate runtime and count toward
the same campaign. Resuming preserves completed results and rejects changed
candidate, opponent, harness, checker, protocol, or schedule inputs.

Example commands from the repository root, using a **new** run directory only
when starting a new campaign:

```powershell
.venv/Scripts/python.exe -m research.runner prepare --run-dir research/runs/v0-01
.venv/Scripts/python.exe -m research.runner run --run-dir research/runs/v0-01 --max-games 8
.venv/Scripts/python.exe -m research.runner run --run-dir research/runs/v0-01
.venv/Scripts/python.exe -m research.runner summary --run-dir research/runs/v0-01
```

The fixed suite has no minimum win rate. Local completion requires all designated
checks and games, zero candidate runtime failures, and resolved infrastructure
issues. Testing may exceed three hours, as authorized. Quality commands and the
deterministic completion decision are stored with the validation evidence.

## Status and approval boundary

v0 is a candidate during construction and testing. A local pass does not promote
it, create an archive, or authorize upload. Linux compatibility and enforcement
of the competition's CPU, memory, filesystem, and network restrictions remain
separate platform checks. No v1 optimization begins before its numeric admission
gate receives approval.

The proposed package contains only `agent.py`; the research records, reference
opponents, and harness stay outside it. Do not create a submission ZIP or upload
without the user's explicit authorization. Re-read the live
[competition documentation](https://aichessathon.com/docs) and
[rules](https://aichessathon.com/terms) before later submission work.

## Starter provenance

This fork retains the supplied baselines and unchanged harness from
[advitrocks9/aichessathon-starter](https://github.com/advitrocks9/aichessathon-starter).
Its original license is in [LICENSE](LICENSE). The player implementation and
research tooling were created for SearchMate; assistance is disclosed in the
research records.
