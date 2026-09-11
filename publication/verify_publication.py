"""Check published result/document integrity using only the standard library."""

import csv
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from typing import Any, cast
from urllib.parse import unquote
from zipfile import ZipFile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def read(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def main() -> None:
    record = read(ROOT / "research/tournament-results/swiss-110-122.json")
    games = record["games"]
    assert [game["event_number"] for game in games] == list(range(110, 123))
    assert [game["swiss_round"] for game in games] == list(range(1, 14))
    counts = Counter(game["result"] for game in games)
    assert counts == {"win": 7, "draw": 1, "loss": 5}
    assert record["points"] == counts["win"] + counts["draw"] / 2 == 7.5
    assert record["rank"] == 103 and record["field_size"] == 334
    assert record["buchholz"] == 90 and record["displayed_swiss_rating"] == 1872
    cumulative = 0.0
    for game in games:
        points = {"win": 1.0, "draw": 0.5, "loss": 0.0}[game["result"]]
        cumulative += points
        assert points == game["points"] and cumulative == game["cumulative_points"]
        assert game["per_game_build_hash_verified"] is False
    for color in ("white", "black"):
        c = Counter(g["result"] for g in games if g["color"] == color)
        assert all(record["color_results"][color][key] == c[key] for key in counts)
    for singular, plural in (("win", "wins"), ("draw", "draws"), ("loss", "losses")):
        assert (
            record["previous_ladder"][plural] + counts[singular]
            == record["combined_profile_record_after_swiss"][plural]
        )
    with (ROOT / "research/tournament-results/swiss-110-122.csv").open(
        encoding="utf-8", newline=""
    ) as file:
        rows = list(csv.DictReader(file))
    assert len(rows) == 13
    for row, game in zip(rows, games, strict=True):
        for key, value in row.items():
            assert str(game[key]) == value, (game["swiss_round"], key)
    manifest = read(HERE / "manifest.json")
    for item in manifest["files"]:
        path = HERE / item["path"]
        assert path.stat().st_size == item["bytes"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"]
    docx = HERE / "SearchMate-technical-case-study.docx"
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    with ZipFile(docx) as archive:
        assert archive.testzip() is None
        document = ET.fromstring(archive.read("word/document.xml"))
        text = " ".join(t.text or "" for t in document.findall(".//w:t", ns))
        assert len(document.findall(".//w:sectPr", ns)) == 2
        for forbidden in ("Lorem ipsum", "[Author]", "Report title", "Source placeholders"):
            assert forbidden not in text
        for phrase in ("103rd", "334 teams", "7.5", "592 parameters", "not peer reviewed"):
            assert phrase in text, phrase
        for number in range(1, 13):
            assert f"[{number}]" in text
        assert len(document.findall(".//w:hyperlink", ns)) == 20
    assert (HERE / "SearchMate-technical-case-study.pdf").read_bytes().startswith(b"%PDF-")
    docs = [*HERE.glob("*.md"), ROOT / "research/tournament-results/README.md"]
    link_count = 0
    for path in docs:
        for link in re.findall(r"\[[^\]]*\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            if re.match(r"[a-z]+:", link) or link.startswith("#"):
                continue
            target = (path.parent / unquote(link.split("#")[0]).strip("<>")).resolve()
            assert target.is_relative_to(ROOT) and target.exists(), (path, link)
            link_count += 1
    print(
        json.dumps(
            {
                "passed": True,
                "swiss_games": 13,
                "points": 7.5,
                "rank": "103/334",
                "artifact_hashes": len(manifest["files"]),
                "document_links": link_count,
                "toc_anchors": 20,
                "engine_imports": 0,
                "new_games": 0,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
