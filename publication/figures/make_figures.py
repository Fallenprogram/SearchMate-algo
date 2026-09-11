"""Render publication figures from public evidence without importing an engine."""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parents[1] / "research"
INK = "#183C3B"
TEAL = "#257E77"
GRAY = "#838B8D"


def save(figure: plt.Figure, name: str) -> None:
    for extension in ("png", "svg"):
        figure.savefig(HERE / f"{name}.{extension}", dpi=220, facecolor="white")
    svg = HERE / f"{name}.svg"
    svg.write_bytes(
        ("\n".join(line.rstrip() for line in svg.read_text().splitlines()) + "\n").encode()
    )
    plt.close(figure)


def main() -> None:
    plt.rcParams.update(
        {"font.family": "DejaVu Sans", "font.size": 10, "svg.hashsalt": "searchmate-report"}
    )
    swiss = json.loads((RESEARCH / "tournament-results/swiss-110-122.json").read_text())
    games = swiss["games"]
    points = [0.0]
    for game in games:
        points.append(points[-1] + {"win": 1.0, "draw": 0.5, "loss": 0.0}[game["result"]])
    figure = plt.figure(figsize=(6.5, 6.3))
    figure.text(0.07, 0.94, "Final qualification Swiss", fontsize=17, color=INK)
    figure.text(0.07, 0.884, "103rd of 334 teams  |  7 wins  1 draw  5 losses", fontsize=11)
    axis = figure.add_axes((0.12, 0.23, 0.79, 0.57))
    axis.plot(range(14), points, marker="o", color=TEAL, linewidth=2.2, markersize=4.5)
    axis.annotate(
        "7.5 / 13",
        (13, 7.5),
        xytext=(-8, 12),
        textcoords="offset points",
        ha="right",
        fontsize=12,
        color=INK,
    )
    axis.set(
        xlim=(-0.25, 13.5),
        ylim=(-0.25, 9),
        xlabel="Swiss round",
        ylabel="Cumulative points",
        xticks=range(1, 14),
    )
    axis.spines[["top", "right"]].set_visible(False)
    axis.grid(axis="y", color="#E0E5E4", linewidth=0.7)
    axis.set_axisbelow(True)
    figure.text(0.07, 0.115, "White  6W / 0D / 0L     Black  1W / 1D / 5L", fontsize=10, color=INK)
    figure.text(
        0.07,
        0.069,
        "Public Final events 110-122  |  Recorded 11 September 2026",
        fontsize=8.5,
        color="#555555",
    )
    save(figure, "swiss-result")

    accuracy = json.loads(
        (RESEARCH / "releases/competition-v6-internal-v37-01/model-accuracy.json").read_text()
    )["metrics"]
    groups = ["validation", "test"]
    figure, axis = plt.subplots(figsize=(6.5, 2.65))
    figure.subplots_adjust(left=0.11, bottom=0.18, right=0.98, top=0.80)
    for offset, key, label, color in (
        (-0.18, "baseline_mae", "Classical evaluation", GRAY),
        (0.18, "candidate_mae", "Classical plus neural residual", TEAL),
    ):
        bars = axis.bar(
            [x + offset for x in range(2)],
            [accuracy[g][key] for g in groups],
            width=0.32,
            color=color,
            label=label,
        )
        axis.bar_label(bars, fmt="%.2f", padding=3, fontsize=10)
    axis.set(
        xticks=[0, 1],
        xticklabels=["Validation", "Test"],
        ylabel="Mean absolute error (cp)",
        ylim=(0, 200),
    )
    axis.spines[["top", "right"]].set_visible(False)
    axis.grid(axis="y", color="#E0E5E4", linewidth=0.7)
    axis.set_axisbelow(True)
    axis.legend(loc="lower center", bbox_to_anchor=(0.5, 1.13), ncols=2, frameon=False, fontsize=9)
    save(figure, "neural-accuracy")


if __name__ == "__main__":
    main()
