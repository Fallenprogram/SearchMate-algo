"""Release packaging and metadata rejection checks; never import or run the player."""

from __future__ import annotations

import argparse
import importlib.util
import io
import json
import tempfile
import unittest
import zipfile
from contextlib import redirect_stdout
from pathlib import Path
from types import ModuleType
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[4]
EXPECTED_ZIP_SHA256 = "278d9818bbe5ac82427e5a483e4acbfde9cb98569f49aec74c2c99bac0bd9bde"


def load_checker() -> ModuleType:
    path = ROOT / ".github/scripts/check_v2_submission.py"
    spec = importlib.util.spec_from_file_location("check_v2_submission", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load the release checker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CHECKER = load_checker()


class PackageTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="v2-package-unit-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name) / "repository"
        self.work = Path(temporary.name) / "package"
        self.work.mkdir()
        self.source = (ROOT / CHECKER.TESTED_SOURCE_PATH).read_bytes()
        for relative in (CHECKER.SOURCE_PATH, CHECKER.TESTED_SOURCE_PATH):
            destination = self.root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(self.source)
        self.metadata = {
            "source_path": CHECKER.SOURCE_PATH,
            "tested_source_path": CHECKER.TESTED_SOURCE_PATH,
            "agent_sha256": CHECKER.CANDIDATE_SHA256,
            "zip_sha256": EXPECTED_ZIP_SHA256,
        }

    def test_exact_archive_and_extraction_ignore_root_player(self) -> None:
        decoy = b"raise AssertionError('root agent must not be used')\n"
        (self.root / "agent.py").write_bytes(decoy)
        report = CHECKER.make_package(
            self.root, self.work, CHECKER.CANDIDATE_SHA256, EXPECTED_ZIP_SHA256)
        self.assertEqual(report["zip_sha256"], EXPECTED_ZIP_SHA256)
        self.assertEqual(report["zip_bytes"], 8658)
        self.assertEqual(report["uncompressed_bytes"], 8544)
        self.assertEqual(report["runtime_imports"], ["chess", "time"])
        self.assertTrue(report["source_and_tested_snapshot_identical"])
        self.assertTrue(report["extraction_verified"])
        self.assertEqual((self.work / "player/agent.py").read_bytes(), self.source)
        self.assertEqual((self.root / "agent.py").read_bytes(), decoy)
        with zipfile.ZipFile(self.work / "submission.zip") as archive:
            self.assertEqual(archive.namelist(), ["agent.py"])
            member = archive.getinfo("agent.py")
            self.assertEqual(member.date_time, (1980, 1, 1, 0, 0, 0))
            self.assertEqual(member.compress_type, zipfile.ZIP_STORED)
            self.assertEqual(member.create_system, 3)
            self.assertEqual(member.external_attr >> 16, 0o100644)
            self.assertEqual(archive.read("agent.py"), self.source)

    def test_missing_root_player_does_not_block_exact_snapshot(self) -> None:
        self.assertFalse((self.root / "agent.py").exists())
        CHECKER.make_package(
            self.root, self.work, CHECKER.CANDIDATE_SHA256, EXPECTED_ZIP_SHA256)
        self.assertEqual((self.work / "player/agent.py").read_bytes(), self.source)

    def test_either_source_change_rejects_before_packaging(self) -> None:
        for relative in (CHECKER.SOURCE_PATH, CHECKER.TESTED_SOURCE_PATH):
            with self.subTest(path=relative):
                path = self.root / relative
                path.write_bytes(self.source + b"\n")
                with self.assertRaisesRegex(ValueError, "differs from the recorded SHA-256"):
                    CHECKER.make_package(
                        self.root, self.work, CHECKER.CANDIDATE_SHA256, EXPECTED_ZIP_SHA256)
                self.assertFalse((self.work / "submission.zip").exists())
                path.write_bytes(self.source)

    def test_wrong_zip_hash_rejects_before_extraction(self) -> None:
        with self.assertRaisesRegex(ValueError, "temporary ZIP differs"):
            CHECKER.make_package(self.root, self.work, CHECKER.CANDIDATE_SHA256, "0" * 64)
        self.assertFalse((self.work / "player").exists())

    def test_other_candidate_hash_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "frozen v2-01 candidate"):
            CHECKER.make_package(self.root, self.work, "0" * 64, EXPECTED_ZIP_SHA256)
        self.assertFalse((self.work / "submission.zip").exists())

    def test_metadata_paths_cannot_redirect_source_or_tested_snapshot(self) -> None:
        for field in ("source_path", "tested_source_path"):
            with self.subTest(field=field):
                metadata = {**self.metadata, field: "agent.py"}
                self.assert_metadata_rejected(
                    metadata, field, f"unexpected release metadata {field}")

    def test_requested_hash_must_agree_with_metadata(self) -> None:
        self.assert_metadata_rejected(
            self.metadata, "requested-hash", "disagrees with committed release metadata",
            expected_agent="0" * 64)

    def assert_metadata_rejected(
        self, metadata: dict[str, str], name: str, message: str, expected_agent: str = ""
    ) -> None:
        metadata_path = self.work / f"{name}.json"
        metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
        output = self.work / name
        arguments = argparse.Namespace(
            release_metadata=metadata_path, output=output,
            expected_agent_sha256=expected_agent, expected_zip_sha256="")
        with (
            patch.object(CHECKER, "ROOT", self.root),
            patch.object(CHECKER.shutil, "which", return_value=None),
            patch.object(CHECKER, "run_logged") as run_logged,
            redirect_stdout(io.StringIO()),
        ):
            self.assertEqual(CHECKER.outer(arguments), 1)
        run_logged.assert_not_called()
        report = json.loads((output / "report.json").read_text(encoding="utf-8"))
        self.assertFalse(report["passed"])
        self.assertIn(message, report["error"])


if __name__ == "__main__":
    unittest.main()
