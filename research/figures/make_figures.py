"""Rebuild retrospective figures from published data; no engine imports or calls.

Run: python research/figures/make_figures.py
Dependency: matplotlib==3.11.1 (see requirements.txt).
"""

import json
from pathlib import Path
from typing import Any, cast

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.patches import Patch
from matplotlib.ticker import PercentFormatter

HERE = Path(__file__).resolve().parent
plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": False,
        "axes.edgecolor": "#d8e0e8",
        "axes.labelcolor": "#24364b",
        "text.color": "#18304b",
        "xtick.color": "#42566d",
        "ytick.color": "#42566d",
        "axes.titleweight": "bold",
        "svg.fonttype": "none",
        "svg.hashsalt": "searchmate-retrospective-20260911",
        "savefig.facecolor": "white",
    }
)


def read(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def save(fig: Figure, name: str) -> None:
    fig.savefig(
        HERE / f"{name}.png",
        dpi=180,
        bbox_inches="tight",
        metadata={"Software": "SearchMate documentation figure script"},
    )
    fig.savefig(
        HERE / f"{name}.svg",
        bbox_inches="tight",
        metadata={"Date": None, "Creator": "SearchMate documentation figure script"},
    )
    vector_path = HERE / f"{name}.svg"
    vector = vector_path.read_text(encoding="utf-8")
    vector_path.write_bytes(
        ("\n".join(line.rstrip() for line in vector.splitlines()) + "\n").encode("utf-8")
    )
    plt.close(fig)


def rated_history() -> None:
    data = read(HERE.parent / "rated-results/rated-results-26-109.json")
    games = data["games"]
    fig, ax = plt.subplots(figsize=(12, 5.8))
    fig.subplots_adjust(top=0.78, bottom=0.22, left=0.08, right=0.95)
    fig.suptitle(
        "SearchMate in rated play: the observed trajectory",
        x=0.08,
        y=0.98,
        ha="left",
        fontsize=19,
        weight="bold",
    )
    fig.text(
        0.08,
        0.916,
        "Rounds 26\u2013109 · frozen 11 September 2026 · 35W / 18D / 30L + 1 void",
        fontsize=11,
    )
    spans = [
        (25.5, 35.5, "v0 (provisional)", "#b6c2d0"),
        (35.5, 53.5, "v2", "#70a8dc"),
        (53.5, 75.5, "v7", "#72c1c5"),
        (75.5, 79.5, "v14", "#9fc677"),
        (80.5, 105.5, "v16.1", "#b69add"),
        (106.5, 109.5, "v39", "#e9af6e"),
    ]
    for start, end, _label, color in spans:
        ax.axvspan(start, end, color=color, alpha=0.24, lw=0, zorder=0)
    for start, end in [(79.5, 80.5), (105.5, 106.5)]:
        ax.axvspan(start, end, facecolor="white", edgecolor="#939ba5", hatch="////", lw=0, zorder=0)
    ax.plot(
        [g["round"] for g in games],
        [g["displayed_rating_after_round"] for g in games],
        color="#204f80",
        lw=2.4,
    )
    ax.scatter([109], [1723], color="#c67220", s=45, zorder=4)
    ax.annotate(
        "1723\nrank 182 / 465",
        xy=(109, 1723),
        xytext=(99, 1765),
        ha="right",
        fontsize=10,
        color="#9c5418",
        arrowprops={"arrowstyle": "-", "color": "#c67220"},
    )
    ax.set(xlim=(25.5, 110), ylim=(1230, 1810), ylabel="Displayed rating", xlabel="Rated round")
    ax.set_xticks([26, 35, 45, 55, 65, 75, 85, 95, 105, 109])
    ax.set_yticks([1250, 1375, 1500, 1625, 1750])
    ax.grid(axis="y", color="#e1e7ed", lw=0.7)
    ax.set_axisbelow(True)
    legend = [Patch(facecolor=color, alpha=0.6, label=label) for _, _, label, color in spans]
    legend.append(
        Patch(facecolor="white", edgecolor="#939ba5", hatch="////", label="Uncertain build")
    )
    fig.legend(
        handles=legend,
        loc="upper left",
        bbox_to_anchor=(0.073, 0.885),
        ncol=7,
        frameon=False,
        fontsize=9,
        handlelength=1.2,
        columnspacing=1.2,
    )
    fig.text(
        0.08,
        0.075,
        "Build ranges follow user history, not per-game hashes. Round 80 and round "
        "106 remain uncertain.",
        fontsize=9,
    )
    fig.text(
        0.08,
        0.036,
        "Current rating is fitted to the current build; the historical curve spans "
        "submissions. This is not a controlled Elo-gain plot.",
        fontsize=9,
    )
    save(fig, "rated-history")


def local_qualification() -> None:
    data = read(HERE / "qualification-data.json")["campaigns"]
    fig, ax = plt.subplots(figsize=(10.8, 5.8))
    fig.subplots_adjust(top=0.77, bottom=0.22, left=0.09, right=0.98)
    fig.suptitle(
        "Three successful local predecessor comparisons",
        x=0.09,
        y=0.98,
        ha="left",
        fontsize=18,
        weight="bold",
    )
    fig.text(
        0.09,
        0.914,
        "Candidate points ÷ games · draws count as half a point · each comparison "
        "uses a different campaign",
        fontsize=10,
    )
    for offset, stage, color in [(-0.19, "short", "#3476a8"), (0.19, "full", "#20867f")]:
        values = []
        labels = []
        for row in data:
            d = row[stage]
            n = d["wins"] + d["draws"] + d["losses"]
            points = d["wins"] + d["draws"] / 2
            values.append(points / n)
            labels.append(f"{points:g}/{n}\n{d['wins']}W {d['draws']}D {d['losses']}L")
        bars = ax.bar([x + offset for x in range(len(data))], values, width=0.33, color=color)
        for bar, label in zip(bars, labels, strict=True):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.025,
                label,
                ha="center",
                va="bottom",
                fontsize=9,
            )
    ax.set_xticks(
        range(len(data)), [f"{d['candidate']} vs {d['comparator']}" for d in data], fontsize=12
    )
    ax.set_ylim(0, 1.14)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1])
    ax.yaxis.set_major_formatter(PercentFormatter(1))
    ax.set_ylabel("Candidate points / games")
    ax.grid(axis="y", color="#e1e7ed", lw=0.7)
    ax.set_axisbelow(True)
    fig.legend(
        handles=[
            Patch(color="#3476a8", label="Short: 10s + 0.1s"),
            Patch(color="#20867f", label="Full: 120s + 0.5s"),
        ],
        loc="upper left",
        bbox_to_anchor=(0.085, 0.882),
        ncol=2,
        frameon=False,
    )
    fig.text(
        0.09,
        0.085,
        "Different opponents, roots, sample sizes and selection histories: these "
        "bars are not directly comparable Elo estimates.",
        fontsize=9,
    )
    fig.text(
        0.09,
        0.045,
        "Final v39 inherited v37, then passed targeted maintenance checks; v39 did "
        "not repeat this broad strength screen.",
        fontsize=9,
    )
    save(fig, "local-qualification")


