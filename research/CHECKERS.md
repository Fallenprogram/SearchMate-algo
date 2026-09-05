# SearchMate evidence checkers

Checker definitions: **c0**. Memory: **m0-bootstrap**. Recorded: **2026-09-05**.
The authoritative v0 pass criteria are in [GATE_SPEC.md](GATE_SPEC.md).

| ID | Checker | Evidence and decision | Limit |
|---|---|---|---|
| C-LEGAL | Move legality/interface | Parse every reply as UCI; verify membership in legal moves on all declared nonterminal fixtures and played turns | No legal-move requirement for terminal positions with no legal move |
| C-TERM | Terminal and referee behavior | Check internal mate/draw scoring and unchanged referee handling of terminal fixtures, including its available repetition/draw semantics | FEN alone cannot restore earlier repetition history |
| C-TIME | Runtime and clock | Preserve initialization/move timings and termination reasons; reject candidate runtime failures; investigate fixture overruns | Windows scheduling and machine load differ from platform enforcement |
| C-IMPORT | Runtime compatibility | Fresh-process import, supported dependencies, signature review, source provenance, required lint and strict typing | Does not emulate all Linux or sandbox restrictions |
| C-PACKAGE | Proposed contents | Enumerate intended `agent.py`, hash and byte count; review prohibited artifacts and dependencies without making a ZIP | Actual archive/extraction verification waits for packaging approval |
| C-INTEGRITY | Measurement integrity | Reconcile manifest, hashes, colors, positions, clocks, seeds, PGNs, fixed counts, attempt history, and unchanged harness | Uncontrolled random sources must remain explicitly qualified |
| C-REPAIR | Targeted repair | Compare the predeclared failure metric using its permitted evidence and fixed calculation | Inactive for initial v0 setup; no retrospective hypothesis substitution |
| C-STRENGTH | Champion comparison | Apply the later approved paired statistical gate against a frozen champion | Inactive: no champion or numeric v1 gate is approved |
| C-REGRESSION | Reference regression | Report v0 results by fixed reference opponent; later apply approved regression thresholds | v0 has no minimum score and its reference games are development evidence |
| C-SPLIT | Evidence separation | Label v0 as evolution; later verify fresh gate blocks and final-test isolation | A viewed final result cannot remain untouched evidence for a subsequent patch |

Emit explicit pass, fail, incomplete, or not-applicable decisions with evidence
references. A checker description is not a test result. A summary cannot overrule
raw failure evidence. Preserve contradictory evidence and explain unresolved
attribution instead of averaging it away.

The v0 completion calculation must be executable and pinned with the manifest.
Diagnostic checkers can later improve through recorded memory patches; anything
affecting admission requires an approved protocol/gate revision and versioned
decision code. The Researcher explains decisions but does not override the fixed
criteria or supply human promotion approval.
