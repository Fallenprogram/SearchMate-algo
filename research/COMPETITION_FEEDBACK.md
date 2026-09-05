# Using competition feedback in SearchMate research

Written and sources checked: **2026-09-05**. This is a workflow guide, not a
record of an upload, validation result, or leaderboard result. It does not change
the frozen v0 protocol, promote a champion, or approve a v1 experiment.

## What the official sources say

The official [homepage FAQ](https://aichessathon.com/) describes training data
as unrestricted, including positions annotated by an existing engine. The
[technical documentation](https://aichessathon.com/docs) permits training your
own network on engine-labelled positions. It prohibits shipping a third-party
engine or published chess network, including a port or wrapper, and prohibits a
database of engine moves or evaluations used for lookup during play. Source must
remain explainable. These are constraints on the submitted player; they do not
amount to a blanket prohibition on learning from game results.

The [rules](https://aichessathon.com/terms), version **2026-08-31.v3**, prohibit
accessing hidden match data, another entrant's systems, or credentials, and
prohibit manipulated pairings and coordinated outcomes. They allow publication
of factual event records. The Daily Five puzzle challenge has separate rules
against outside assistance; this guide concerns rated **agent games**.

**Interpretation:** analysing our own legitimately available rated-game PGNs,
logs, and outcomes to improve original SearchMate code is consistent with those
published provisions. The pages do not explicitly name RSI or authorize every
possible data-use method. Do not extend this interpretation to hidden data,
unauthorized access, opponent-engine copying, or shipping a move lookup database.
Recheck the official sources before a materially different method or submission.

The requested canonical endpoints
[agent-contract.md](https://aichessathon.com/docs/agent-contract.md) and
[rules.md](https://aichessathon.com/docs/rules.md) were unavailable through the
browsing tool on this date. The linked official HTML pages were retrieved as
fallbacks. This guide makes no claim that unavailable text was inspected.

## What counts as success after your manual upload

Treat these as separate observations:

1. **Accepted submission:** inspect the dashboard's validation status and save
   its log. Official validation builds the entry and plays a smoke game in each
   colour. The latest submission that passes validation is the one used for
   play. [Official submission documentation](https://aichessathon.com/docs)
2. **Observed platform reliability:** confirm actual rated games use the intended
   version, where the dashboard exposes that association. Check their termination
   and timing records. A clean loss is evidence that the player ran; a crash,
   illegal move, or clock failure calls for a reliability investigation. Passing
   validation alone is not evidence of reliability in every future game.
3. **Observed competitive performance:** record wins, draws, losses, opponent,
   colour, game count, rating, and observation time for that version. The ladder
   uses Glicko-2; its displayed number resembles Elo.
   [Official scoring documentation](https://aichessathon.com/docs)
4. **Evidence that v1 improved:** apply the separately approved, predeclared local
   candidate gate against the approved champion. A leaderboard appearance proves
   participation, and a rising number is encouraging, but changing opponents and
   small samples make it insufficient to establish a causal improvement.

The documentation says the team's dashboard provides each rated game's PGN and a
private log with initialization time, move times, and remaining clocks.
[Official wire-protocol documentation](https://aichessathon.com/docs)
Prefer those records over a rating screenshot alone. If an association or field
is not exposed, record **unknown** rather than guessing. Preserve the exact
uploaded ZIP locally so its SHA-256 identifies what was actually submitted.

## What to bring back to this task

After uploading manually, paste the completed template below and attach exported
PGNs and logs, or give their local paths. Public game links are useful too. A
dashboard screenshot can establish visible status when export is unavailable;
it does not replace move and timing records for diagnosis. Start with the
validation result, then supply all available games from a stated interval,
including wins, draws, losses, and failures. Do not select only interesting wins
or losses when reporting aggregate performance.

```text
SearchMate platform feedback

Player version / champion identifier:
Git commit:
agent.py SHA-256:
Uploaded ZIP filename:
Uploaded ZIP SHA-256:
Upload date, time, and timezone:
Submission ID / version shown by the site (or unknown):
Validation status and time:
Validation log attachment / local path:

Observation window, with timezone:
Team name / leaderboard link:
Displayed rating at start and end (include timestamps):
Displayed rank and field size, if available:
Total rated games for this version in this window:
Wins / draws / losses / voids:
Missing or unavailable records:

For each game, or in an attached table:
- Game ID / link and start time
- Submission version association: shown by site / inferred / unknown
- Opponent and displayed rating, if available
- SearchMate colour, result, and exact termination reason
- PGN attachment / local path
- Own-team log attachment / local path
- Initialization time, move times, and remaining clock if available
- Any organizer rerun, correction, or infrastructure notice

Question or pattern you noticed (optional):
```

Keep raw observations unchanged and record corrections separately. Hash received
files and preserve their source and receipt time in a new platform-feedback
bundle; append a reference in the experiment ledger and platform observations.
Do not add results into the completed `runs/v0-01` campaign. Label inferred build
associations explicitly, particularly around an upload change. Account secrets
are unnecessary; remove credentials or session links before sharing. Private
dashboard logs need not be published to GitHub to be useful for local research.

## How feedback becomes an RSI experiment

Competition outcomes are useful feedback for the **Researcher**, which operates
between builds. The v0 Player does not change its own code or learn between
competition games. There is no automatic rating-to-code or loss-to-lesson step.

Follow the existing [research protocol](RESEARCH_PROTOCOL.md):

1. **Record the observation.** For example: a supplied log shows a clock loss,
   or several supplied PGNs show a recurring tactical failure. Keep the complete
   evidence and separate player, opponent, and infrastructure causes.
2. **Form one bounded hypothesis.** Identify one primary subsystem and explain
   what code behaviour might cause the pattern. An observed loss does not prove
   that the proposed explanation is correct.
3. **Declare the test before changing code.** Specify the evidence supplied,
   hypothesis, target metric, numeric success threshold, test positions and
   budgets, player and memory versions, and researcher configuration. Use
   competition positions as labelled development examples.
4. **Build an isolated candidate after the v1 protocol is approved.** Run the
   targeted diagnostic, safety checks, fresh champion comparison, and regression
   checks required by the frozen gate. Keep every attempt and the exact code
   hash. The [v1 gate document](V1_GATE_PROPOSAL.md) is currently a proposal.
5. **Calculate the declared decision and review it.** Gate failure or inconclusive
   evidence leaves the champion unchanged. Human approval remains a separate
   promotion decision.
6. **Update memory only with supported lessons.** A successful code patch can
   justify a narrowly scoped lesson after evidence review. It does not by itself
   prove the diagnosis or prove that evolving memory caused the improvement.

The meaningful research signal is the collection of measured outcomes: platform
acceptance, runtime reliability, the targeted repair metric, and the fixed local
comparison. Rating is contextual evidence, not a replacement for those checks.

## Development evidence and untouched final evaluation

Our research plan imposes a separation that is distinct from competition rules.
Once the Researcher sees a competition result or PGN and uses it to guide a patch,
that material becomes **development/evolution evidence**. Record the lineage as
**platform-adaptive**. It cannot also be described as an untouched final test.

Keep the reserved final evaluation unavailable until candidate selection ends.
If a later patch uses that final result, relabel it as development evidence and
reserve a new untouched final evaluation before making another final-test claim.
Exposing competition feedback does not prohibit continued research; it changes
which independence claims the evidence can support. The deferred matched
comparison against frozen memory is still needed for a causal claim about RSI
memory, as described in the existing protocol.

No platform feedback has been imported by creating this guide, and no accepted
memory lesson has been added.
