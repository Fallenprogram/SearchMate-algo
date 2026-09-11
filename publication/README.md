# SearchMate technical case study

**SearchMate: CPU chess engine development and competition results** is a standalone, project-authored report dated 11 September 2026. It includes the final qualification Swiss and can be read or shared without navigating this repository.

- [Read the PDF](SearchMate-technical-case-study.pdf).
- [Download the editable Word document](SearchMate-technical-case-study.docx).
- [Read the manuscript as text](manuscript.md).
- [Find the evidence behind each section](EVIDENCE_GUIDE.md).

The report explains original compiled search, classical and neural evaluation, failed experiments, local qualification, endgame maintenance, rated results and the final Swiss. SearchMate finished **103rd of 334, with 7.5/13 points**. The qualification goal was not reached. The report treats this as an engineering case study, without claiming a measured causal effect from research memory or the neural component alone.

This is a technical report, **not a peer-reviewed paper**. The author label is **SearchMate project**. No individual authorship, university affiliation or DOI has been inferred. Human direction and AI assistance are disclosed in the manuscript.

## Two complementary forms

The PDF is the stable reading and sharing edition; the DOCX is editable. GitHub holds versioned manuscript source, figures, evidence and release identities. The earlier [research retrospective](../research/RETROSPECTIVE.md) remains a historical account ending at rated round 109. It was not silently rewritten with post-competition knowledge.

| Material | Where it belongs |
|---|---|
| Narrative and reflection | This standalone report |
| Exact submitted engine and model | [Final v39 release](../research/releases/final-internal-v39-01/README.md) |
| Local campaigns and failed studies | [Research chronology](../research/studies/README.md) |
| Ladder observations | [Rated record through 109](../research/rated-results/README.md) |
| Final qualification results | [Swiss rounds 1–13](../research/tournament-results/README.md) |
| Reproduction limits and source mapping | [Evidence guide](EVIDENCE_GUIDE.md) |

## Preparing a future publication

1. Choose the intended venue and confirm the author's preferred name and any valid affiliation. Adapt the report to its format and authorship/AI-assistance requirements.
2. Keep the current case-study claims distinct from future experiments. A causal neural contribution needs a matched ablation; a causal research-memory benefit needs a controlled comparison. Neither follows from the current rating graph.
3. If game-level explanations of the Swiss losses are desired, first preserve and replay those PGNs and runtime logs. This update records public outcomes and does not claim that audit has been completed.
4. Create a dated revision and, if desired, a user-approved archival deposit. No journal submission, DOI registration or third-party publication was performed here.

Suggested citation: **SearchMate project. (2026). SearchMate: CPU chess engine development and competition results. Technical report, 11 September 2026.** Cite the specific repository commit when using its evidence.

## Figures and document checks

[make_figures.py](figures/make_figures.py) renders both figures from the public Swiss JSON and frozen v31 accuracy metrics. It needs Matplotlib 3.11.1; it imports no chess engine. PNG and SVG exports are included. Run from any working directory with `python publication/figures/make_figures.py`.

The Word report adapts the selected Design Report template. Original styles, embedded fonts, numbering, headers/footer geometry and section layout are retained. Its contents fields were refreshed with Word, and the exported PDF was visually inspected page by page. [Publication manifest](manifest.json) records artifact identities. Engine source, weights, release ZIPs and harness remain unchanged.
