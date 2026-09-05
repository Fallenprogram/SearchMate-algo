"""Immutable, resumable local v0 campaign using the unchanged platform harness.

Prepare after candidate checks, then run as many or as few games per invocation
as desired. Never edit the candidate, inputs, or this runner during a campaign.
Interrupted attempts remain evidence and are reported separately from completed
games. Completed games, including failures and void results, are never replayed.
"""

import argparse
import hashlib
import io
import json
import os
import platform
import sys
import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path
from typing import cast

import chess
import chess.pgn

from harness.referee import FAILED_TERMINATIONS, RESULT_HEADERS, Outcome, play_match
from harness.rules import BASE_MS, INCREMENT_MS, INIT_BUDGET_S, PLY_CAP
from harness.sandbox import Agent, AgentFailure, local
from research.positions import Opening, openings

type Json = bool | int | float | str | list[Json] | dict[str, Json] | None
type Object = dict[str, Json]

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = 1
FAST_BASE_MS = 10_000
FAST_INCREMENT_MS = 100
OPPONENTS = ("random", "greedy", "minimax", "numba")
SHORT_SUBSETS = {
    "random": tuple(range(32)),
    "greedy": (0, 2, 6, 8, 10, 12, 16, 18, 20, 24, 28, 31),
    "minimax": (0, 4, 8, 12, 16, 20, 24, 28),
    "numba": (2, 10, 22, 30),
}
FULL_SUBSETS = {"greedy": (0, 16), "minimax": (8, 24)}


@dataclass(frozen=True)
class GameSpec:
    identifier: str
    opponent: str
    opening: Opening
    candidate_color: str
    clock: str
    base_ms: int
    increment_ms: int
    calibration: bool

    def to_json(self) -> Object:
        return {
            "id": self.identifier,
            "opponent": self.opponent,
            "opening_id": self.opening.identifier,
            "start_fen": self.opening.fen,
            "candidate_color": self.candidate_color,
            "clock": self.clock,
            "base_ms": self.base_ms,
            "increment_ms": self.increment_ms,
            "ply_cap": PLY_CAP,
            "calibration": self.calibration,
        }


def schedule() -> tuple[GameSpec, ...]:
    """120 fixed games; the first eight calibrate all non-numba conditions."""
    positions = openings()
    pairs: list[tuple[str, str, int, bool]] = [
        ("short", "random", 0, True),
        ("short", "greedy", 0, True),
        ("short", "minimax", 0, True),
        ("full", "greedy", 0, True),
    ]
    used = {(clock, opponent, index) for clock, opponent, index, _ in pairs}
    for clock, subsets in (("short", SHORT_SUBSETS), ("full", FULL_SUBSETS)):
        for opponent, indices in subsets.items():
            for index in indices:
                if (clock, opponent, index) not in used:
                    pairs.append((clock, opponent, index, False))
    result = []
    for clock, opponent, index, calibration in pairs:
        opening = positions[index]
        for color in ("white", "black"):
            result.append(
                GameSpec(
                    f"{clock}-{opponent}-{opening.identifier}-{color}",
                    opponent,
                    opening,
                    color,
                    clock,
                    FAST_BASE_MS if clock == "short" else BASE_MS,
                    FAST_INCREMENT_MS if clock == "short" else INCREMENT_MS,
                    calibration,
                )
            )
    return tuple(result)


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def canonical_bytes(value: Json) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_object(path: Path) -> Object:
    value: object = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return cast(Object, value)


def field_text(value: Object, field: str) -> str:
    result = value.get(field)
    if not isinstance(result, str):
        raise ValueError(f"expected string field {field}")
    return result


def atomic_bytes(path: Path, data: bytes, *, replace: bool = False) -> None:
    """Publish a complete file; retain any prior immutable evidence."""
    if path.exists() and not replace:
        raise FileExistsError(f"refusing to overwrite evidence: {path}")
    temporary = path.with_name(path.name + f".{os.getpid()}.{time.time_ns()}.tmp")
    with temporary.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def atomic_json(path: Path, data: Object, *, replace: bool = False) -> None:
    atomic_bytes(path, canonical_bytes(data), replace=replace)


