# Proposed v1 admission gate — NOT APPROVED

Draft: **2026-09-05**. Status: **recommendation for user review only**.

This document does not authorize v1 work, change the frozen v0 gate, select test
positions, or promote a champion. It completes the approved v0 deliverable's
recommendation for a later numeric gate. The user must first approve v0 as the
initial champion and approve the exact v1 protocol, executable gate, and budgets.
The proposal may be revised or rejected before that approval.

## Proposed fixed budget

Allow at most **four formal candidate evaluations** under this gate version. Each
candidate changes one diagnosed primary subsystem and is evaluated against the
then-current approved champion. Freeze the schedule, source and opponent hashes,
clock settings, decision code, and evidence boundaries before evaluation.

| Component | Games per formal candidate | Clock per side |
|---|---:|---|
| Candidate versus approved champion: 64 opening pairs | 128 | 10,000 ms + 100 ms/move |
| Reference regression: candidate and champion each play 8 pairs against each of greedy, minimax, and numba | 96 | 10,000 ms + 100 ms/move |
| Candidate safety against random: 32 opening pairs | 64 | 10,000 ms + 100 ms/move |
| Candidate full-clock safety: 2 pairs each against greedy and minimax | 8 | 120,000 ms + 500 ms/move |
| **Total** | **296** | **288 short-clock; 8 full-clock** |

This totals at most **1,184 scheduled games across four formal candidates**,
before separately declared targeted diagnostics, non-game checks, or any later
final evaluation. The regression allocation includes the champion's reference
games; they are not assumed to be free. Reuse is permissible only if its exact
scope is approved in advance and the champion hash, positions, reference hashes,
clocks, and other relevant configuration match. Otherwise run the entire budget.

Run games sequentially, reverse candidate colors within each pair, and preserve
every attempt, PGN, timing record, command, and hash. A formal candidate gets one
fixed sample: no extra games, borderline retries, or repetition of an identical
deterministic matchup to manufacture more independent evidence. A proposed
extension would require a new approved testing plan before additional evidence.

## Champion comparison

Before v1, freeze **four disjoint blocks of 64 distinct opening positions**, one
previously unused block for each formal candidate. Keep these separate from
evolution evidence and the reserved final set. Do not choose or replace positions
after seeing candidate results. Select the block construction/sampling procedure
and its provenance before candidate optimization.

For each opening pair, let `s` be the candidate's points from its two games,
counting a win as 1, a draw as 0.5, and a loss as 0:

- Favorable pair: `s > 1`.
- Unfavorable pair: `s < 1`.
- Tied pair: `s = 1`; exclude it from the sign test.

Let `f` be favorable pairs, `u` unfavorable pairs, and `n = f + u`. For `n > 0`,
calculate the exact one-sided paired sign-test tail:

```text
p = sum(comb(n, k) for k in range(f, n + 1)) / 2**n
```

The head-to-head component passes only when **both** conditions hold:

1. `p <= 0.0125`, using `0.05 / 4` for the maximum four formal evaluations.
2. Candidate points across all 128 games are at least **55%** of available points
   (at least **70.5 points**, given half-point scoring).

With no decisive pairs (`n = 0`), the result is **inconclusive**. Any result that
does not satisfy both criteria fails admission; a favorable but inconclusive
result is not a promotion pass. Report the complete pair-score distribution as
well as `f`, `u`, tied pairs, total points, and the exact tail probability.

The four-test correction bounds the family of formal tests only under valid
individual test assumptions. It does not cure biased opening selection, dependent
observations, or adaptive reuse of evidence. This is a conditional comparison on
the declared opening blocks: interpreting significance requires defensible
representative and independent sampling of opening pairs. It does not prove
universal chess superiority or an Elo gain. Short-clock evidence does not become
full-clock strength evidence.

## Reference regression guard

Freeze eight opening pairs for each reference opponent: greedy, minimax, and
numba. The candidate and champion each play all 16 games per opponent under the
same declared conditions.

For **each** opponent, require:

```text
candidate points >= champion points - 1.0
```

