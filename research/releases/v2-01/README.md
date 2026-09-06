# SearchMate v2-01 release check

This branch prepares the exact, locally tested v2-01 candidate for a manual validation upload. It does not upload to the competition. Linux compatibility is pending in this initial preparation commit; a later STATUS.md and completion record will report the actual result.

The selected player is `research/releases/v2-01/player/agent.py`. Its identical tested snapshot is `research/runs/v2-01/candidate/agent.py`. Root `agent.py` remains the historical v0 baseline, so a root `make zip` would not produce this v2 release.

The local release ZIP is named `submission-v2-01.zip` and contains only `agent.py`. It is retained locally; the dedicated Linux workflow recreates the identical archive and preserves it as an Actions artifact. Agent SHA-256: `1bec488584769b1d58e9e9d38851d696c5285379e96390b468689131fc8b4cee`. ZIP SHA-256: `278d9818bbe5ac82427e5a483e4acbfde9cb98569f49aec74c2c99bac0bd9bde`.

The completed local evaluation passed the prospectively approved v2 gate: 70 wins, 33 draws and 25 losses versus v0 at short clocks, and 21 wins, 10 draws and 1 loss at full clocks. These are local comparisons, not a predicted competition rating. The local research records referenced by release.json are preserved in the original workspace; this branch publishes only the selected source and release checker, not private competition feedback or the evaluation corpus.

The dedicated `v2-01 Linux compatibility` workflow checks the extracted player using 96 fixtures, two fresh-process calls and two full-clock games, and verifies the effective Docker restrictions. Generic repository CI still checks root v0. The compatibility container is an approximation of the platform; dashboard validation after manual upload establishes acceptance.