def event(run_dir: Path, kind: str, **details: Json) -> None:
    record: Object = {"at": utc_now(), "kind": kind, **details}
    with (run_dir / "events.jsonl").open("ab") as stream:
        stream.write(json.dumps(record, sort_keys=True, allow_nan=False).encode("utf-8") + b"\n")
        stream.flush()
        os.fsync(stream.fileno())


@contextmanager
def campaign_lock(run_dir: Path) -> Iterator[None]:
    """OS-owned lock releases after crashes, unlike a stale PID sentinel."""
    with (run_dir / ".lock").open("a+b") as stream:
        if stream.tell() == 0:
            stream.write(b"0")
            stream.flush()
        stream.seek(0)
        if sys.platform == "win32":
            import msvcrt

            try:
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError as error:
                raise RuntimeError("another runner holds this campaign lock") from error
            try:
                yield
            finally:
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            try:
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as error:
                raise RuntimeError("another runner holds this campaign lock") from error
            try:
                yield
            finally:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def frozen_inputs(root: Path) -> Object:
    files = [root / "agent.py", root / "pyproject.toml", root / "uv.lock"]
    files.extend(sorted((root / "harness").glob("*.py")))
    files.extend(root / "baselines" / name / "agent.py" for name in OPPONENTS)
    files.extend(
        root / "research" / name
        for name in (
            "runner.py",
            "positions.py",
            "__init__.py",
            "checks.py",
            "test_player.py",
            "test_runner.py",
            "gate.py",
            "test_gate.py",
            "RESEARCH_PROTOCOL.md",
            "GATE_SPEC.md",
            "CHECKERS.md",
            "INVOCATION_POLICY.md",
        )
    )
    hashes: Object = {path.relative_to(root).as_posix(): sha256(path) for path in files}
    packages: Object = {
        name: version(name) for name in ("chess", "numpy", "numba", "torch", "onnxruntime")
    }
    positions: list[Json] = [
        {"id": item.identifier, "name": item.name, "san": item.san, "fen": item.fen}
        for item in openings()
    ]
    games: list[Json] = [item.to_json() for item in schedule()]
    return {
        "schema_version": SCHEMA_VERSION,
        "suite": "searchmate-v0-evolution-120",
        "root": str(root.resolve()),
        "source_hashes": hashes,
        "candidate_sha256": sha256(root / "agent.py"),
        "environment": {
            "python": sys.version,
            "executable": str(Path(sys.executable).resolve()),
            "platform": platform.platform(),
            "processor": platform.processor(),
            "logical_cpu_count": os.cpu_count(),
            "dependencies": packages,
            "execution": "local harness; host OS, CPU and memory limits differ from platform",
        },
        "protocol": "unmodified harness.sandbox.local and harness.referee.play_match",
        "init_budget_s": INIT_BUDGET_S,
        "positions": positions,
        "positions_sha256": hashlib.sha256(canonical_bytes(positions)).hexdigest(),
        "position_provenance": "hand-authored common-opening SAN; no engine labels; evolution only",
        "random_seed": None,
        "random_seed_note": "baseline randomness is uncontrolled; unchanged baseline processes",
        "schedule": games,
        "schedule_sha256": hashlib.sha256(canonical_bytes(games)).hexdigest(),
        "hard_time_limit_hours": None,
        "promotion": "none; fixed v0 setup evidence with no minimum win-rate gate",
        "researcher": {
            "implementation": "Codex",
            "reported_model": "gpt-6-astra",
            "reasoning_effort": "ultra",
            "exact_backend_weight_pin": None,
            "task_id": "01a070e7-c24b-77d3-a38b-e77b75990948",
        },
    }


def prepare(run_dir: Path, root: Path = ROOT) -> None:
    manifest = frozen_inputs(root)
    manifest["created_at"] = utc_now()
    run_dir.mkdir(parents=True, exist_ok=False)
    (run_dir / "candidate").mkdir()
    (run_dir / "games").mkdir()
    (run_dir / "attempts").mkdir()
    atomic_bytes(run_dir / "candidate" / "agent.py", (root / "agent.py").read_bytes())
    atomic_json(run_dir / "manifest.json", manifest)
    event(run_dir, "prepared", manifest_sha256=sha256(run_dir / "manifest.json"))
    print(f"Prepared {len(schedule())} immutable games in {run_dir}", flush=True)


