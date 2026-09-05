"""Admission checks for the fixed schedule, wire records and crash recovery."""

import io
import json
import shutil
import tempfile
import unittest
from collections import Counter
from contextlib import redirect_stdout
from pathlib import Path
from typing import cast
from unittest.mock import patch

import chess
import chess.pgn

from harness.referee import Outcome, play_match
from research import runner
from research.positions import Opening, openings


class ScheduleTests(unittest.TestCase):
    def test_fixed_counts_and_color_reversed_pairs(self) -> None:
        games = runner.schedule()
        self.assertEqual(len(games), 120)
        self.assertEqual(len({game.identifier for game in games}), 120)
        self.assertEqual(
            Counter((game.clock, game.opponent) for game in games),
            {
                ("short", "random"): 64,
                ("short", "greedy"): 24,
                ("short", "minimax"): 16,
                ("short", "numba"): 8,
                ("full", "greedy"): 4,
                ("full", "minimax"): 4,
            },
        )
        for white, black in zip(games[::2], games[1::2], strict=True):
            self.assertEqual((white.candidate_color, black.candidate_color), ("white", "black"))
            self.assertEqual(white.opening, black.opening)
            self.assertEqual(white.opponent, black.opponent)
            self.assertEqual(
                (white.base_ms, white.increment_ms), (black.base_ms, black.increment_ms)
            )
        self.assertTrue(all(game.calibration for game in games[:8]))
        self.assertFalse(any(game.calibration for game in games[8:]))
        self.assertEqual(
            [(game.clock, game.opponent) for game in games[:8:2]],
            [("short", "random"), ("short", "greedy"), ("short", "minimax"), ("full", "greedy")],
        )
        for game in games:
            expected = (10_000, 100) if game.clock == "short" else (120_000, 500)
            self.assertEqual((game.base_ms, game.increment_ms), expected)

    def test_all_openings_are_distinct_legal_and_nonterminal(self) -> None:
        positions = openings()
        self.assertEqual(len(positions), 32)
        self.assertEqual(len({" ".join(item.fen.split()[:4]) for item in positions}), 32)
        self.assertEqual({chess.Board(item.fen).turn for item in positions}, {True, False})
        for item in positions:
            board = chess.Board()
            for san in item.san.split():
                board.push_san(san)
            self.assertTrue(board.is_valid())
            self.assertFalse(board.is_game_over(claim_draw=True))
            self.assertEqual(board.fen(), item.fen)

    def test_pgn_rejects_mismatched_result_opening_and_illegal_moves(self) -> None:
        spec = runner.schedule()[0]
        game = chess.pgn.Game()
        game.setup(spec.opening.fen)
        game.headers["Result"] = "1-0"
        game.headers["Termination"] = "illegal"
        valid = str(game)
        self.assertEqual(runner.validate_pgn(valid, spec, "white", "illegal"), 0)
        with self.assertRaisesRegex(ValueError, "result"):
            runner.validate_pgn(valid, spec, "black", "illegal")
        with self.assertRaisesRegex(ValueError, "opening"):
            runner.validate_pgn(valid, runner.schedule()[8], "white", "illegal")
        with self.assertRaisesRegex(ValueError, "termination"):
            runner.validate_pgn(valid, spec, "white", "flag")
        illegal = valid.rsplit("1-0", 1)[0] + "5. Qa8 1-0"
        with (
            self.assertLogs("chess.pgn", level="ERROR"),
            self.assertRaisesRegex(ValueError, "malformed"),
        ):
            runner.validate_pgn(illegal, spec, "white", "illegal")


class CampaignTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="searchmate-runner-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "repository"
        self.root.mkdir()
        hashes = cast(runner.Object, runner.frozen_inputs(runner.ROOT)["source_hashes"])
        for relative in hashes:
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(runner.ROOT / relative, target)
        (self.root / "agent.py").write_text(
            "def get_move(fen: str, time_left_ms: int) -> str:\n    return 'a1a1'\n",
            encoding="utf-8",
        )
        self.run_dir = Path(self.temporary.name) / "run"
        self.output = io.StringIO()
        self.redirect = redirect_stdout(self.output)
        self.redirect.__enter__()
        self.addCleanup(self.redirect.__exit__, None, None, None)

    def prepare(self) -> str:
        runner.prepare(self.run_dir, self.root)
        return runner.verify_manifest(self.run_dir, self.root)

    def test_manifest_rejects_candidate_harness_checker_opponent_and_snapshot_changes(self) -> None:
        self.prepare()
        for relative in (
            "agent.py",
            "harness/referee.py",
            "research/checks.py",
            "research/GATE_SPEC.md",
            "baselines/random/agent.py",
        ):
            path = self.root / relative
            original = path.read_bytes()
            path.write_bytes(original + b"\n# changed\n")
            with self.assertRaisesRegex(ValueError, "manifest mismatch"):
                runner.verify_manifest(self.run_dir, self.root)
            path.write_bytes(original)
            runner.verify_manifest(self.run_dir, self.root)
        snapshot = self.run_dir / "candidate" / "agent.py"
        snapshot.write_bytes(snapshot.read_bytes() + b"\n# snapshot changed\n")
        with self.assertRaisesRegex(ValueError, "snapshot hash"):
            runner.verify_manifest(self.run_dir, self.root)

    def test_manifest_rejects_schedule_and_dependency_metadata_changes(self) -> None:
        self.prepare()
        path = self.run_dir / "manifest.json"
        original = path.read_bytes()
        value = runner.read_object(path)
        value["schedule_sha256"] = "0" * 64
        path.write_bytes(runner.canonical_bytes(value))
        with self.assertRaisesRegex(ValueError, "manifest mismatch"):
            runner.verify_manifest(self.run_dir, self.root)
        path.write_bytes(original)
        value = runner.read_object(path)
        cast(runner.Object, value["environment"])["python"] = "different python"
        path.write_bytes(runner.canonical_bytes(value))
        with self.assertRaisesRegex(ValueError, "manifest mismatch"):
            runner.verify_manifest(self.run_dir, self.root)

    def test_mutable_research_memory_does_not_change_frozen_manifest(self) -> None:
        digest = self.prepare()
        (self.root / "research" / "WORKING_MEMORY.md").write_text("updated", encoding="utf-8")
        self.assertEqual(runner.verify_manifest(self.run_dir, self.root), digest)

    def test_illegal_reply_is_attributed_to_candidate_and_never_replayed(self) -> None:
        digest = self.prepare()
        first = runner.run_campaign(self.run_dir, max_games=1, root=self.root)
        self.assertEqual(first["completed_games"], 1)
        self.assertEqual(first["candidate_failure_count"], 1)
        self.assertEqual(first["candidate_results"], {"win": 0, "draw": 0, "loss": 1, "void": 0})
        spec = runner.schedule()[0]
        record = runner.completed_record(self.run_dir, spec, digest)
        self.assertIsNotNone(record)
        assert record is not None
        self.assertEqual(
            record["failures"],
            [{"color": "white", "role": "candidate", "stage": "referee", "reason": "illegal"}],
        )
        white = cast(runner.Object, record["white"])
        self.assertEqual(white["move_count"], 1)
        self.assertEqual(cast(list[runner.Object], white["moves"])[0]["uci"], "a1a1")
        second = runner.run_campaign(self.run_dir, max_games=0, root=self.root)
        self.assertEqual(second["candidate_failure_count"], 1)
        self.assertEqual(second["completed_games"], 1)
        self.assertEqual(len(list((self.run_dir / "attempts" / spec.identifier).iterdir())), 1)

    def test_black_candidate_failure_and_opponent_failure_are_distinct(self) -> None:
        digest = self.prepare()
        spec = runner.schedule()[1]
        record = runner.run_game(self.run_dir, spec, digest, self.root)
        self.assertEqual(record["candidate_result"], "loss")
        self.assertEqual(
            record["failures"],
            [{"color": "black", "role": "candidate", "stage": "referee", "reason": "illegal"}],
        )
        white = runner.ObservedAgent(self.root, "white", "candidate")
        black = runner.ObservedAgent(self.root, "black", "opponent")
        self.assertEqual(
            runner.failure_records(Outcome("white", "flag", ""), (white, black)),
            [{"color": "black", "role": "opponent", "stage": "referee", "reason": "flag"}],
        )

    def test_both_startup_failures_remain_void_and_count_each_side(self) -> None:
        for path in (self.root / "agent.py", self.root / "baselines/random/agent.py"):
            path.write_text("raise RuntimeError('intentional startup failure')\n", encoding="utf-8")
        digest = self.prepare()
        record = runner.run_game(self.run_dir, runner.schedule()[0], digest, self.root)
        self.assertEqual(record["result"], "void")
        self.assertEqual(record["candidate_result"], "void")
        self.assertEqual(record["termination"], "both_failed")
        self.assertEqual(len(cast(list[runner.Json], record["failures"])), 2)
        state = runner.summary(self.run_dir, digest)
        self.assertEqual(state["candidate_failure_count"], 1)
        self.assertEqual(state["candidate_results"], {"win": 0, "draw": 0, "loss": 0, "void": 1})
        self.assertIn(
            "intentional startup failure",
            runner.field_text(cast(runner.Object, record["white"]), "stderr"),
        )

    def test_observer_passes_legal_moves_through_original_wire_and_referee(self) -> None:
        (self.root / "agent.py").write_text(
            "def get_move(fen: str, time_left_ms: int) -> str:\n    return 'f7f8'\n",
            encoding="utf-8",
        )
        fen = "7k/5Q2/6K1/8/8/8/8/8 w - - 0 1"
        white = runner.ObservedAgent(self.root, "white", "candidate")
        black = runner.ObservedAgent(self.root / "baselines/random", "black", "opponent")
        outcome = play_match(white, black, 1000, 100, start_fen=fen)
        self.assertEqual((outcome.result, outcome.termination), ("white", "checkmate"))
        spec = runner.GameSpec(
            "mate-test",
            "random",
            Opening("mate-test", "mate", "", fen),
            "white",
            "short",
            1000,
            100,
            False,
        )
        self.assertEqual(runner.validate_pgn(outcome.pgn, spec, "white", "checkmate"), 1)
        self.assertEqual(runner.failure_records(outcome, (white, black)), [])
        observation = white.to_json()
        self.assertEqual(observation["minimum_input_time_left_ms"], 1000)
        self.assertGreater(cast(float, observation["startup_ms"]), 0)
        self.assertGreaterEqual(cast(float, white.moves[0]["elapsed_ms"]), 0)

    def test_interruption_keeps_attempt_evidence_and_resume_uses_new_attempt(self) -> None:
        digest = self.prepare()
        spec = runner.schedule()[0]
        with (
            patch.object(runner, "play_match", side_effect=KeyboardInterrupt("simulated")),
            self.assertRaises(KeyboardInterrupt),
        ):
            runner.run_game(self.run_dir, spec, digest, self.root)
        first = self.run_dir / "attempts" / spec.identifier / "001"
        self.assertTrue((first / "start.json").is_file())
        self.assertTrue((first / "interrupted.json").is_file())
        self.assertIsNone(runner.completed_record(self.run_dir, spec, digest))
        state = runner.run_campaign(self.run_dir, max_games=1, root=self.root)
        self.assertEqual(state["completed_games"], 1)
        self.assertEqual(len(cast(list[runner.Json], state["interrupted_attempts"])), 1)
        self.assertTrue((first.parent / "002/completed.json").is_file())
        events = [
            json.loads(line)
            for line in (self.run_dir / "events.jsonl").read_text(encoding="utf-8").splitlines()
        ]
        self.assertIn("runner_interrupted", [item["kind"] for item in events])

    def test_power_loss_start_sentinel_becomes_interrupted_evidence(self) -> None:
        digest = self.prepare()
        spec = runner.schedule()[0]
        attempt = self.run_dir / "attempts" / spec.identifier / "001"
        attempt.mkdir(parents=True)
        runner.atomic_json(
            attempt / "start.json",
            {
                "manifest_sha256": digest,
                "game_id": spec.identifier,
            },
        )
        runner.recover_attempts(self.run_dir, digest)
        saved = (attempt / "interrupted.json").read_bytes()
        runner.recover_attempts(self.run_dir, digest)
        self.assertEqual((attempt / "interrupted.json").read_bytes(), saved)

    def test_crash_after_durable_outcome_recovers_without_replaying_failure(self) -> None:
        digest = self.prepare()
        spec = runner.schedule()[0]
        original = runner.atomic_bytes

        def fail_pgn(path: Path, data: bytes, *, replace: bool = False) -> None:
            if path.name == "game.pgn":
                raise OSError("simulated crash before convenience PGN publication")
            original(path, data, replace=replace)

        with (
            patch.object(runner, "atomic_bytes", side_effect=fail_pgn),
            self.assertRaisesRegex(OSError, "simulated crash"),
        ):
            runner.run_game(self.run_dir, spec, digest, self.root)
        self.assertFalse((self.run_dir / "games" / f"{spec.identifier}.json").exists())
        state = runner.run_campaign(self.run_dir, max_games=0, root=self.root)
        self.assertEqual((state["completed_games"], state["candidate_failure_count"]), (1, 1))
        self.assertEqual(len(list((self.run_dir / "attempts" / spec.identifier).iterdir())), 1)
        self.assertEqual(state["interrupted_attempts"], [])

    def test_completed_artifact_tampering_is_rejected(self) -> None:
        digest = self.prepare()
        spec = runner.schedule()[0]
        runner.run_game(self.run_dir, spec, digest, self.root)
        pgn = self.run_dir / "games" / f"{spec.identifier}.pgn"
        original = pgn.read_bytes()
        pgn.write_bytes(original + b"\n")
        with self.assertRaisesRegex(ValueError, "PGN hash mismatch"):
            runner.completed_record(self.run_dir, spec, digest)
        pgn.write_bytes(original)
        record_path = self.run_dir / "games" / f"{spec.identifier}.json"
        record = runner.read_object(record_path)
        record["candidate_result"] = "win"
        record_path.write_bytes(runner.canonical_bytes(record))
        with self.assertRaisesRegex(ValueError, "durable completed attempt"):
            runner.completed_record(self.run_dir, spec, digest)

    def test_immutable_file_cannot_be_overwritten(self) -> None:
        self.prepare()
        path = self.run_dir / "test-evidence.json"
        runner.atomic_json(path, {"original": True})
        with self.assertRaises(FileExistsError):
            runner.atomic_json(path, {"replacement": True})
        self.assertEqual(runner.read_object(path), {"original": True})
        with self.assertRaises(FileExistsError):
            runner.prepare(self.run_dir, self.root)


if __name__ == "__main__":
    unittest.main()
