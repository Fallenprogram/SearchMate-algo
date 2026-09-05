# SearchMate invocation policy

Policy: **rho0**. Memory: **m0-bootstrap**. Recorded: **2026-09-05**.

This is the initial diagnostic routing policy. It specifies investigation steps,
not prevalidated skills or automatic code changes. Use permitted evolution
evidence and record the actual evidence and lesson IDs supplied to the Researcher.

| Observed evidence | Diagnostic | First evidence to inspect | Primary subsystem candidates |
|---|---|---|---|
| Illegal/malformed reply, exception, or crash | Reliability | Exact FEN, output, exception, legal moves, candidate hash | Reliability |
| Flag or excessive move duration | Time management | Clock before move, elapsed time, search completion/deadline diagnostics | Time management |
| Tactical loss | Search horizon | Representative PGN, forcing sequence, completed depth, terminal scores | Search or move ordering |
| Quiet deterioration | Evaluation | Position features and static scores from representative positions | Evaluation |
| Avoidable repetition or draw | Game state | Position history available to player, referee draw reason, FEN counters | Game-state memory |
| Import failure or package rejection | Competition contract | Fresh-process error, dependency manifest, proposed contents, live contract | Packaging/runtime compatibility |
| Inconclusive or contradictory results | Measurement quality | Paired counts, hashes, seeds, manifest, timings, failure attribution | Measurement infrastructure |

Choose exactly one primary subsystem before proposing a later candidate patch.
The table offers possibilities; it does not authorize mixing unrelated fixes.
Diagnose player, opponent, and infrastructure separately before attributing a
failure. If evidence does not distinguish explanations, record uncertainty and
gather a bounded diagnostic reproduction rather than declaring a lesson.

Change this policy only through an explicit evidence-backed memory patch with a
new version. The invocation policy cannot alter the frozen outer gate. A control
arm for the entire evolving memory system retains its frozen initial routing.
