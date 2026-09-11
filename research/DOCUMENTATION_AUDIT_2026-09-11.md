# Retrospective publication: provenance and verification

This is a documentation-only update based on records already collected. It creates a technical essay, consolidates the rated inventory through 109, renders three figures, and replaces conflicting front-page “current” statements with one [current state](CURRENT_STATE.md). It does not resume engine development, query a reference engine, fit weights or play games.

## Corrections and preservation

| Earlier ambiguity | Published correction |
|---|---|
| “The trained neural component first appeared in v31” | Neural experiments began with v29/v30. V31 trained the particular network retained in v37–v39 |
| Root working memory still called v0 the current champion | The current state is final user-confirmed v39; old m0 pages are archived intact |
| An overall rating was described as spanning builds | The current rating is fitted to the current build under the live rule description; cumulative W/D/L and the historical graph span submissions |
| Good v20 scores against v14 could imply a recommendation over v16.1 | The direct v20–v16.1 screen failed; the old comparator evidence does not establish superiority |
| V37 game results could be read as v39's own broad screen | V37's broader qualification and v39's targeted maintenance/smoke evidence are kept separate |
| “Through 90” index presented as the latest inventory | A new through 109 inventory preserves the old snapshots and explicit evidence levels |

Seven replaced pages were copied byte-for-byte to the [archive](archive/pre-retrospective-2026-09-11/README.md), with SHA-256 identities and source commit in its manifest. Existing dated research reports, prior inventories, release payloads and harness files were not rewritten. The final release README was corrected, but its archive, source, model, assets, manifests, PGNs and evidence remain unchanged. The ledger receives an appended publication event; its prior bytes are retained.

## Source hierarchy and access

The narrative draws first on the dated public progress reports and exact release evidence linked in the [reading guide](README.md). Where an intermediate study was previously private, its selected result is reproduced in the [study chronology](studies/README.md), and the [source-identity file](studies/retrospective-source-identities.json) identifies the retained original report by hash. A hash is an identity claim, not access to the underlying private evidence.

The rated consolidation merges the preserved 26–90 inventory with the saved public through 109 profile. For rounds 93–104, it includes content identities from the already completed PGN/log replay audit. Round 105 has a supplied log but no supplied PGN. Public-only results are marked as such. The saved profile's URL, timestamp and source hash are in the [new inventory](rated-results/rated-results-26-109.json). Its numeric rating history was extracted from text; no screenshot measurements or inferred missing ratings were inserted.

The figure data cites its campaign sources. V29/v30 accuracy figures come from their retained reports; v31 comes from the frozen public model accuracy record. These studies have different datasets and are not presented as a controlled architecture comparison. Rounded metrics are sufficient to reproduce the displayed figures, not full precision training results.

The live [contract](https://aichessathon.com/docs/agent-contract.md) and [rules](https://aichessathon.com/docs/rules.md) supply the dated competition constraints and rating interpretation. The publication cutoff contains ladder observations only; no Swiss outcome or personal eligibility claim is included.

## Checks performed

- Recomputed the 84-round inventory, 83 scored games, 35W/18D/30L, 44 points and each provisional version group. CSV and JSON must agree.
- Compared v37 chart counts and retained-network MAE with frozen public evidence; checked v2 time controls against its retained manifest.
- Checked new/current Markdown links and image paths, JSON parsing, archive identities and plotting-script syntax.
- Rendered and visually inspected all three figures in PNG; saved matching SVGs for export. The finalized script reproduced all six files byte-for-byte in the recorded documentation environment.
- Ruff passed for both new documentation scripts. Strict mypy passed with third-party imports skipped/ignored where unavailable in the engine environment; this is not a type audit of Matplotlib itself.
- Ran the final release's static artifact verifier, covering its exact ZIP, nine payloads, source syntax and smoke PGN hashes, without importing the player.
- Compared all tracked pre-edit files by SHA-256: 822 retained their exact bytes. Only seven declared documentation pages and the appended ledger event changed. The prior ledger prefix was preserved. Release payloads, dated reports and harness retained their identities.

The portable [verification script](verify_documentation.py) checks inventory arithmetic, chart/evidence consistency, archived pages and local links. Run `python research/verify_documentation.py` in a fresh clone. Separately, `python research/releases/final-internal-v39-01/verify_artifacts.py` checks the unchanged final artifact. Neither script performs a chess search.

These static checks support accurate publication; they are not a new engine qualification. The repository still does not publish the bulk training/reference corpus, private runtime logs, machine identifiers, sealed inputs or unqualified candidate payloads. Complete historical training reproduction is therefore outside this public bundle. Recuris's causal playing-strength benefit remains unmeasured.
