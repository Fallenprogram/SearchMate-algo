"""Verify this preserved release without importing the chess engine."""

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
    archive = (release / record["zip_path"]).read_bytes()
    assert digest(archive) == record["zip_sha256"], "ZIP SHA-256 mismatch"
    assert len(archive) == record["zip_bytes"], "ZIP size mismatch"
    expected = {item["path"]: item for item in record["members"]}
    assert set(expected) == {
        "agent.py", "evaluation.npz", "TABLEBASES.txt", "tables/KQvK.rtbw", "tables/KQvK.rtbz"
    }, "Unexpected payload manifest"
    with ZipFile(release / record["zip_path"]) as zipped:
        assert zipped.testzip() is None, "ZIP CRC failure"
        assert len(zipped.namelist()) == len(expected), "Duplicate ZIP member"
        assert set(zipped.namelist()) == set(expected), "Unexpected ZIP member"
        for name, item in expected.items():
            data = zipped.read(name)
            assert data == (release / "player" / name).read_bytes(), name
            assert len(data) == item["bytes"], f"Size mismatch: {name}"
            assert digest(data) == item["sha256"], f"SHA-256 mismatch: {name}"
        assert sum(zipped.getinfo(name).file_size for name in expected) == record[
            "uncompressed_bytes"
        ], "Uncompressed size mismatch"
    source = (release / record["agent_path"]).read_bytes()
    assert digest(source) == record["agent_sha256"], "Source identity mismatch"
    ast.parse(source, filename="agent.py")
    rollback = record["rollback"]
    for kind in ("agent", "zip"):
        data = (release / rollback[f"{kind}_path"]).read_bytes()
        assert digest(data) == rollback[f"{kind}_sha256"], f"Rollback {kind} mismatch"
    print("PASS: archive, five payloads, source syntax, and declared rollback hashes")
    print("No engine imports, searches, tablebase probes or games performed.")


if __name__ == "__main__":
    verify()
