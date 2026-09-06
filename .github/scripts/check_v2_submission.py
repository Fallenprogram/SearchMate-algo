"""Check the frozen v2-01 release in a restricted, nonofficial Linux container.

This opt-in release check never writes the repository's submission.zip, promotes
a champion, or uploads to the competition. The temporary archive is deterministic
and can be compared against a separately prepared local release by SHA-256.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
import zipfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent.parent
SOURCE_PATH = "research/releases/v2-01/player/agent.py"
TESTED_SOURCE_PATH = "research/runs/v2-01/candidate/agent.py"
CANDIDATE_SHA256 = "1bec488584769b1d58e9e9d38851d696c5285379e96390b468689131fc8b4cee"
FULL_GAME_PLY_CAP = 600
LIMITATIONS = [
    "This is python:3.12-slim with chess 1.11.2, not the official competition image.",
    "The GitHub runner CPU model and scheduler differ from the competition host.",
    "The harness, opponent, and candidate share the container's CPU and memory limits.",
    "The repository harness does not suspend a player while its opponent thinks.",
    "The unchanged harness receives an explicit 600-ply cap. Its material adjudication "
    "at that boundary is not the platform's draw rule, so any cap ending fails this check.",
    "A pass is compatibility evidence; only the dashboard establishes upload acceptance.",
]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def save_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def emit(kind: str, **fields: Any) -> None:
    print(json.dumps({"kind": kind, **fields}, sort_keys=True), flush=True)


def make_package(root: Path, work: Path, expected: str, expected_zip: str) -> dict[str, Any]:
    """Package exactly the two agreeing frozen source copies; never use root/agent.py."""
    require(re.fullmatch(r"[0-9a-f]{64}", expected) is not None, "invalid agent SHA-256")
    require(expected == CANDIDATE_SHA256, "release does not identify the frozen v2-01 candidate")
    require(re.fullmatch(r"[0-9a-f]{64}", expected_zip) is not None, "invalid ZIP SHA-256")
    for relative in (SOURCE_PATH, TESTED_SOURCE_PATH):
        path = root / relative
        require(path.resolve().is_relative_to(root.resolve()), "source resolves outside repository")
        require(path.is_file() and not path.is_symlink(), "source must be a regular file")
    source = (root / SOURCE_PATH).read_bytes()
    frozen = (root / TESTED_SOURCE_PATH).read_bytes()
    require(digest(source) == expected, "release player differs from the recorded SHA-256")
    require(digest(frozen) == expected, "tested candidate differs from the recorded SHA-256")
    require(frozen == source, "release player differs from the tested v2-01 snapshot")
    imports: list[str] = []
    for node in ast.walk(ast.parse(source)):
        require(not isinstance(node, ast.ImportFrom), "unexpected candidate import-from statement")
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
    require(sorted(imports) == ["chess", "time"], "candidate imports differ from reviewed scope")
    require(0 < len(source) <= 50_000_000, "invalid uncompressed package size")
    archive = work / "submission.zip"
    member = zipfile.ZipInfo("agent.py", date_time=(1980, 1, 1, 0, 0, 0))
    member.create_system = 3
    member.external_attr = 0o100644 << 16
    member.compress_type = zipfile.ZIP_STORED
    with zipfile.ZipFile(archive, "w") as output:
        output.writestr(member, source)
    archive_hash = digest(archive.read_bytes())
    require(archive_hash == expected_zip, "temporary ZIP differs from the recorded release ZIP")
    extracted = work / "player"
    extracted.mkdir(mode=0o755)
    with zipfile.ZipFile(archive) as incoming:
        require(incoming.namelist() == ["agent.py"], "unexpected archive members")
        require(incoming.testzip() is None, "archive CRC verification failed")
        require(incoming.getinfo("agent.py").file_size == len(source), "archive size mismatch")
        require(incoming.read("agent.py") == source, "archive content mismatch")
        incoming.extractall(extracted)
    (extracted / "agent.py").chmod(0o644)
    require((extracted / "agent.py").read_bytes() == source, "extracted source mismatch")
    return {
        "members": ["agent.py"], "uncompressed_bytes": len(source),
        "agent_sha256": expected, "zip_sha256": archive_hash,
        "zip_bytes": archive.stat().st_size, "zip_method": "stored",
        "zip_timestamp": "1980-01-01T00:00:00", "zip_unix_mode": "100644",
        "source_path": SOURCE_PATH, "tested_source_path": TESTED_SOURCE_PATH,
        "source_and_tested_snapshot_identical": True, "extraction_verified": True,
        "runtime_imports": sorted(imports),
    }


def prepare_support(root: Path, work: Path) -> Path:
    # The player process cannot fall back to root/agent.py: it is never mounted.
    sys.path.insert(0, str(root))
    from research.checks import CLOCKS_MS, fixtures, validate_fixtures

    cases = fixtures()
    validate_fixtures(cases)
    support = work / "checks"
    support.mkdir(mode=0o755)
    shutil.copytree(root / "harness", support / "harness", ignore=shutil.ignore_patterns(
        "__pycache__", "*.pyc"))
    greedy = support / "baselines/greedy"
    greedy.mkdir(parents=True)
    shutil.copy2(root / "baselines/greedy/agent.py", greedy / "agent.py")
    shutil.copy2(Path(__file__), support / "check_v2_submission.py")
    save_json(support / "fixtures.json", [
        {"fixture": case.name, "fen": case.fen, "remaining_ms": clock}
        for case in cases for clock in CLOCKS_MS
    ])
    for path in support.rglob("*"):
        path.chmod(0o755 if path.is_dir() else 0o644)
    return support


def run_logged(command: list[str], output: Path, timeout: int) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(
            command, capture_output=True, text=True, timeout=timeout, check=False)
    except subprocess.TimeoutExpired as error:
        stdout = error.stdout or b""
        stderr = error.stderr or b""
        output.with_suffix(".stdout.txt").write_bytes(
            stdout.encode() if isinstance(stdout, str) else stdout)
        output.with_suffix(".stderr.txt").write_bytes(
            stderr.encode() if isinstance(stderr, str) else stderr)
        raise
    output.with_suffix(".stdout.txt").write_text(result.stdout, encoding="utf-8")
    output.with_suffix(".stderr.txt").write_text(result.stderr, encoding="utf-8")
    return result


def verify_container(metadata: dict[str, Any]) -> None:
    """Check Docker's effective configuration, not just the requested command."""
    config = metadata["HostConfig"]
    for field, expected in {
        "NetworkMode": "none", "NanoCpus": 1_000_000_000,
        "Memory": 2_000_000_000, "MemorySwap": 2_000_000_000,
        "PidsLimit": 128, "ReadonlyRootfs": True,
    }.items():
        require(config.get(field) == expected, f"container {field} restriction mismatch")
    require(metadata["Config"]["User"] == "65532:65532", "container is not the intended user")
    require("ALL" in config["CapDrop"], "container capabilities were not dropped")
    require("no-new-privileges" in config["SecurityOpt"], "missing no-new-privileges restriction")
    require(config["Tmpfs"].get("/tmp") == "rw,noexec,nosuid,size=256000000,mode=1777",
            "temporary filesystem restriction mismatch")
    mounts = {
        mount["Destination"]: mount for mount in metadata["Mounts"] if mount["Type"] == "bind"
    }
    require(set(mounts) == {"/checks", "/player"}, "unexpected container bind mounts")
    require(all(not mount["RW"] for mount in mounts.values()), "writable container bind mount")
    require(all(mount["Type"] == "bind" or
                (mount["Type"] == "tmpfs" and mount["Destination"] == "/tmp")
                for mount in metadata["Mounts"]), "unexpected extra container mount")