One point out of 16 games is **6.25 percentage points**. All three comparisons
must satisfy the margin. This is a descriptive regression guard, not a confidence
bound proving the absence of regression. Preserve baseline randomness limitations
where seeds are uncontrolled; pinned code and clocks alone do not guarantee
identical random choices. Reused reference evidence is development feedback and
must not be described as an untouched final test.

## Safety, targeted repair, and completion

Require all 64 random safety games, all eight full-clock safety games, and the
other designated games to complete without a candidate illegal/malformed reply,
crash, initialization failure, memory failure, or clock loss. **Any candidate
runtime failure rejects that candidate.** Preserve opponent or infrastructure
failures and resolve them explicitly; unresolved mandatory evidence means
incomplete. A retry cannot erase an observed player failure.

Also require the same 24 nonterminal wire fixtures at 20, 100, 1,000, and 10,000 ms
(96 legal, timely replies), relevant internal terminal/referee checks, fresh
imports, source/dependency and proposed-manifest review, lint, strict typing,
required unit tests, and unchanged-harness/input integrity. Freeze the executable
definitions along with the approved gate. The eight full-clock games establish
only observed reliability in those games.

Before each patch, declare the diagnosed failure, one primary subsystem, targeted
test data, exact numeric metric, and numeric improvement threshold. The targeted
repair must pass its predeclared criterion in addition to this outer gate. Record
the targeted diagnostic budget before running it; do not invent a new success
metric after seeing results. The outer admission criteria remain fixed across all
four formal candidates.

Admission requires every safety, targeted-repair, head-to-head, regression, and
evidence-integrity component to pass. The Researcher may explain the calculation
but cannot override it. A passing candidate still awaits **human champion
approval**. ZIP creation and upload retain their separate approval boundaries.

## Provisional time estimate

The completed **120-game v0 campaign** recorded **880.916 seconds** of summed game
durations and **1,001.114 seconds** of campaign wall time. Wall time includes the
calibration pause and evidence processing. Short games averaged **5.302 seconds**;
the eight full-clock games averaged **35.884 seconds**.
[Measured analysis](runs/v0-01/analysis.json)

| Measured v0 opponent, short clock | Mean game duration |
|---|---:|
| Random | 4.093 seconds |
| Greedy | 4.183 seconds |
| Minimax | 8.952 seconds |
| Numba | 11.037 seconds |

Applying the overall averages mechanically gives about **30.2 minutes**:

```text
288 × 5.302 seconds + 8 × 35.884 seconds ≈ 1,814 seconds
```

That calculation mixes many easy random/greedy games into the estimate for
head-to-head play. Candidate-versus-champion games remain uncalibrated and may be
longer. A more conservative planning model assigns them **twice the measured
minimax duration**. This multiplier is an explicit assumption, not a measurement:

```text
128 × (2 × 8.952)                  head-to-head proxy
+ 32 × (4.183 + 8.952 + 11.037)   both players' reference games
+ 64 × 4.093                      random safety
+ 8 × 35.884                      full-clock safety
≈ 3,614 seconds ≈ 60.2 minutes
```

Recommend provisionally **60–120 minutes of testing per formal candidate**, or
**4–8 hours for four candidates**, plus coding and separately budgeted targeted
tests. This replaces the early eight-game calibration estimate of 25–45 minutes
with full-campaign measurements and an allowance for uncertain head-to-head cost.
Initialization, longer games, checks, evidence processing, and machine load can
still extend runtime. These are planning estimates, not statistical guarantees
or time caps. Never truncate sample counts or relax the gate to meet an estimate.

## Final evidence and deferred control

Reserve a disjoint final test set before v1. Its positions, games, and scores stay
unavailable to the Researcher until candidate selection ends. Specify its budget
before use; it is outside the 296-game per-candidate allocation. A final result
used to guide another patch becomes development evidence.

The matched control remains deferred. Define it before v1 using the same initial
approved v0, researcher configuration, allowed evidence, candidate/game budgets,
position splits, and outer gate. Its clean sessions receive the **frozen initial
whole memory system**, including working-state rules, lessons, invocation policy,
and checkers; they must not receive the evolving arm's learned lessons or adapted
rules. Until that comparison exists, report measured player improvements without
claiming that evolving memory caused them.