def verify_manifest(run_dir: Path, root: Path = ROOT) -> str:
    manifest = read_object(run_dir / "manifest.json")
    expected = frozen_inputs(root)
    expected["created_at"] = field_text(manifest, "created_at")
    if manifest != expected:
        raise ValueError(
            "manifest mismatch: source, harness, opponents, environment or suite changed"
        )
    if sha256(run_dir / "candidate" / "agent.py") != expected["candidate_sha256"]:
        raise ValueError("candidate snapshot hash differs from the frozen root agent.py")
    return sha256(run_dir / "manifest.json")


class ObservedAgent(Agent):
    """Observe the original wire runner; do not replace the referee or its clock."""

    def __init__(self, directory: Path, color: str, role: str) -> None:
        super().__init__(local(directory).command)
        self.color = color
        self.role = role
        self.startup_ms = 0.0
        self.start_failure: str | None = None
        self.moves: list[Object] = []

    def start(self, init_budget_s: float) -> None:
        started = time.perf_counter()
        try:
            super().start(init_budget_s)
        except AgentFailure as failure:
            self.start_failure = failure.reason
            raise
        finally:
            self.startup_ms = (time.perf_counter() - started) * 1000.0

    def move(self, fen: str, time_left_ms: int) -> str:
        started = time.perf_counter()
        uci: str | None = None
        error: str | None = None
        try:
            uci = super().move(fen, time_left_ms)
            return uci
        except AgentFailure as failure:
            error = failure.reason
            raise
        finally:
            elapsed_ms = (time.perf_counter() - started) * 1000.0
            self.moves.append(
                {
                    "fen": fen,
                    "input_time_left_ms": time_left_ms,
                    "elapsed_ms": elapsed_ms,
                    "estimated_after_reply_ms": time_left_ms - elapsed_ms,
                    "uci": uci,
                    "failure": error,
                }
            )

    def to_json(self) -> Object:
        inputs = [cast(int, move["input_time_left_ms"]) for move in self.moves]
        after = [cast(float, move["estimated_after_reply_ms"]) for move in self.moves]
        return {
            "color": self.color,
            "role": self.role,
            "command": list(self.command),
            "startup_ms": self.startup_ms,
            "startup_failure": self.start_failure,
            "stderr": self.stderr_tail,
            "moves": list(self.moves),
            "move_count": len(self.moves),
            "minimum_input_time_left_ms": min(inputs) if inputs else None,
            "minimum_estimated_after_reply_ms": min(after) if after else None,
            "timing_note": (
                "Input clock is the actual integer passed by the referee. After-reply clock is "
                "a perf_counter estimate excluding observation and referee overhead, before "
                "increment. The unchanged referee uses monotonic, which can be coarse on Windows."
            ),
        }


def failure_records(outcome: Outcome, agents: tuple[ObservedAgent, ObservedAgent]) -> list[Json]:
    records: list[Json] = []
    failed_colors: set[str] = set()
    for agent in agents:
        if agent.start_failure is not None:
            records.append(
                {
                    "color": agent.color,
                    "role": agent.role,
                    "stage": "startup",
                    "reason": agent.start_failure,
                }
            )
            failed_colors.add(agent.color)
        for move in agent.moves:
            if move["failure"] is not None:
                records.append(
                    {
                        "color": agent.color,
                        "role": agent.role,
                        "stage": "move",
                        "reason": move["failure"],
                    }
                )
                failed_colors.add(agent.color)
    if outcome.termination in FAILED_TERMINATIONS:
        losers = (
            {"white", "black"}
            if outcome.result == "void"
            else ({"black"} if outcome.result == "white" else {"white"})
        )
        for agent in agents:
            if agent.color in losers and agent.color not in failed_colors:
                records.append(
                    {
                        "color": agent.color,
                        "role": agent.role,
                        "stage": "referee",
                        "reason": outcome.termination,
                    }
                )
    return records


