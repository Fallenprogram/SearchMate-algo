"""Failure-injection checks for the fixed v0 evidence gate; no games are played."""

from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import chess

from research import gate, runner
from research.checks import CLOCKS_MS, fixtures
from research.runner import Json, Object


def complete_campaign() -> Object:
    sizes = {"short-random": 64, "short-greedy": 24, "short-minimax": 16,
             "short-numba": 8, "full-greedy": 4, "full-minimax": 4}
    groups: Object = {name: {"win": 0, "draw": 0, "loss": size, "void": 0}
                      for name, size in sizes.items()}
    return {
        "expected_games": 120, "completed_games": 120, "complete": True,
        "candidate_results": {"win": 0, "draw": 0, "loss": 120, "void": 0},
        "by_clock_and_opponent": groups, "failures": [], "candidate_failure_count": 0,
        "interrupted_attempts": [],
    }


def fixture_report() -> Object:
    calls: list[Json] = []
    for case in fixtures():
        for clock in CLOCKS_MS:
            calls.append({"fixture": case.name, "fen": case.fen, "remaining_ms": clock,
                          "move": next(iter(chess.Board(case.fen).legal_moves)).uci(),
                          "elapsed_ms": 0.5, "error": ""})
    internal: list[Json] = list(gate.INTERNAL_CHECKS)
    return {
        "agent_sha256": "test-hash", "passed": True, "failures": [], "import_ms": 1,
        "internal_checks": internal, "fixture_calls": calls,
        "package_proposal": {"files": ["agent.py"], "uncompressed_bytes": 100,
                             "imports": ["chess", "time"], "archive_created": False,
                             "platform_checks": "pending"},
    }


def resolution_fixture(root: Path) -> tuple[Path, Path, str]:
    """Create only the linked evidence needed for resolution validation."""
    run_dir = root / "run"
    spec = runner.schedule()[0]
    manifest = "test-manifest"
    original_dir = run_dir / "attempts" / spec.identifier / "001"
    replacement_dir = original_dir.parent / "002"
    for path in (original_dir, replacement_dir, run_dir / "games"):
        path.mkdir(parents=True, exist_ok=True)
    runner.atomic_json(original_dir / "start.json", {
        "game_id": spec.identifier, "attempt": 1, "manifest_sha256": manifest,
        "spec": spec.to_json(),
    })
    runner.atomic_json(original_dir / "interrupted.json", {
        "status": "interrupted", "game_id": spec.identifier, "manifest_sha256": manifest,
        "white": {"startup_failure": None, "startup_ms": 50, "moves": []},
        "reason": "KeyboardInterrupt",
    })
    replacement: Object = {
        "status": "completed", "game_id": spec.identifier, "attempt": 2,
        "manifest_sha256": manifest, "spec": spec.to_json(), "failures": [],
        "result": "draw", "termination": "stalemate",
    }
    runner.atomic_json(replacement_dir / "completed.json", replacement)
    runner.atomic_json(run_dir / "games" / f"{spec.identifier}.json", replacement)
    resolution_path = root / "resolution.json"
    runner.atomic_json(resolution_path, {
        "interrupted_attempt": {
            "path": (original_dir / "interrupted.json").relative_to(run_dir).as_posix(),
            "sha256": runner.sha256(original_dir / "interrupted.json"),
        },
        "replacement_completed": {
            "path": (replacement_dir / "completed.json").relative_to(run_dir).as_posix(),
            "sha256": runner.sha256(replacement_dir / "completed.json"),
        },
        "cause": "external interruption", "explanation": "Host run was stopped externally.",
        "candidate_failure_excluded": True,
    })
    return run_dir, resolution_path, manifest


def resolution_validation(root: Path, resolution_path: Path) -> Object:
    return {"interruption_resolutions": [{
        "path": resolution_path.relative_to(root).as_posix(),
        "sha256": runner.sha256(resolution_path),
    }]}


