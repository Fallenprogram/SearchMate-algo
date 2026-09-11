"""Static checks for the retrospective; never imports a chess player."""

import ast
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, cast
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
RESEARCH = ROOT / "research"
DOCS = [
    "README.md",
    "research/README.md",
    "research/CURRENT_STATE.md",
    "research/WORKING_MEMORY.md",
    "research/EXPERIENTIAL_MEMORY.md",
    "research/RETROSPECTIVE.md",
    "research/DOCUMENTATION_AUDIT_2026-09-11.md",
    "research/releases/README.md",
    "research/studies/README.md",
    "research/rated-results/README.md",
    "research/figures/README.md",
    "research/releases/final-internal-v39-01/README.md",
    "research/archive/pre-retrospective-2026-09-11/README.md",
]


def read(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    checks = []
    data = read(RESEARCH / "rated-results/rated-results-26-109.json")
    games = data["games"]
    assert [g["round"] for g in games] == list(range(26, 110))
    counts = Counter(g["result"] for g in games)
    assert counts == {"win": 35, "draw": 18, "loss": 30, "void": 1}
    assert counts == data["totals"]
    assert counts["win"] + counts["draw"] / 2 == data["points"] == 44
    assert data["scored_games"] == 83
    for group in data["version_groups"]:
        members = [g for g in games if g["attribution"] == group["attribution"]]
        assert [g["round"] for g in members] == group["rounds"]
        count = Counter(g["result"] for g in members)
        assert (count["win"], count["draw"], count["loss"], count["void"]) == (
            group["wins"],
            group["draws"],
            group["losses"],
            group["voids"],
        )
        assert group["points"] == count["win"] + count["draw"] / 2
        assert group["scored_games"] == len(members) - count["void"]
    assert all(not g["per_game_build_hash_verified"] for g in games)
    assert games[80 - 26]["attribution"] == "v14_or_v16_uncertain"
    assert games[106 - 26]["attribution"] == "unassigned"
    assert games[-1]["displayed_rating_after_round"] == data["profile"]["rating"] == 1723
    with (RESEARCH / "rated-results/rated-results-26-109.csv").open(
        encoding="utf-8", newline=""
    ) as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == len(games)
    for row, game in zip(rows, games, strict=True):
        for key, value in row.items():
            assert str(game[key]) == value, (game["round"], key)
    checks.append(
        "84 unique ordered rated records; 83 scored; totals, groups, uncertainties and CSV agree"
    )

    for row in read(RESEARCH / "figures/qualification-data.json")["campaigns"]:
        for stage in ("short", "full"):
            assert all(isinstance(row[stage][x], int) for x in ("wins", "draws", "losses"))
    campaign = read(RESEARCH / "figures/qualification-data.json")["campaigns"][-1]
    v37 = read(RESEARCH / "releases/competition-v6-internal-v37-01/games.json")
    for stage in ("short", "full"):
        for key in ("wins", "draws", "losses"):
            assert campaign[stage][key] == v37["stages"][stage][key]
    neural = read(RESEARCH / "figures/neural-data.json")["models"][-1]
    metrics = read(RESEARCH / "releases/competition-v6-internal-v37-01/model-accuracy.json")[
        "metrics"
    ]
    for stage in ("validation", "test"):
        assert neural[stage]["baseline"] == round(metrics[stage]["baseline_mae"], 2)
        assert neural[stage]["hybrid"] == round(metrics[stage]["candidate_mae"], 2)
    checks.append("V37 game chart and v31 accuracy chart agree with frozen public evidence")

    archive = read(RESEARCH / "archive/pre-retrospective-2026-09-11/manifest.json")
    for item in archive["files"]:
        assert digest(ROOT / item["archive_path"]) == item["sha256"]
    checks.append(f"{len(archive['files'])} replaced front pages preserved by SHA-256")

    links = 0
    for rel in DOCS:
        path = ROOT / rel
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
            if re.match(r"[a-z]+:", target) or target.startswith("#"):
                continue
            target = unquote(target.split("#", 1)[0]).strip("<>")
            dest = (path.parent / target).resolve()
            assert dest.is_relative_to(ROOT), (rel, target)
            assert dest.exists(), (rel, target)
            links += 1
    checks.append(f"{links} relative documentation/image links resolve inside repository")
    for name in ("rated-history", "local-qualification", "neural-generalization"):
        assert (RESEARCH / f"figures/{name}.png").read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
        assert b"<svg" in (RESEARCH / f"figures/{name}.svg").read_bytes()
    ast.parse((RESEARCH / "figures/make_figures.py").read_text(encoding="utf-8"))
    checks.append("Three PNG/SVG pairs present; plotting script parses without importing it")
    print(
        json.dumps(
            {"passed": True, "checks": checks, "engine_imports": 0, "searches": 0, "new_games": 0},
            indent=2,
        )
    )


if __name__ == "__main__":
    verify()