def validate_pgn(pgn: str, spec: GameSpec, result: str, termination: str) -> int:
    game = chess.pgn.read_game(io.StringIO(pgn))
    if game is None or game.errors:
        raise ValueError("missing or malformed PGN")
    if game.headers.get("Result") != RESULT_HEADERS.get(result):
        raise ValueError("PGN result does not match recorded result")
    if game.headers.get("Termination") != termination:
        raise ValueError("PGN termination does not match recorded termination")
    board = game.board()
    if board.fen() != spec.opening.fen:
        raise ValueError("PGN starts from a different opening")
    count = 0
    for move in game.mainline_moves():
        if move not in board.legal_moves:
            raise ValueError("illegal PGN move")
        board.push(move)
        count += 1
    if count > PLY_CAP:
        raise ValueError("PGN exceeds the unchanged referee ply cap")
    return count


def completed_record(run_dir: Path, spec: GameSpec, manifest_hash: str) -> Object | None:
    path = run_dir / "games" / f"{spec.identifier}.json"
    if not path.exists():
        return None
    record = read_object(path)
    if (
        record.get("spec") != spec.to_json()
        or record.get("status") != "completed"
        or record.get("manifest_sha256") != manifest_hash
    ):
        raise ValueError(f"completed game metadata mismatch: {spec.identifier}")
    attempt = record.get("attempt")
    if not isinstance(attempt, int) or isinstance(attempt, bool) or attempt < 1:
        raise ValueError("invalid completed attempt number")
    durable_path = run_dir / "attempts" / spec.identifier / f"{attempt:03d}" / "completed.json"
    if read_object(durable_path) != record:
        raise ValueError("canonical game differs from its durable completed attempt")
    pgn_path = run_dir / "games" / f"{spec.identifier}.pgn"
    if sha256(pgn_path) != record.get("pgn_sha256"):
        raise ValueError(f"completed PGN hash mismatch: {spec.identifier}")
    plies = validate_pgn(
        pgn_path.read_text(encoding="utf-8"),
        spec,
        field_text(record, "result"),
        field_text(record, "termination"),
    )
    if plies != record.get("plies"):
        raise ValueError(f"completed PGN ply count mismatch: {spec.identifier}")
    return record


def recover_attempts(run_dir: Path, manifest_hash: str) -> None:
    """Keep outcomes saved before a crash; retain interrupted attempts visibly."""
    specs = {spec.identifier: spec for spec in schedule()}
    for start_path in sorted((run_dir / "attempts").glob("*/*/start.json")):
        attempt_dir = start_path.parent
        start = read_object(start_path)
        if start.get("manifest_sha256") != manifest_hash:
            raise ValueError("attempt manifest hash mismatch")
        identifier = field_text(start, "game_id")
        spec = specs[identifier]
        outcome_path = attempt_dir / "completed.json"
        if outcome_path.exists():
            record = read_object(outcome_path)
            pgn_bytes = field_text(record, "pgn").encode("utf-8")
            pgn_source = attempt_dir / "game.pgn"
            if pgn_source.exists():
                if pgn_source.read_bytes() != pgn_bytes:
                    raise ValueError("attempt PGN differs from its durable completed outcome")
            else:
                atomic_bytes(pgn_source, pgn_bytes)
            destination = run_dir / "games" / f"{identifier}.json"
            if not destination.exists():
                pgn_destination = run_dir / "games" / f"{identifier}.pgn"
                if pgn_destination.exists():
                    if pgn_destination.read_bytes() != pgn_source.read_bytes():
                        raise ValueError("orphan canonical PGN differs from completed attempt")
                else:
                    atomic_bytes(pgn_destination, pgn_source.read_bytes())
                atomic_json(destination, record)
                event(
                    run_dir,
                    "recovered_completed_game",
                    game_id=identifier,
                    attempt=attempt_dir.name,
                )
            completed_record(run_dir, spec, manifest_hash)
        elif not (attempt_dir / "interrupted.json").exists():
            atomic_json(
                attempt_dir / "interrupted.json",
                {
                    "status": "interrupted",
                    "at": utc_now(),
                    "game_id": identifier,
                    "reason": "previous process ended before a durable outcome; evidence kept",
                    "manifest_sha256": manifest_hash,
                },
            )
            event(
                run_dir,
                "recovered_interrupted_attempt",
                game_id=identifier,
                attempt=attempt_dir.name,
            )