class GateTests(unittest.TestCase):
    def test_no_minimum_win_rate(self) -> None:
        self.assertEqual(gate.decide(complete_campaign(), [], [])["decision"], "pass")

    def test_candidate_failure_overrides_score_and_completeness(self) -> None:
        campaign = complete_campaign()
        campaign["failures"] = [{"role": "candidate", "reason": "flag"}]
        campaign["candidate_failure_count"] = 1
        self.assertEqual(gate.decide(campaign, [], [])["decision"], "failed")

    def test_opponent_and_interruption_never_pass(self) -> None:
        cases: list[tuple[str, Json]] = [
            ("failures", [{"role": "opponent", "reason": "init"}]),
            ("interrupted_attempts", ["attempts/game/001/interrupted.json"]),
        ]
        for key, value in cases:
            with self.subTest(key=key):
                campaign = complete_campaign()
                campaign[key] = value
                self.assertEqual(gate.decide(campaign, [], [])["decision"], "incomplete")

    def test_incomplete_and_malformed_evidence_never_pass(self) -> None:
        self.assertEqual(gate.decide(None, [], [])["decision"], "incomplete")
        self.assertEqual(gate.decide({}, [], [])["decision"], "failed")
        campaign = complete_campaign()
        campaign["complete"] = False
        self.assertEqual(gate.decide(campaign, [], [])["decision"], "incomplete")
        campaign = complete_campaign()
        campaign["completed_games"] = True
        self.assertEqual(gate.decide(campaign, [], [])["decision"], "failed")
        self.assertEqual(gate.decide(complete_campaign(), ["lint failed"], [])["decision"],
                         "failed")
        self.assertEqual(gate.decide(complete_campaign(), [], ["no smoke"])["decision"],
                         "incomplete")

    def test_wrong_opponent_allocation_fails(self) -> None:
        campaign = complete_campaign()
        groups = gate.as_object(campaign["by_clock_and_opponent"])
        groups["short-numba"] = {"win": 0, "draw": 0, "loss": 7, "void": 0}
        self.assertEqual(gate.decide(campaign, [], [])["decision"], "failed")

    def test_fixture_content_is_rechecked(self) -> None:
        original = fixture_report()
        gate.validate_fixtures(original, "test-hash", 100)
        changes: list[tuple[str, Json]] = [
            ("move", "a1a8"), ("elapsed_ms", 20), ("elapsed_ms", float("nan")),
            ("fen", chess.STARTING_FEN.replace(" w ", " b ")), ("error", "illegal"),
        ]
        for key, value in changes:
            with self.subTest(key=key, value=value):
                report = copy.deepcopy(original)
                first = gate.as_object(gate.as_list(report["fixture_calls"])[0])
                first[key] = value
                with self.assertRaises(ValueError):
                    gate.validate_fixtures(report, "test-hash", 100)
        with self.assertRaises(ValueError):
            gate.validate_fixtures(original, "different-agent", 100)

    def test_duplicate_fixture_fails(self) -> None:
        report = fixture_report()
        calls = gate.as_list(report["fixture_calls"])
        calls[1] = copy.deepcopy(calls[0])
        with self.assertRaises(ValueError):
            gate.validate_fixtures(report, "test-hash", 100)

    def test_missing_files_return_incomplete(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = gate.evaluate(root / "absent-run", root / "absent-validation.json", root)
        self.assertEqual(result["decision"], "incomplete")

    def test_path_escape_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory, self.assertRaises(ValueError):
            gate.evidence_path("../outside.json", Path(directory))

    def test_external_interruption_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run_dir, record, manifest = resolution_fixture(root)
            accepted = gate.validate_resolutions(resolution_validation(root, record),
                                                 run_dir, manifest, root)
            self.assertEqual(len(accepted), 1)
            self.assertTrue(record.exists())

    def test_bad_resolution_links_fail(self) -> None:
        for alteration in ("hash", "game", "replacement", "duplicate"):
            with self.subTest(alteration=alteration), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                run_dir, record, manifest = resolution_fixture(root)
                resolution = runner.read_object(record)
                replacement_ref = gate.as_object(resolution["replacement_completed"])
                if alteration == "hash":
                    replacement_ref["sha256"] = "incorrect"
                elif alteration in {"game", "replacement"}:
                    path = gate.evidence_path(replacement_ref["path"], run_dir)
                    replacement = runner.read_object(path)
                    replacement["game_id" if alteration == "game" else "attempt"] = (
                        "different-game" if alteration == "game" else 1
                    )
                    runner.atomic_json(path, replacement, replace=True)
                    replacement_ref["sha256"] = runner.sha256(path)
                runner.atomic_json(record, resolution, replace=True)
                validation = resolution_validation(root, record)
                if alteration == "duplicate":
                    refs = gate.as_list(validation["interruption_resolutions"])
                    refs.append(copy.deepcopy(refs[0]))
                with self.assertRaises(ValueError):
                    gate.validate_resolutions(validation, run_dir, manifest, root)

    def test_observed_failure_cannot_be_resolved(self) -> None:
        for alteration in ("startup", "move", "illegal", "overrun"):
            with self.subTest(alteration=alteration), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                run_dir, record, manifest = resolution_fixture(root)
                resolution = runner.read_object(record)
                reference = gate.as_object(resolution["interrupted_attempt"])
                path = gate.evidence_path(reference["path"], run_dir)
                original = runner.read_object(path)
                telemetry = gate.as_object(original["white"])
                if alteration == "startup":
                    telemetry["startup_failure"] = "init"
                else:
                    telemetry["moves"] = [{
                        "fen": chess.STARTING_FEN, "input_time_left_ms": 20,
                        "elapsed_ms": 25 if alteration == "overrun" else 1,
                        "uci": "a1a8" if alteration == "illegal" else "e2e4",
                        "failure": "flag" if alteration == "move" else None,
                    }]
                runner.atomic_json(path, original, replace=True)
                reference["sha256"] = runner.sha256(path)
                runner.atomic_json(record, resolution, replace=True)
                with self.assertRaises(ValueError):
                    gate.validate_resolutions(resolution_validation(root, record),
                                              run_dir, manifest, root)

    def test_evaluate_resolves_both_old_start_and_interruption(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run_dir, record, manifest = resolution_fixture(root)
            validation = resolution_validation(root, record)
            (root / "agent.py").write_text("test source", encoding="utf-8")
            validation["agent_sha256"] = runner.sha256(root / "agent.py")
            empty = root / "empty.json"
            runner.atomic_json(empty, {})
            for key in ("fixture_report", "official_smoke"):
                validation[key] = {"path": "empty.json", "sha256": runner.sha256(empty)}
            validation_path = root / "validation.json"
            runner.atomic_json(validation_path, validation)
            campaign = complete_campaign()
            original = gate.as_object(runner.read_object(record)["interrupted_attempt"])
            campaign["interrupted_attempts"] = [original["path"]]
            with (
                patch.object(runner, "verify_manifest", return_value=manifest),
                patch.object(runner, "summary", return_value=campaign),
                patch.multiple(gate, validate_fixtures=Mock(), validate_quality=Mock(),
                               validate_smoke=Mock()),
            ):
                accepted = gate.evaluate(run_dir, validation_path, root)
                self.assertEqual(accepted["decision"], "pass")
                self.assertEqual(accepted["interrupted_attempts"], [original["path"]])
                validation["interruption_resolutions"] = []
                runner.atomic_json(validation_path, validation, replace=True)
                unresolved = gate.evaluate(run_dir, validation_path, root)
                self.assertEqual(unresolved["decision"], "incomplete")


if __name__ == "__main__":
    unittest.main()
