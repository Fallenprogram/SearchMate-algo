"""Deterministic v0 completion decision from frozen local evidence; never promotes."""

from __future__ import annotations

import argparse
import math
import re
import sys
from pathlib import Path

import chess

from harness.referee import FAILED_TERMINATIONS
from harness.rules import INIT_BUDGET_S, MAX_UNZIPPED_BYTES
from research import runner
from research.checks import CLOCKS_MS, fixtures
from research.runner import Json, Object

ROOT = Path(__file__).resolve().parents[1]
INTERNAL_CHECKS = [
    "mate_in_one_both_colors_fixed_depth",
    "terminal_and_referee_checkmate",
    "terminal_and_referee_stalemate",
    "terminal_and_referee_insufficient_material",
    "terminal_and_referee_fifty_move_draw",
    "terminal_and_referee_mate_before_draw",
    "search_and_referee_repetition",
    "expired_deadline_preserves_board",
    "evaluation_side_to_move",
    "fixed_depth_determinism",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def as_object(value: Json) -> Object:
    require(isinstance(value, dict), "expected a JSON object")
    assert isinstance(value, dict)
    return value


def as_list(value: Json) -> list[Json]:
    require(isinstance(value, list), "expected a JSON list")
    assert isinstance(value, list)
    return value


def finite_number(value: Json) -> float:
    require(isinstance(value, (int, float)) and not isinstance(value, bool), "expected number")
    assert isinstance(value, (int, float))
    require(math.isfinite(value), "nonfinite number in evidence")
    return float(value)


def evidence_path(value: Json, root: Path) -> Path:
    require(isinstance(value, str), "evidence path must be a string")
    assert isinstance(value, str)
    relative = Path(value)
    require(not relative.is_absolute(), "evidence paths must be repository relative")
    path = (root / relative).resolve()
    require(path.is_relative_to(root.resolve()), "evidence path escapes repository")
    return path


def referenced_file(reference: Object, root: Path, *, output: bool = False) -> Path:
    path_key, hash_key = ("output_path", "output_sha256") if output else ("path", "sha256")
    path = evidence_path(reference.get(path_key), root)
    require(runner.sha256(path) == reference.get(hash_key), f"evidence hash mismatch: {path}")
    return path


def validate_fixtures(report: Object, agent_hash: str, agent_size: int) -> None:
    require(report.get("agent_sha256") == agent_hash, "fixture candidate hash mismatch")
    require(report.get("passed") is True and report.get("failures") == [], "fixtures failed")
    require(report.get("internal_checks") == INTERNAL_CHECKS, "internal checks incomplete")
    elapsed_import = finite_number(report.get("import_ms"))
    require(0 <= elapsed_import < INIT_BUDGET_S * 1_000, "initialization budget failure")
    expected = {(case.name, clock): case.fen for case in fixtures() for clock in CLOCKS_MS}
    calls = as_list(report.get("fixture_calls"))
    require(len(calls) == len(expected) == 96, "fixture call count mismatch")
    seen: set[tuple[str, int]] = set()
    for value in calls:
        call = as_object(value)
        name, clock = call.get("fixture"), call.get("remaining_ms")
        require(isinstance(name, str) and type(clock) is int, "invalid fixture identity")
        assert isinstance(name, str) and isinstance(clock, int)
        key = (name, clock)
        require(key in expected and key not in seen, "unknown or duplicate fixture")
        seen.add(key)
        require(call.get("fen") == expected[key], "fixture FEN mismatch")
        require(call.get("error") == "", "fixture recorded an error")
        elapsed = finite_number(call.get("elapsed_ms"))
        require(0 <= elapsed < clock, "fixture clock overrun")
        move_text = call.get("move")
        require(isinstance(move_text, str), "fixture move must be a string")
        assert isinstance(move_text, str)
        move = chess.Move.from_uci(move_text)
        require(move in chess.Board(expected[key]).legal_moves, "illegal fixture move")
    proposal = as_object(report.get("package_proposal"))
    require(proposal.get("files") == ["agent.py"], "unexpected proposed package contents")
    require(proposal.get("uncompressed_bytes") == agent_size, "proposed byte count mismatch")
    require(0 < agent_size <= MAX_UNZIPPED_BYTES, "proposed package size exceeds limit")
    require(proposal.get("imports") == ["chess", "time"], "unexpected v0 player imports")
    require(proposal.get("archive_created") is False, "archive creation was not authorized")
    require(proposal.get("platform_checks") == "pending", "unexpected platform success claim")


def quality_commands(root: Path) -> dict[str, list[str]]:
    python = str(Path(sys.executable).resolve())
    paths = sorted(path.relative_to(root).as_posix() for path in (root / "research").glob("*.py"))
    return {
        "ruff": [python, "-m", "ruff", "check", "."],
        "mypy": [python, "-m", "mypy", "--strict", "agent.py", "harness", *paths],
        "unit": [python, "-m", "unittest", "discover", "-s", "research", "-p", "test_*.py",
                 "-v"],
    }


def validate_quality(validation: Object, root: Path) -> None:
    expected = quality_commands(root)
    commands = as_list(validation.get("commands"))
    require(len(commands) == len(expected), "quality command count mismatch")
    seen: set[str] = set()
    for value in commands:
        command = as_object(value)
        name = command.get("name")
        require(isinstance(name, str) and name in expected and name not in seen,
                "unknown or duplicate quality command")
        assert isinstance(name, str)
        seen.add(name)
        require(command.get("command") == expected[name], f"{name} command mismatch")
        require(type(command.get("exit_code")) is int and command.get("exit_code") == 0,
                f"{name} command failed")
        output = referenced_file(command, root, output=True).read_text(encoding="utf-8-sig")
        if name == "ruff":
            require("All checks passed!" in output, "ruff success output missing")
        elif name == "mypy":
            require("Success: no issues found" in output, "mypy success output missing")
        else:
            require(re.search(r"Ran [1-9][0-9]* tests? in", output) is not None,
                    "unit test count missing")
            require(re.search(r"^OK\s*$", output, re.MULTILINE) is not None,
                    "unit success output missing")


def validate_smoke(metadata: Object, root: Path, agent_hash: str) -> None:
    require(metadata.get("agent_sha256") == agent_hash, "smoke candidate hash mismatch")
    expected = [str(Path(sys.executable).resolve()), "-m", "harness.arena", "--opponent",
                "baselines/random", "--games", "2", "--base-ms", "5000"]
    require(metadata.get("command") == expected, "official smoke command mismatch")
    require(type(metadata.get("exit_code")) is int and metadata.get("exit_code") == 0,
            "official smoke command failed")
    output = referenced_file(metadata, root, output=True).read_text(encoding="utf-8-sig")
    games = re.findall(r"^game ([12])/2: (\w+) by (\w+)\s*$", output, re.MULTILINE)
    require(len(games) == 2 and [item[0] for item in games] == ["1", "2"],
            "official smoke did not complete exactly two games")
    require(all(result in {"white", "black", "draw"} and end not in FAILED_TERMINATIONS
                for _, result, end in games), "official smoke runtime failure or void")


def result_counts(value: Json) -> dict[str, int]:
    record = as_object(value)
    require(set(record) == {"win", "draw", "loss", "void"}, "result keys mismatch")
    result: dict[str, int] = {}
    for key, count in record.items():
        require(type(count) is int and count >= 0, "invalid result count")
        assert isinstance(count, int)
        result[key] = count
    return result


def check_interrupted_telemetry(record: Object) -> None:
    """A retry cannot erase a failure already observed before interruption."""
    require(not record.get("failures"), "interrupted attempt has recorded failures")
    require(record.get("termination") not in FAILED_TERMINATIONS,
            "interrupted attempt has a failed termination")
    for color in ("white", "black"):
        if color not in record:
            # Abrupt host termination can leave only a recovered start record.
            # Exclusion then depends on the explicit external-cause review.
            continue
        telemetry = as_object(record[color])
        require(telemetry.get("startup_failure") is None, "interrupted startup failure")
        startup = finite_number(telemetry.get("startup_ms"))
        require(0 <= startup < INIT_BUDGET_S * 1_000, "interrupted initialization overrun")
        for value in as_list(telemetry.get("moves")):
            move = as_object(value)
            require(move.get("failure") is None, "interrupted move failure")
            elapsed = finite_number(move.get("elapsed_ms"))
            remaining = finite_number(move.get("input_time_left_ms"))
            require(0 <= elapsed < remaining, "interrupted observed clock overrun")
            uci = move.get("uci")
            if uci is not None:
                require(isinstance(uci, str), "invalid interrupted move output")
                fen = move.get("fen")
                require(isinstance(fen, str), "missing interrupted move FEN")
                assert isinstance(uci, str) and isinstance(fen, str)
                require(chess.Move.from_uci(uci) in chess.Board(fen).legal_moves,
                        "illegal move in interrupted attempt")


def validate_resolutions(
    validation: Object, run_dir: Path, manifest_hash: str, root: Path
) -> list[Object]:
    """Verify explicit external-interruption reviews without altering raw history."""
    accepted: list[Object] = []
    seen: set[Path] = set()
    for value in as_list(validation.get("interruption_resolutions", [])):
        reference = as_object(value)
        resolution_path = referenced_file(reference, root)
        resolution = runner.read_object(resolution_path)
        for key in ("cause", "explanation"):
            text = resolution.get(key)
            require(isinstance(text, str) and bool(text.strip()), f"resolution needs {key}")
        require(resolution.get("candidate_failure_excluded") is True,
                "candidate failure was not explicitly excluded")
        original_path = referenced_file(as_object(resolution.get("interrupted_attempt")), run_dir)
        replacement_path = referenced_file(
            as_object(resolution.get("replacement_completed")), run_dir
        )
        require(original_path not in seen, "duplicate interruption resolution")
        seen.add(original_path)
        original = runner.read_object(original_path)
        replacement = runner.read_object(replacement_path)
        require(original.get("status") == "interrupted", "original attempt is not interrupted")
        require(replacement.get("status") == "completed", "replacement is not completed")
        game_id = original.get("game_id")
        require(isinstance(game_id, str) and replacement.get("game_id") == game_id,
                "resolution crosses game slots")
        assert isinstance(game_id, str)
        specs = {item.identifier: item.to_json() for item in runner.schedule()}
        require(game_id in specs and replacement.get("spec") == specs[game_id],
                "resolution references an unknown or changed game specification")
        require(original.get("manifest_sha256") == replacement.get("manifest_sha256")
                == manifest_hash, "resolution manifest mismatch")
        original_number = int(original_path.parent.name)
        replacement_number = int(replacement_path.parent.name)
        require(0 < original_number < replacement_number, "replacement must be a later attempt")
        expected_parent = (run_dir / "attempts" / game_id).resolve()
        require(original_path == expected_parent / f"{original_number:03d}" / "interrupted.json",
                "original is not the expected interrupted attempt path")
        expected_replacement = expected_parent / f"{replacement_number:03d}" / "completed.json"
        require(replacement_path == expected_replacement,
                "replacement is not the expected completed attempt path")
        require(replacement.get("attempt") == replacement_number, "replacement number mismatch")
        start = runner.read_object(original_path.parent / "start.json")
        require(start.get("game_id") == game_id and start.get("attempt") == original_number
                and start.get("manifest_sha256") == manifest_hash,
                "original start identity mismatch")
        require(start.get("spec") == replacement.get("spec"),
                "original start specification mismatch")
        require(not (original_path.parent / "completed.json").exists(),
                "original attempt already has a completed outcome")
        canonical = runner.read_object(run_dir / "games" / f"{game_id}.json")
        require(replacement == canonical, "replacement does not match the canonical completed game")
        require(replacement.get("failures") == [] and replacement.get("result") != "void"
                and replacement.get("termination") not in FAILED_TERMINATIONS,
                "replacement has a failure or void result")
        check_interrupted_telemetry(original)
        accepted.append({
            "resolution_path": reference["path"], "resolution_sha256": reference["sha256"],
            "interrupted_attempt": original_path.relative_to(run_dir.resolve()).as_posix(),
            "replacement_completed": replacement_path.relative_to(run_dir.resolve()).as_posix(),
            "cause": resolution["cause"], "explanation": resolution["explanation"],
        })
    return accepted


def decide(campaign: Object | None, failures: list[str], missing: list[str]) -> Object:
    """Pure decision: neither a high score nor an asserted summary pass overrides checks."""
    failed, incomplete = list(failures), list(missing)
    if campaign is None:
        incomplete.append("campaign evidence unavailable")
    else:
        try:
            require(campaign.get("expected_games") == 120, "unexpected campaign allocation")
            completed = campaign.get("completed_games")
            require(type(completed) is int and 0 <= completed <= 120, "invalid completed count")
            assert isinstance(completed, int)
            counts = result_counts(campaign.get("candidate_results"))
            require(sum(counts.values()) == completed, "campaign totals do not reconcile")
            records = as_list(campaign.get("failures"))
            candidate_failures = sum(as_object(item).get("role") == "candidate" for item in records)
            require(type(campaign.get("candidate_failure_count")) is int
                    and campaign.get("candidate_failure_count") == candidate_failures,
                    "candidate failure count mismatch")
            if candidate_failures:
                failed.append("candidate runtime failures recorded")
            if records and not candidate_failures:
                incomplete.append("opponent or infrastructure failures need resolution")
            if counts["void"]:
                incomplete.append("void games need resolution")
            if as_list(campaign.get("interrupted_attempts")):
                incomplete.append("interrupted attempts need explicit resolution")
            if completed != 120 or campaign.get("complete") is not True:
                incomplete.append(f"campaign incomplete: {completed}/120 games")
            if completed == 120:
                expected_groups = {"short-random": 64, "short-greedy": 24, "short-minimax": 16,
                                   "short-numba": 8, "full-greedy": 4, "full-minimax": 4}
                groups = as_object(campaign.get("by_clock_and_opponent"))
                require(set(groups) == set(expected_groups), "campaign groups mismatch")
                combined = dict.fromkeys(counts, 0)
                for name, size in expected_groups.items():
                    group = result_counts(groups[name])
                    require(sum(group.values()) == size, f"wrong game count in {name}")
                    for outcome, count in group.items():
                        combined[outcome] += count
                require(combined == counts, "group results do not reconcile")
        except (ValueError, TypeError, KeyError) as error:
            failed.append(f"campaign integrity: {error}")
    decision = "failed" if failed else "incomplete" if incomplete else "pass"
    return {
        "schema_version": 1, "gate_version": "searchmate-v0-safety.1",
        "decision": decision, "failure_reasons": list(failed),
        "incomplete_reasons": list(incomplete),
        "promotion": "not authorized", "archive_created": False,
        "platform_checks": "pending", "win_rate_threshold": None,
    }


def evaluate(run_dir: Path, validation_path: Path, root: Path = ROOT) -> Object:
    failures: list[str] = []
    missing: list[str] = []
    campaign: Object | None = None
    manifest_hash: str | None = None
    resolutions: list[Object] = []
    unfinished: list[Path] = []
    try:
        manifest_hash = runner.verify_manifest(run_dir, root)
        campaign = runner.summary(run_dir, manifest_hash)
        # A process can stop before it writes interrupted.json. Such a partial
        # attempt must not become invisible just because the gate is read-only.
        for start in (run_dir / "attempts").glob("*/*/start.json"):
            if not (start.parent / "completed.json").exists():
                unfinished.append(start.parent)
    except FileNotFoundError as error:
        missing.append(f"missing campaign artifact: {error.filename}")
    except (ValueError, KeyError, TypeError, OSError) as error:
        failures.append(f"frozen campaign integrity: {error}")
    try:
        validation = runner.read_object(validation_path)
        if manifest_hash is not None:
            resolutions = validate_resolutions(validation, run_dir, manifest_hash, root)
        agent = root / "agent.py"
        agent_hash = runner.sha256(agent)
        require(validation.get("agent_sha256") == agent_hash, "validation candidate mismatch")
        report_path = referenced_file(as_object(validation.get("fixture_report")), root)
        validate_fixtures(runner.read_object(report_path), agent_hash, agent.stat().st_size)
        validate_quality(validation, root)
        smoke_path = referenced_file(as_object(validation.get("official_smoke")), root)
        validate_smoke(runner.read_object(smoke_path), root, agent_hash)
    except FileNotFoundError as error:
        missing.append(f"missing validation artifact: {error.filename}")
    except (ValueError, KeyError, TypeError, OSError) as error:
        failures.append(f"validation evidence: {error}")
    resolved_paths = {item["interrupted_attempt"] for item in resolutions
                      if isinstance(item["interrupted_attempt"], str)}
    for attempt in unfinished:
        relative = (attempt / "interrupted.json").relative_to(run_dir).as_posix()
        if relative not in resolved_paths:
            missing.append(f"unfinished attempt: {attempt.relative_to(run_dir)}")
    history = campaign.get("interrupted_attempts", []) if campaign is not None else []
    decision_campaign = dict(campaign) if campaign is not None else None
    if decision_campaign is not None and isinstance(history, list):
        decision_campaign["interrupted_attempts"] = [
            path for path in history if not isinstance(path, str) or path not in resolved_paths
        ]
    result = decide(decision_campaign, failures, missing)
    result["interrupted_attempts"] = history
    result["interruption_resolutions"] = list(resolutions)
    result["manifest_sha256"] = manifest_hash
    result["validation_sha256"] = (
        runner.sha256(validation_path) if validation_path.is_file() else None
    )
    result["run_dir"] = str(run_dir.resolve())
    result["validation"] = str(validation_path.resolve())
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--validation", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = evaluate(args.run_dir.resolve(), args.validation.resolve())
    output: Path = args.out.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    runner.atomic_json(output, result)
    print(result["decision"])
    if result["decision"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