def run_game(run_dir: Path, spec: GameSpec, manifest_hash: str, root: Path = ROOT) -> Object:
    attempts = run_dir / "attempts" / spec.identifier
    attempts.mkdir(exist_ok=True)
    number = len(list(attempts.iterdir())) + 1
    attempt_dir = attempts / f"{number:03d}"
    attempt_dir.mkdir()
    candidate = run_dir / "candidate"
    opponent = root / "baselines" / spec.opponent
    plays_white = spec.candidate_color == "white"
    white = ObservedAgent(
        candidate if plays_white else opponent, "white", "candidate" if plays_white else "opponent"
    )
    black = ObservedAgent(
        opponent if plays_white else candidate, "black", "opponent" if plays_white else "candidate"
    )
    started_at = utc_now()
    atomic_json(
        attempt_dir / "start.json",
        {
            "game_id": spec.identifier,
            "attempt": number,
            "started_at": started_at,
            "manifest_sha256": manifest_hash,
            "spec": spec.to_json(),
            "white_command": list(white.command),
            "black_command": list(black.command),
        },
    )
    event(run_dir, "game_started", game_id=spec.identifier, attempt=number)
    started = time.perf_counter()
    try:
        outcome = play_match(
            white,
            black,
            spec.base_ms,
            spec.increment_ms,
            ply_cap=PLY_CAP,
            start_fen=spec.opening.fen,
        )
        elapsed_s = time.perf_counter() - started
        plies = validate_pgn(outcome.pgn, spec, outcome.result, outcome.termination)
        failures = failure_records(outcome, (white, black))
        candidate_result = (
            "void"
            if outcome.result == "void"
            else "draw"
            if outcome.result == "draw"
            else "win"
            if outcome.result == spec.candidate_color
            else "loss"
        )
        pgn_bytes = (outcome.pgn + "\n").encode("utf-8")
        record: Object = {
            "status": "completed",
            "game_id": spec.identifier,
            "attempt": number,
            "manifest_sha256": manifest_hash,
            "spec": spec.to_json(),
            "started_at": started_at,
            "finished_at": utc_now(),
            "elapsed_s": elapsed_s,
            "result": outcome.result,
            "candidate_result": candidate_result,
            "termination": outcome.termination,
            "plies": plies,
            "failures": failures,
            "white": white.to_json(),
            "black": black.to_json(),
            "pgn_sha256": hashlib.sha256(pgn_bytes).hexdigest(),
            "pgn": pgn_bytes.decode("utf-8"),
        }
        # The single durable outcome includes the PGN. A crash while publishing
        # the convenience copies can therefore recover without replaying a loss.
        atomic_json(attempt_dir / "completed.json", record)
        atomic_bytes(attempt_dir / "game.pgn", pgn_bytes)
        atomic_bytes(run_dir / "games" / f"{spec.identifier}.pgn", pgn_bytes)
        atomic_json(run_dir / "games" / f"{spec.identifier}.json", record)
        event(
            run_dir,
            "game_completed",
            game_id=spec.identifier,
            attempt=number,
            candidate_result=candidate_result,
            termination=outcome.termination,
            failures=failures,
            elapsed_s=elapsed_s,
        )
        return record
    except BaseException as error:
        if not (attempt_dir / "completed.json").exists():
            atomic_json(
                attempt_dir / "interrupted.json",
                {
                    "status": "interrupted",
                    "game_id": spec.identifier,
                    "manifest_sha256": manifest_hash,
                    "at": utc_now(),
                    "reason": f"{type(error).__name__}: {error}",
                    "white": white.to_json(),
                    "black": black.to_json(),
                },
            )
        event(
            run_dir,
            "runner_interrupted",
            game_id=spec.identifier,
            attempt=number,
            reason=f"{type(error).__name__}: {error}",
        )
        raise


