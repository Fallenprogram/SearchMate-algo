"""Verify the exact final release without importing the chess engine."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify() -> None:
    release = Path(__file__).resolve().parent
    record = json.loads((release / "release.json").read_text(encoding="utf-8"))
    archive_path = release / record["zip_path"]
    archive = archive_path.read_bytes()
    assert digest(archive) == record["zip_sha256"], "ZIP hash mismatch"
    assert len(archive) == record["zip_bytes"], "ZIP size mismatch"
    expected = {item["path"]: item for item in record["members"]}
    assert set(expected) == {
        "agent.py", "evaluation.npz", "TABLEBASES.txt",
        "tables/KQvK.rtbw", "tables/KQvK.rtbz",
        "tables/KBBvK.rtbw", "tables/KBBvK.rtbz",
        "tables/KBvK.rtbw", "tables/KBvK.rtbz",
    }, "Unexpected payload manifest"
    with ZipFile(archive_path) as zipped:
        assert zipped.testzip() is None, "ZIP CRC failure"
        assert len(zipped.namelist()) == len(expected), "Duplicate ZIP member"
        assert set(zipped.namelist()) == set(expected), "Unexpected ZIP member"
        for name, item in expected.items():
            data = zipped.read(name)
            assert data == (release / "player" / name).read_bytes(), name
            assert len(data) == item["bytes"], name
            assert digest(data) == item["sha256"], name
        assert sum(zipped.getinfo(n).file_size for n in expected) == record[
            "uncompressed_bytes"
        ], "Uncompressed size mismatch"
    source = (release / record["agent_path"]).read_bytes()
    assert digest(source) == record["agent_sha256"], "Source identity mismatch"
    ast.parse(source, filename="agent.py")
    games = json.loads((release / "games.json").read_text(encoding="utf-8"))
    for game in games["games"]:
        assert digest((release / game["path"]).read_bytes()) == game["sha256"]
    print("PASS: exact archive, nine payloads, source syntax and smoke PGN hashes")
    print("No engine imports, searches, tablebase probes or games performed.")


if __name__ == "__main__":
    verify()
