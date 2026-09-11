# Reproducible retrospective figures

The [retrospective](../RETROSPECTIVE.md) embeds PNGs for convenient GitHub viewing. Matching SVGs retain vector text and geometry for reuse in a publication.

| Figure | Public data | Export |
|---|---|---|
| Rated trajectory | [84 per-round records](../rated-results/rated-results-26-109.json) | [PNG](rated-history.png), [SVG](rated-history.svg) |
| Local qualification | [Campaign counts and source links](qualification-data.json) | [PNG](local-qualification.png), [SVG](local-qualification.svg) |
| Neural accuracy | [Study-specific rounded MAE](neural-data.json) | [PNG](neural-generalization.png), [SVG](neural-generalization.svg) |

From a separate documentation environment, install [requirements.txt](requirements.txt), then run from the repository root:

```text
python research/figures/make_figures.py
```

The [script](make_figures.py) reads public JSON only. It imports no player, performs no training, reference query or chess search, and does not alter the engine environment. Matplotlib's raster rendering can vary with fonts/library versions; the numeric sources remain the authority.

The rating chart uses saved numeric profile values, not screenshot digitization. Current rating is fitted to the current build, while the historical series spans submissions. Version ranges are reported attribution, not verified per-game hashes. The local campaign chart keeps clocks and denominators separate. The neural chart compares each candidate with its own baseline; its three studies used different datasets. No figure supplies a causal Recuris estimate, component ablation or Elo forecast.