def summary(run_dir: Path, manifest_hash: str) -> Object:
    records = [
        record
        for spec in schedule()
        if (record := completed_record(run_dir, spec, manifest_hash)) is not None
    ]
    counts: Object = {"win": 0, "draw": 0, "loss": 0, "void": 0}
    groups: Object = {}
    failures: list[Json] = []
    terminations: Object = {}
    elapsed_s = 0.0
    for record in records:
        result = field_text(record, "candidate_result")
        counts[result] = cast(int, counts[result]) + 1
        spec_value = cast(Object, record["spec"])
        group_name = f"{field_text(spec_value, 'clock')}-{field_text(spec_value, 'opponent')}"
        if group_name not in groups:
            groups[group_name] = {"win": 0, "draw": 0, "loss": 0, "void": 0}
        group = cast(Object, groups[group_name])
        group[result] = cast(int, group[result]) + 1
        termination = field_text(record, "termination")
        terminations[termination] = cast(int, terminations.get(termination, 0)) + 1
        elapsed_s += cast(float, record["elapsed_s"])
        for failure in cast(list[Object], record["failures"]):
            failures.append({"game_id": record["game_id"], **failure})
    interrupted: list[Json] = [
        str(path.relative_to(run_dir)).replace("\\", "/")
        for path in sorted((run_dir / "attempts").glob("*/*/interrupted.json"))
    ]
    candidate_failures = [
        failure
        for failure in failures
        if isinstance(failure, dict) and failure.get("role") == "candidate"
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "updated_at": utc_now(),
        "manifest_sha256": manifest_hash,
        "expected_games": len(schedule()),
        "completed_games": len(records),
        "complete": len(records) == len(schedule()),
        "candidate_results": counts,
        "by_clock_and_opponent": groups,
        "terminations": terminations,
        "failures": failures,
        "candidate_failure_count": len(candidate_failures),
        "interrupted_attempts": interrupted,
        "game_elapsed_s": elapsed_s,
        "interpretation": "v0 evolution/setup evidence; no promotion and no held-out claim",
        "all_checks_passed": None,
        "checks_note": "separate position, import, timing, lint and typing checks are required",
    }


def run_campaign(run_dir: Path, max_games: int | None = None, root: Path = ROOT) -> Object:
    if max_games is not None and max_games < 0:
        raise ValueError("max-games must be nonnegative")
    with campaign_lock(run_dir):
        manifest_hash = verify_manifest(run_dir, root)
        recover_attempts(run_dir, manifest_hash)
        event(run_dir, "run_invoked", command=list(sys.argv), max_games=max_games)
        played = 0
        for index, spec in enumerate(schedule(), 1):
            if completed_record(run_dir, spec, manifest_hash) is not None:
                continue
            if max_games is not None and played >= max_games:
                break
            verify_manifest(run_dir, root)
            print(f"Starting {index}/120 {spec.identifier}", flush=True)
            record = run_game(run_dir, spec, manifest_hash, root)
            played += 1
            state = summary(run_dir, manifest_hash)
            atomic_json(run_dir / "summary.json", state, replace=True)
            print(
                f"Finished {index}/120 {spec.identifier}: {record['candidate_result']} "
                f"by {record['termination']} ({record['elapsed_s']:.1f}s)",
                flush=True,
            )
        state = summary(run_dir, manifest_hash)
        atomic_json(run_dir / "summary.json", state, replace=True)
        event(
            run_dir,
            "run_finished",
            played=played,
            completed_games=state["completed_games"],
            complete=state["complete"],
        )
        print(json.dumps(state, indent=2), flush=True)
        return state


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "run", "summary"))
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument(
        "--max-games",
        type=int,
        default=None,
        help="pause after this many new games; never changes the fixed suite",
    )
    arguments = parser.parse_args()
    run_dir = arguments.run_dir.resolve()
    if arguments.action == "prepare":
        prepare(run_dir)
    elif arguments.action == "summary":
        with campaign_lock(run_dir):
            manifest_hash = verify_manifest(run_dir)
            recover_attempts(run_dir, manifest_hash)
            state = summary(run_dir, manifest_hash)
            atomic_json(run_dir / "summary.json", state, replace=True)
            print(json.dumps(state, indent=2))
    else:
        run_campaign(run_dir, arguments.max_games)


if __name__ == "__main__":
    main()