def outer(args: argparse.Namespace) -> int:
    output: Path = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    report: dict[str, Any] = {
        "passed": False, "limitations": LIMITATIONS,
        "candidate_id": "v2-01", "full_game_ply_cap": FULL_GAME_PLY_CAP,
        "source_commit": os.environ.get("GITHUB_SHA"),
        "github_run_id": os.environ.get("GITHUB_RUN_ID"),
    }
    container = "searchmate-v2-check-" + uuid.uuid4().hex
    image = container + ":local"
    try:
        require(args.release_metadata is not None, "release metadata is required")
        metadata_path: Path = args.release_metadata.resolve()
        metadata_bytes = metadata_path.read_bytes()
        metadata = json.loads(metadata_bytes)
        require(isinstance(metadata, dict), "release metadata must be an object")
        for field, expected_path in (("source_path", SOURCE_PATH),
                                     ("tested_source_path", TESTED_SOURCE_PATH)):
            require(metadata.get(field) == expected_path, f"unexpected release metadata {field}")
        for attribute, field in (("expected_agent_sha256", "agent_sha256"),
                                 ("expected_zip_sha256", "zip_sha256")):
            recorded = metadata.get(field)
            require(isinstance(recorded, str) and
                    re.fullmatch(r"[0-9a-f]{64}", recorded) is not None,
                    f"invalid release metadata {field}")
            requested = getattr(args, attribute).lower()
            require(not requested or requested == recorded,
                    f"requested {field} disagrees with committed release metadata")
            setattr(args, attribute, recorded)
        report["release_metadata_sha256"] = digest(metadata_bytes)
        (output / "release-metadata.json").write_bytes(metadata_bytes)
        with tempfile.TemporaryDirectory(prefix="searchmate-package-") as temporary:
            work = Path(temporary)
            report["package"] = make_package(
                ROOT, work, args.expected_agent_sha256.lower(), args.expected_zip_sha256.lower())
            save_json(output / "package.json", report["package"])
            shutil.copy2(work / "submission.zip", output / "submission.zip")
            support = prepare_support(ROOT, work)
            report["check_support_sha256"] = {
                path.relative_to(support).as_posix(): digest(path.read_bytes())
                for path in sorted(support.rglob("*")) if path.is_file()
            }
            dockerfile = work / "Dockerfile"
            dockerfile.write_text(
                "FROM python:3.12-slim\n"
                "RUN python -m pip install --no-cache-dir chess==1.11.2\n"
                "ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1\n"
                "USER 65532:65532\nWORKDIR /tmp\n", encoding="utf-8")
            build = run_logged(["docker", "build", "--pull", "-t", image, str(work)],
                               output / "image-build", 600)
            require(build.returncode == 0, "container image build failed; see image-build logs")
            command = [
                "docker", "run", "--name", container, "--network", "none", "--cpus", "1",
                "--memory", "2000000000", "--memory-swap", "2000000000",
                "--pids-limit", "128", "--read-only",
                "--tmpfs", "/tmp:rw,noexec,nosuid,size=256000000,mode=1777", "--cap-drop", "ALL",
                "--security-opt", "no-new-privileges", "--user", "65532:65532",
                "--env", "HOME=/tmp", "--env", "TMPDIR=/tmp", "--env", "XDG_CACHE_HOME=/tmp",
                "--mount", f"type=bind,src={work / 'player'},dst=/player,readonly",
                "--mount", f"type=bind,src={support},dst=/checks,readonly",
                image, "python", "-I", "/checks/check_v2_submission.py", "--inside",
                "--expected-agent-sha256", args.expected_agent_sha256.lower(),
            ]
            report["container_command"] = command
            runtime = run_logged(command, output / "runtime", 1500)
            report["container_exit_code"] = runtime.returncode
            records = [json.loads(line) for line in runtime.stdout.splitlines() if line.strip()]
            save_json(output / "runtime-records.json", records)
            summaries = [record for record in records if record.get("kind") == "summary"]
            require(runtime.returncode == 0, "container check failed; see runtime records/logs")
            require(len(summaries) == 1 and summaries[0].get("passed") is True,
                    "container did not report one successful completion")
            report["checks"] = summaries[0]
            report["passed"] = True
    except Exception as error:
        report["error"] = f"{type(error).__name__}: {error}"
    finally:
        if shutil.which("docker"):
            try:
                inspected = subprocess.run(["docker", "inspect", container], capture_output=True,
                                           text=True, check=False, timeout=30)
                if inspected.returncode == 0:
                    container_metadata = json.loads(inspected.stdout)
                    save_json(output / "container-inspect.json", container_metadata)
                    verify_container(container_metadata[0])
                    report["container_restrictions_verified"] = True
                    report["oom_killed"] = container_metadata[0]["State"]["OOMKilled"]
                    if report["oom_killed"]:
                        report["passed"] = False
                elif report["passed"]:
                    report["passed"] = False
                    report["error"] = "completed container could not be inspected"
            except Exception as error:
                report["passed"] = False
                report["inspection_error"] = f"{type(error).__name__}: {error}"
            for command in (["docker", "rm", "--force", container],
                            ["docker", "image", "rm", image]):
                try:
                    subprocess.run(command, capture_output=True, check=False, timeout=30)
                except Exception as error:
                    report.setdefault("cleanup_errors", []).append(str(error))
        save_json(output / "report.json", report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["passed"] else 1


def memory_observations() -> dict[str, Any]:
    if sys.platform == "win32":
        return {"unavailable": "container memory observations require Linux"}
    import resource

    observation: dict[str, Any] = {
        "driver_max_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "child_max_rss_kib": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
    }
    for filename in ("memory.peak", "memory.max", "memory.events", "cpu.max", "pids.max"):
        path = Path("/sys/fs/cgroup") / filename
        if path.is_file():
            observation[filename] = path.read_text().strip()
    return observation


def inside(expected: str) -> int:
    if sys.platform != "linux":
        raise RuntimeError("the restricted container checks require Linux")
    # Isolated mode omits the script's directory, so add only the mounted checks.
    sys.path.insert(0, "/checks")
    import chess

    from harness.referee import FAILED_TERMINATIONS, play_match
    from harness.rules import BASE_MS, INCREMENT_MS, INIT_BUDGET_S
    from harness.sandbox import local

    player = Path("/player")
    require(expected == CANDIDATE_SHA256, "unexpected candidate hash inside container")
    require(BASE_MS == 120_000 and INCREMENT_MS == 500 and INIT_BUDGET_S == 90.0,
            "harness clock or initialization constants differ from reviewed contract")
    require(digest((player / "agent.py").read_bytes()) == expected, "mounted source hash mismatch")
    require(not Path("/checks/agent.py").exists(), "test support exposes a fallback player")
    emit("environment", python=sys.version, platform=platform.platform(), chess=chess.__version__,
         machine=platform.machine(), uid=os.getuid(), memory=memory_observations(),
         limitations=LIMITATIONS)
    cases = json.loads(Path("/checks/fixtures.json").read_text())
    require(len(cases) == 96, "fixture count must be 96")
    results: list[dict[str, Any]] = []
    fresh: list[dict[str, Any]] = []
    for process_index in range(3):
        agent = local(player)
        try:
            started = time.perf_counter()
            agent.start(INIT_BUDGET_S)
            startup_ms = (time.perf_counter() - started) * 1000
            emit("startup", process_index=process_index, elapsed_ms=startup_ms)
            calls = cases if process_index == 0 else [cases[1]]
            for case in calls:
                started = time.perf_counter()
                move = agent.move(case["fen"], case["remaining_ms"])
                elapsed = (time.perf_counter() - started) * 1000
                board = chess.Board(case["fen"])
                record = {**case, "process_index": process_index, "move": move,
                          "elapsed_ms": elapsed, "passed": False}
                try:
                    require(chess.Move.from_uci(move) in board.legal_moves, "illegal fixture move")
                    require(elapsed < case["remaining_ms"], "fixture exceeded supplied clock")
                    record["passed"] = True
                finally:
                    emit("fixture" if process_index == 0 else "fresh_process", **record)
                (results if process_index == 0 else fresh).append(record)
        finally:
            agent.stop()
            if agent.stderr_tail:
                emit("player_stderr", process_index=process_index, text=agent.stderr_tail)
    games: list[dict[str, Any]] = []
    greedy = Path("/checks/baselines/greedy")
    natural_terminations = {termination.name.lower() for termination in chess.Termination}
    for color in ("white", "black"):
        white, black = (player, greedy) if color == "white" else (greedy, player)
        started = time.perf_counter()
        outcome = play_match(
            local(white), local(black), BASE_MS, INCREMENT_MS, ply_cap=FULL_GAME_PLY_CAP)
        record = {"candidate_color": color, "result": outcome.result,
                  "termination": outcome.termination, "pgn": outcome.pgn,
                  "elapsed_s": time.perf_counter() - started,
                  "base_ms": BASE_MS, "increment_ms": INCREMENT_MS,
                  "ply_cap": FULL_GAME_PLY_CAP,
                  "natural_termination": outcome.termination in natural_terminations,
                  "passed": outcome.termination not in FAILED_TERMINATIONS
                            and outcome.termination in natural_terminations
                            and outcome.result != "void"}
        emit("full_clock_game", **record)
        games.append(record)
    passed = (len(results) == 96 and len(fresh) == 2 and len(games) == 2
              and all(record["passed"] for record in [*results, *fresh, *games]))
    emit("summary", passed=passed, fixture_calls=len(results), fresh_process_calls=len(fresh),
         full_clock_games=len(games), full_game_ply_cap=FULL_GAME_PLY_CAP,
         cap_adjudication_accepted=False, memory=memory_observations(), limitations=LIMITATIONS)
    return 0 if passed else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-agent-sha256", default="")
    parser.add_argument("--expected-zip-sha256", default="")
    parser.add_argument("--release-metadata", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--inside", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.inside:
        try:
            return inside(args.expected_agent_sha256)
        except Exception as error:
            emit("error", error=f"{type(error).__name__}: {error}")
            return 1
    if args.output is None or args.release_metadata is None:
        parser.error("--output and --release-metadata are required outside the container")
    return outer(args)


if __name__ == "__main__":
    raise SystemExit(main())