def neural_generalization() -> None:
    data = read(HERE / "neural-data.json")["models"]
    fig, axes = plt.subplots(1, 3, figsize=(12, 5.8), sharey=True)
    fig.subplots_adjust(top=0.69, bottom=0.24, left=0.07, right=0.98, wspace=0.2)
    fig.suptitle(
        "Neural evaluation: held-out accuracy across three attempts",
        x=0.07,
        y=0.98,
        ha="left",
        fontsize=18,
        weight="bold",
    )
    fig.text(
        0.07,
        0.915,
        "Group-balanced mean absolute error · lower is better · compare bars within each study",
        fontsize=11,
    )
    for ax, row in zip(axes, data, strict=True):
        for offset, kind, color in [(-0.18, "baseline", "#b0beca"), (0.18, "hybrid", "#346f9b")]:
            values = [row[s][kind] for s in ["validation", "test"]]
            bars = ax.bar([x + offset for x in range(2)], values, width=0.31, color=color)
            for bar, value in zip(bars, values, strict=True):
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    value + 4,
                    f"{value:.1f}",
                    ha="center",
                    fontsize=9,
                )
        ax.set_title(
            f"{row['model']} · {row['parameters']:,} parameters\n{row['representation']}",
            fontsize=11,
            pad=16,
        )
        ax.set_xticks([0, 1], ["Validation", "Test"])
        ax.set_ylim(0, 220)
        ax.grid(axis="y", color="#e1e7ed", lw=0.7)
        ax.set_axisbelow(True)
    axes[0].set_ylabel("Mean absolute error (reference cp)")
    fig.legend(
        handles=[
            Patch(color="#b0beca", label="Classical baseline"),
            Patch(color="#346f9b", label="With trained residual"),
        ],
        loc="upper left",
        bbox_to_anchor=(0.063, 0.879),
        ncol=2,
        frameon=False,
    )
    fig.text(
        0.07,
        0.105,
        "V29 overfit; v30 missed the 2% improvement gate. V31 passed accuracy but "
        "failed its own short-game screen.",
        fontsize=10,
    )
    fig.text(
        0.07,
        0.056,
        "Datasets differ: absolute errors across models are not a controlled "
        "architecture comparison. V31's weights were retained through v39.",
        fontsize=9,
    )
    save(fig, "neural-generalization")


if __name__ == "__main__":
    rated_history()
    local_qualification()
    neural_generalization()
    print("Wrote three PNG and three SVG figures from published data.")
