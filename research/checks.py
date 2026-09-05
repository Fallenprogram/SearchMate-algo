"""Independent v0 contract fixtures and referee checks; never builds an archive.

Run with the same interpreter as the game campaign. The 96 timed calls use the
unchanged wire runner, including its process communication overhead.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import time
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

import chess

from harness.package import DEFAULT_INCLUDES, members
from harness.referee import play_match
from harness.rules import INIT_BUDGET_S, MAX_UNZIPPED_BYTES
from harness.sandbox import Agent, AgentFailure, local

ROOT = Path(__file__).resolve().parents[1]
CLOCKS_MS = (20, 100, 1_000, 10_000)


@dataclass(frozen=True)
class Fixture:
    name: str
    fen: str
    feature: str = "legal"


def from_san(name: str, moves: str) -> Fixture:
    board = chess.Board()
    for san in moves.split():
        board.push_san(san)
    return Fixture(name, board.fen())


def fixtures() -> list[Fixture]:
    """Original coverage examples; these are development tests, not engine labels."""
    opening = [
        from_san("initial_white", ""),
        from_san("initial_black", "e4"),
        from_san("open_game", "e4 e5 Nf3 Nc6 Bc4 Bc5"),
        from_san("sicilian", "e4 c5 Nf3 d6 d4 cxd4 Nxd4 Nf6"),
        from_san("french", "e4 e6 d4 d5 Nc3 Nf6"),
        from_san("caro_kann", "e4 c6 d4 d5 e5 Bf5"),
        from_san("queens_gambit", "d4 d5 c4 e6 Nc3 Nf6"),
        from_san("kings_indian", "d4 Nf6 c4 g6 Nc3 Bg7 e4 d6"),
        from_san("english", "c4 e5 Nc3 Nf6 g3 d5"),
        from_san("reti", "Nf3 d5 g3 Nf6 Bg2 e6"),
        from_san("middlegame", "e4 e5 Nf3 Nc6 Bb5 a6 Ba4 Nf6 O-O Be7 Re1 b5 Bb3 d6"),
        from_san("queen_check", "e4 e5 Qh5 Nc6 Bc4 Nf6"),
    ]
    special = [
        Fixture("white_castling", "r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1", "castle"),
        Fixture("black_castling", "r3k2r/8/8/8/8/8/8/R3K2R b KQkq - 0 1", "castle"),
        Fixture("white_en_passant", "4k3/8/8/3pP3/8/8/8/4K3 w - d6 0 1", "ep"),
        Fixture("black_en_passant", "4k3/8/8/8/3Pp3/8/8/4K3 b - d3 0 1", "ep"),
        Fixture("white_promotion", "4k3/P7/8/8/8/8/8/4K3 w - - 0 1", "promotion"),
        Fixture("black_promotion", "4k3/8/8/8/8/8/7p/4K3 b - - 0 1", "promotion"),
        Fixture("capture_promotion", "1r2k3/P7/8/8/8/8/8/4K3 w - - 0 1", "promotion"),
        Fixture("forced_evasion", "7k/8/6K1/8/8/8/8/7R b - - 0 1", "forced"),
        Fixture("rook_check", "4k3/8/8/8/8/8/4r3/4K2R w - - 0 1", "check"),
        Fixture("pawn_ending", "8/4k3/4p3/3pP3/3P4/4K3/8/8 w - - 0 1"),
        Fixture("rook_ending", "8/4k3/6r1/7p/P7/1R6/4K3/8 b - - 0 1"),
        Fixture("mate_in_one", "7k/5Q2/6K1/8/8/8/8/8 w - - 0 1"),
    ]
    return opening + special


def validate_fixtures(cases: list[Fixture]) -> None:
    assert len(cases) == 24
    assert len({case.fen for case in cases}) == 24
    for case in cases:
        board = chess.Board(case.fen)
        assert board.is_valid(), case.name
        assert board.outcome(claim_draw=True) is None, case.name
        moves = list(board.legal_moves)
        assert moves, case.name
        if case.feature == "castle":
            assert any(board.is_castling(move) for move in moves), case.name
        elif case.feature == "ep":
            assert any(board.is_en_passant(move) for move in moves), case.name
        elif case.feature == "promotion":
            assert {move.promotion for move in moves if move.promotion} == {2, 3, 4, 5}
        elif case.feature == "forced":
            assert len(moves) == 1, (case.name, moves)
        elif case.feature == "check":
            assert board.is_check(), case.name


def load_player(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location("searchmate_checked_player", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ScriptedAgent(Agent):
    """In-memory moves for referee checks, with no change to referee behavior."""

    def __init__(self, moves: list[str]) -> None:
        super().__init__([])
        self.moves = iter(moves)

    def start(self, init_budget_s: float) -> None:
        pass

    def move(self, fen: str, time_left_ms: int) -> str:
        return next(self.moves)

    def stop(self) -> None:
        pass


def internal_checks(player: ModuleType) -> list[str]:
    passed: list[str] = []
    # Fixed depth makes the choice independent of wall-time speed.
    mate_fen = "7k/5Q2/6K1/8/8/8/8/8 w - - 0 1"
    for board in (chess.Board(mate_fen), chess.Board(mate_fen).mirror()):
        original = board.fen()
        move, _ = player._search_root(board, 1, time.perf_counter() + 10)
        assert board.fen() == original and not board.move_stack
        board.push(move)
        assert board.is_checkmate(), move.uci()
    passed.append("mate_in_one_both_colors_fixed_depth")

    terminal_cases = {
        "checkmate": "7k/6Q1/6K1/8/8/8/8/8 b - - 0 1",
        "stalemate": "7k/5Q2/6K1/8/8/8/8/8 b - - 0 1",
        "insufficient_material": "4k3/8/8/8/8/8/8/4K3 w - - 0 1",
        "fifty_move_draw": "4k3/8/8/8/8/8/8/R3K3 w - - 100 51",
        "mate_before_draw": "7k/6Q1/6K1/8/8/8/8/8 b - - 100 51",
    }
    for name, fen in terminal_cases.items():
        board = chess.Board(fen)
        score = player._terminal_score(board, 0)
        if board.is_checkmate():
            assert score is not None and score < -10_000, name
        else:
            assert score == 0, name
        outcome = play_match(ScriptedAgent([]), ScriptedAgent([]), 1_000, 0, start_fen=fen)
        assert outcome.result == ("white" if board.is_checkmate() else "draw"), name
        passed.append(f"terminal_and_referee_{name}")

    repetition = chess.Board()
    for uci in ("g1f3", "g8f6", "f3g1", "f6g8") * 2:
        repetition.push_uci(uci)
    assert player._terminal_score(repetition, 8) == 0
    outcome = play_match(
        ScriptedAgent(["g1f3", "f3g1"] * 2),
        ScriptedAgent(["g8f6", "f6g8"] * 2),
        1_000,
        0,
    )
    assert outcome.result == "draw" and outcome.termination == "threefold_repetition"
    passed.append("search_and_referee_repetition")

    board = chess.Board()
    original = board.fen()
    try:
        player._search_root(board, 10, time.perf_counter() - 1)
    except player._SearchTimeout:
        pass
    else:
        raise AssertionError("Expired deadline did not interrupt the search")
    assert board.fen() == original and not board.move_stack
    passed.append("expired_deadline_preserves_board")
    # A non-zero material imbalance must be evaluated from the side to move.
    board = chess.Board("4k3/8/8/8/8/8/8/R3K3 w - - 0 1")
    score = player._evaluate(board)
    board.turn = not board.turn
    assert score > 0 and player._evaluate(board) == -score
    passed.append("evaluation_side_to_move")
    first, _ = player._search_root(chess.Board(), 2, time.perf_counter() + 10)
    second, _ = player._search_root(chess.Board(), 2, time.perf_counter() + 10)
    assert first == second
    passed.append("fixed_depth_determinism")
    return passed


def package_proposal(directory: Path) -> dict[str, object]:
    entries = list(members(directory, DEFAULT_INCLUDES))
    assert [name for _, name in entries] == ["agent.py"], entries
    total = sum(path.stat().st_size for path, _ in entries)
    assert total <= MAX_UNZIPPED_BYTES
    tree = ast.parse((directory / "agent.py").read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert imported <= {"__future__", "chess", "time", "math", "collections", "typing"}
    return {
        "files": [name for _, name in entries],
        "uncompressed_bytes": total,
        "imports": sorted(imported),
        "archive_created": False,
        "platform_checks": "pending",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent", type=Path, default=ROOT)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    directory: Path = args.agent.resolve()
    output: Path = args.out.resolve()
    if output.exists():
        raise SystemExit("Refusing to overwrite completed check evidence")
    cases = fixtures()
    validate_fixtures(cases)
    player = load_player(directory / "agent.py")
    internal = internal_checks(player)
    proposal = package_proposal(directory)
    calls: list[dict[str, object]] = []
    failures: list[str] = []
    process = local(directory)
    started = time.perf_counter()
    try:
        process.start(INIT_BUDGET_S)
        import_ms = (time.perf_counter() - started) * 1_000
        for case in cases:
            for remaining in CLOCKS_MS:
                call_start = time.perf_counter()
                move = ""
                error = ""
                try:
                    move = process.move(case.fen, remaining)
                    elapsed = (time.perf_counter() - call_start) * 1_000
                    board = chess.Board(case.fen)
                    if chess.Move.from_uci(move) not in board.legal_moves:
                        error = "illegal"
                    elif elapsed >= remaining:
                        error = "clock_overrun"
                except (AgentFailure, ValueError) as exc:
                    elapsed = (time.perf_counter() - call_start) * 1_000
                    error = str(exc)
                calls.append({
                    "fixture": case.name, "fen": case.fen, "remaining_ms": remaining,
                    "move": move, "elapsed_ms": elapsed, "error": error,
                })
                if error:
                    failures.append(f"{case.name}@{remaining}: {error}")
    finally:
        process.stop()
    report = {
        "schema_version": 1,
        "agent_sha256": hashlib.sha256((directory / "agent.py").read_bytes()).hexdigest(),
        "internal_checks": internal, "fixture_calls": calls, "failures": failures,
        "import_ms": import_ms, "package_proposal": proposal,
        "stderr": process.stderr_tail, "passed": not failures and len(calls) == 96,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "passed": report["passed"], "internal_checks": len(internal),
        "fixture_calls": len(calls), "failures": failures, "output": str(output),
    }))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
