# Current SearchMate state — 11 September 2026

**Best locally qualified build: internal v37-01. Platform upload attempt: v6; acceptance pending after a build failure.** Short 12W/3D/1L, 13.5/16 points; full 7W/1D/0L, 7.5/8 points, against exact submitted v16.1. Zero faults and exact-package checks passed locally. [Release and ZIP](releases/competition-v6-internal-v37-01/README.md).

The log failed at `FROM aichessathon/agent-base:latest` with pull access denied, before agent import or smoke games. The user reports emailing the organizers and awaits their reply. This is no rules-rejection finding and does not establish platform approval. [Validation event](releases/competition-v6-internal-v37-01/platform-validation.json).

The last known user-confirmed submitted engine remains **v16.1/internal v16-01**, source `fdcdea36ad030dd534c2607408b399673d0fee728aeafc0ea456f96871f8f787`. [Rollback archive](releases/competition-v5-internal-v16-01/README.md). No updated deployment or subsequent rated-build attribution is inferred from an upload attempt.

V37 source: `e93e1b7a788cdd92237853621c219fab2c1d14fd85d5e034dd09b0c1c6e46953`.

V37 ZIP: `6cdee0bee1f877e5af1df0aa19b2444cfebc5163515872debb33c53b8cc8ecd3`.

The original 592-parameter model is reused unchanged from v31. V37's full combined build is qualified, while the historical v31-only and v36 screens remain failed. No causal component attribution, Elo prediction or resolution of every weakness is claimed. R82 defense and uncovered two-bishop conversion remain open. [Progress and provenance](PROGRESS_2026-09-11.md).

The local development goal is complete and its overnight follow-up paused. User upload/acceptance is the next step. At most one final focused endgame attempt may follow successful validation if enough time remains; it has not started. Do not interpret historical plans as instructions to launch another campaign.

The public [rated inventory](rated-results/README.md) still covers26–90. Round80's v14/v16 boundary remains uncertain. Private newer observations are not merged into that frozen public snapshot. Prior v20 source/ZIP remain private. Root `agent.py` is historical v0, and `harness/` and all previous release artifacts remain unchanged.

M1-P001 preserves identities and runtime/reset evidence; M1-P002 requires competitive evidence; M1-P003 retains counterevidence and bounded conclusions. Recuris's causal benefit remains unmeasured. No automatic competition upload occurs.
