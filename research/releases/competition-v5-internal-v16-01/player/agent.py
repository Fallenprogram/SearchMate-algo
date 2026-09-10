"""SearchMate combined-clock-02: combined original search with adaptive clock policy 02.
All numeric search, history, hints, evaluation and KQK helpers retain the pinned core.
Only public clock allocation and iteration diagnostics change; no strength claim.
"""

from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any

import chess
import chess.syzygy
import numpy as np
from numba import njit, objmode
from numpy.typing import NDArray

# Original numeric board mechanics.


BoardArray = NDArray[np.int8]
StateArray = NDArray[np.int64]
MoveArray = NDArray[np.int32]

TURN = 0
RIGHTS = 1
EP = 2
HALF = 3
FULL = 4
WK_SQ = 5
BK_SQ = 6
STATE_WIDTH = 7
UNDO_WIDTH = 16
MAX_MOVES = 512

PAWN = 1
KNIGHT = 2
BISHOP = 3
ROOK = 4
QUEEN = 5
KING = 6
WK = 1
WQ = 2
BK = 4
BQ = 8
FLAG_EP = 1
FLAG_CASTLE = 2
FLAG_DOUBLE = 4

_NB_KNIGHT_STEPS = (33, 31, 18, 14, -14, -18, -31, -33)
_NB_KING_STEPS = (1, -1, 16, -16, 15, -15, 17, -17)
_NB_ROOK_STEPS = (1, -1, 16, -16)
_NB_BISHOP_STEPS = (15, -15, 17, -17)


@njit(cache=False)
def _nb_valid(square: int) -> bool:
    return 0 <= square < 128 and (square & 0x88) == 0


@njit(cache=False)
def _nb_pack(source: int, target: int, promotion: int = 0, flags: int = 0) -> int:
    return source | (target << 7) | (promotion << 14) | (flags << 17)


@njit(cache=False)
def is_attacked(board: BoardArray, square: int, by_side: int) -> bool:
    """Geometric attack test; it never calls move generation or changes state."""
    for delta in (15, 17):
        origin = square - by_side * delta
        if _nb_valid(origin) and board[origin] == by_side * PAWN:
            return True
    for delta in _NB_KNIGHT_STEPS:
        origin = square + delta
        if _nb_valid(origin) and board[origin] == by_side * KNIGHT:
            return True
    for delta in _NB_KING_STEPS:
        origin = square + delta
        if _nb_valid(origin) and board[origin] == by_side * KING:
            return True
    for delta in _NB_ROOK_STEPS:
        origin = square + delta
        while _nb_valid(origin):
            piece = int(board[origin])
            if piece:
                if piece == by_side * ROOK or piece == by_side * QUEEN:
                    return True
                break
            origin += delta
    for delta in _NB_BISHOP_STEPS:
        origin = square + delta
        while _nb_valid(origin):
            piece = int(board[origin])
            if piece:
                if piece == by_side * BISHOP or piece == by_side * QUEEN:
                    return True
                break
            origin += delta
    return False


@njit(cache=False)
def in_check(board: BoardArray, state: StateArray) -> bool:
    side = int(state[TURN])
    king = int(state[WK_SQ] if side == 1 else state[BK_SQ])
    return is_attacked(board, king, -side)


@njit(cache=False)
def _nb_remember(board: BoardArray, undo_row: StateArray, square: int) -> None:
    count = int(undo_row[7])
    for index in range(count):
        if undo_row[8 + index] == square:
            return
    if count >= 4:
        raise ValueError("Move exceeds undo capacity")
    undo_row[8 + count] = square
    undo_row[12 + count] = board[square]
    undo_row[7] = count + 1


@njit(cache=False)
def make_move(board: BoardArray, state: StateArray, move: int, undo_row: StateArray) -> None:
    """Apply an encoded pseudo-legal move. Caller supplies a free undo row."""
    source = move & 127
    target = (move >> 7) & 127
    promotion = (move >> 14) & 7
    flags = move >> 17
    side = int(state[TURN])
    if not _nb_valid(source) or not _nb_valid(target) or source == target:
        raise ValueError("Invalid encoded squares")
    piece = int(board[source])
    captured = int(board[target])
    if piece * side <= 0 or captured * side > 0 or abs(captured) == KING:
        raise ValueError("Invalid move ownership or king capture")
    if flags not in (0, FLAG_EP, FLAG_CASTLE, FLAG_DOUBLE):
        raise ValueError("Unknown move flags")
    if promotion and (
        abs(piece) != PAWN or promotion < KNIGHT or promotion > QUEEN or (target >> 4) not in (0, 7)
    ):
        raise ValueError("Invalid promotion")
    captured_square = target
    rook_source = -1
    rook_target = -1
    if flags == FLAG_EP:
        captured_square = target - side * 16
        if (
            abs(piece) != PAWN
            or target != state[EP]
            or captured != 0
            or not _nb_valid(captured_square)
            or board[captured_square] != -side * PAWN
        ):
            raise ValueError("Invalid en passant")
        captured = int(board[captured_square])
    elif flags == FLAG_CASTLE:
        rook_source = (source & 112) + (7 if target > source else 0)
        rook_target = source + (1 if target > source else -1)
        if (
            abs(piece) != KING
            or abs(target - source) != 2
            or captured != 0
            or board[rook_source] != side * ROOK
            or board[rook_target] != 0
        ):
            raise ValueError("Invalid castling structure")
    elif flags == FLAG_DOUBLE:
        if abs(piece) != PAWN or target - source != side * 32:
            raise ValueError("Invalid double pawn move")
    for index in range(STATE_WIDTH):
        undo_row[index] = state[index]
    undo_row[7] = 0
    _nb_remember(board, undo_row, source)
    _nb_remember(board, undo_row, target)
    if flags == FLAG_EP:
        _nb_remember(board, undo_row, captured_square)
    elif flags == FLAG_CASTLE:
        _nb_remember(board, undo_row, rook_source)
        _nb_remember(board, undo_row, rook_target)
    board[source] = 0
    board[target] = side * promotion if promotion else piece
    if flags == FLAG_EP:
        board[captured_square] = 0
    elif flags == FLAG_CASTLE:
        board[rook_source] = 0
        board[rook_target] = side * ROOK
    rights = int(state[RIGHTS])
    if abs(piece) == KING:
        if side == 1:
            state[WK_SQ] = target
            rights &= ~(WK | WQ)
        else:
            state[BK_SQ] = target
            rights &= ~(BK | BQ)
    for corner, bit in ((0, WQ), (7, WK), (112, BQ), (119, BK)):
        if source == corner or target == corner:
            rights &= ~bit
    state[RIGHTS] = rights
    state[EP] = (source + target) // 2 if flags == FLAG_DOUBLE else -1
    state[HALF] = 0 if abs(piece) == PAWN or captured else state[HALF] + 1
    if side == -1:
        state[FULL] += 1
    state[TURN] = -side


@njit(cache=False)
def unmake_move(board: BoardArray, state: StateArray, undo_row: StateArray) -> None:
    """Restore every changed square and every metadata field exactly."""
    for index in range(int(undo_row[7])):
        board[int(undo_row[8 + index])] = undo_row[12 + index]
    for index in range(STATE_WIDTH):
        state[index] = undo_row[index]


@njit(cache=False)
def _nb_legal(board: BoardArray, state: StateArray, move: int, undo_row: StateArray) -> bool:
    side = int(state[TURN])
    make_move(board, state, move, undo_row)
    king = int(state[WK_SQ] if side == 1 else state[BK_SQ])
    legal = not is_attacked(board, king, -side)
    unmake_move(board, state, undo_row)
    return legal


@njit(cache=False)
def _nb_offer(
    board: BoardArray,
    state: StateArray,
    move: int,
    out_moves: MoveArray,
    count: int,
    undo_row: StateArray,
) -> int:
    if _nb_legal(board, state, move, undo_row):
        if count >= out_moves.size:
            raise ValueError("Legal move buffer exhausted")
        out_moves[count] = move
        count += 1
    return count


@njit(cache=False)
def _nb_castle_route(
    board: BoardArray, state: StateArray, king_side: bool, undo_row: StateArray
) -> bool:
    side = int(state[TURN])
    origin = 4 if side == 1 else 116
    right = (WK if king_side else WQ) if side == 1 else (BK if king_side else BQ)
    rook = (7 if king_side else 0) + (0 if side == 1 else 112)
    if (state[RIGHTS] & right) == 0 or board[origin] != side * KING or board[rook] != side * ROOK:
        return False
    direction = 1 if king_side else -1
    square = origin + direction
    while square != rook:
        if board[square] != 0:
            return False
        square += direction
    if is_attacked(board, origin, -side):
        return False
    # Transit must be checked with the king's origin vacated, before moving the rook.
    return _nb_legal(board, state, _nb_pack(origin, origin + direction), undo_row)


@njit(cache=False)
def _nb_generate_tactical(
    board: BoardArray,
    state: StateArray,
    out_moves: MoveArray,
    undo_row: StateArray,
    stop_first: bool,
) -> int:
    count = 0
    side = int(state[TURN])
    for source in range(128):
        if not _nb_valid(source):
            continue
        piece = int(board[source])
        if piece * side <= 0:
            continue
        kind = abs(piece)
        if kind == PAWN:
            target = source + side * 16
            if (
                _nb_valid(target)
                and board[target] == 0
                and (target >> 4) == (7 if side == 1 else 0)
            ):
                for promotion in (KNIGHT, BISHOP, ROOK, QUEEN):
                    count = _nb_offer(
                        board,
                        state,
                        _nb_pack(source, target, promotion),
                        out_moves,
                        count,
                        undo_row,
                    )
                    if stop_first and count:
                        return count
            for delta in (15, 17):
                target = source + side * delta
                if not _nb_valid(target):
                    continue
                victim = int(board[target])
                if victim * side < 0 and abs(victim) != KING:
                    if (target >> 4) == (7 if side == 1 else 0):
                        for promotion in (KNIGHT, BISHOP, ROOK, QUEEN):
                            count = _nb_offer(
                                board,
                                state,
                                _nb_pack(source, target, promotion),
                                out_moves,
                                count,
                                undo_row,
                            )
                            if stop_first and count:
                                return count
                    else:
                        count = _nb_offer(
                            board, state, _nb_pack(source, target), out_moves, count, undo_row
                        )
                        if stop_first and count:
                            return count
                elif (
                    target == state[EP]
                    and victim == 0
                    and board[target - side * 16] == -side * PAWN
                ):
                    count = _nb_offer(
                        board,
                        state,
                        _nb_pack(source, target, 0, FLAG_EP),
                        out_moves,
                        count,
                        undo_row,
                    )
                    if stop_first and count:
                        return count
        elif kind in (KNIGHT, KING):
            steps = _NB_KNIGHT_STEPS if kind == KNIGHT else _NB_KING_STEPS
            for delta in steps:
                target = source + delta
                if not _nb_valid(target):
                    continue
                victim = int(board[target])
                if victim * side < 0 and abs(victim) != KING:
                    count = _nb_offer(
                        board, state, _nb_pack(source, target), out_moves, count, undo_row
                    )
                    if stop_first and count:
                        return count
        else:
            for delta in _NB_KING_STEPS:
                diagonal = abs(delta) == 15 or abs(delta) == 17
                if (kind == BISHOP and not diagonal) or (kind == ROOK and diagonal):
                    continue
                target = source + delta
                while _nb_valid(target):
                    victim = int(board[target])
                    if victim * side > 0 or abs(victim) == KING:
                        break
                    if victim:
                        count = _nb_offer(
                            board, state, _nb_pack(source, target), out_moves, count, undo_row
                        )
                        if stop_first and count:
                            return count
                        break
                    target += delta
    return count


@njit(cache=False)
def _nb_generate(
    board: BoardArray,
    state: StateArray,
    out_moves: MoveArray,
    undo_row: StateArray,
    stop_first: bool,
) -> int:
    count = 0
    side = int(state[TURN])
    for source in range(128):
        if not _nb_valid(source):
            continue
        piece = int(board[source])
        if piece * side <= 0:
            continue
        kind = abs(piece)
        if kind == PAWN:
            target = source + side * 16
            if _nb_valid(target) and board[target] == 0:
                if (target >> 4) == (7 if side == 1 else 0):
                    for promotion in (KNIGHT, BISHOP, ROOK, QUEEN):
                        count = _nb_offer(
                            board,
                            state,
                            _nb_pack(source, target, promotion),
                            out_moves,
                            count,
                            undo_row,
                        )
                        if stop_first and count:
                            return count
                else:
                    count = _nb_offer(
                        board, state, _nb_pack(source, target), out_moves, count, undo_row
                    )
                    if stop_first and count:
                        return count
                    double = source + side * 32
                    if (source >> 4) == (1 if side == 1 else 6) and board[double] == 0:
                        count = _nb_offer(
                            board,
                            state,
                            _nb_pack(source, double, 0, FLAG_DOUBLE),
                            out_moves,
                            count,
                            undo_row,
                        )
                        if stop_first and count:
                            return count
            for delta in (15, 17):
                target = source + side * delta
                if not _nb_valid(target):
                    continue
                victim = int(board[target])
                if victim * side < 0 and abs(victim) != KING:
                    if (target >> 4) == (7 if side == 1 else 0):
                        for promotion in (KNIGHT, BISHOP, ROOK, QUEEN):
                            count = _nb_offer(
                                board,
                                state,
                                _nb_pack(source, target, promotion),
                                out_moves,
                                count,
                                undo_row,
                            )
                            if stop_first and count:
                                return count
                    else:
                        count = _nb_offer(
                            board, state, _nb_pack(source, target), out_moves, count, undo_row
                        )
                        if stop_first and count:
                            return count
                elif (
                    target == state[EP]
                    and victim == 0
                    and board[target - side * 16] == -side * PAWN
                ):
                    count = _nb_offer(
                        board,
                        state,
                        _nb_pack(source, target, 0, FLAG_EP),
                        out_moves,
                        count,
                        undo_row,
                    )
                    if stop_first and count:
                        return count
        elif kind in (KNIGHT, KING):
            steps = _NB_KNIGHT_STEPS if kind == KNIGHT else _NB_KING_STEPS
            for delta in steps:
                target = source + delta
                if not _nb_valid(target):
                    continue
                victim = int(board[target])
                if victim * side <= 0 and abs(victim) != KING:
                    count = _nb_offer(
                        board, state, _nb_pack(source, target), out_moves, count, undo_row
                    )
                    if stop_first and count:
                        return count
            if kind == KING and source == (4 if side == 1 else 116):
                for king_side in (True, False):
                    if _nb_castle_route(board, state, king_side, undo_row):
                        target = source + (2 if king_side else -2)
                        count = _nb_offer(
                            board,
                            state,
                            _nb_pack(source, target, 0, FLAG_CASTLE),
                            out_moves,
                            count,
                            undo_row,
                        )
                        if stop_first and count:
                            return count
        else:
            for delta in _NB_KING_STEPS:
                diagonal = abs(delta) == 15 or abs(delta) == 17
                if (kind == BISHOP and not diagonal) or (kind == ROOK and diagonal):
                    continue
                target = source + delta
                while _nb_valid(target):
                    victim = int(board[target])
                    if victim * side > 0 or abs(victim) == KING:
                        break
                    count = _nb_offer(
                        board, state, _nb_pack(source, target), out_moves, count, undo_row
                    )
                    if stop_first and count:
                        return count
                    if victim:
                        break
                    target += delta
    return count


@njit(cache=False)
def generate_legal(
    board: BoardArray, state: StateArray, out_moves: MoveArray, probe_undo_row: StateArray
) -> int:
    """Fill caller's move buffer; never truncate and always restore board/state."""
    return _nb_generate(board, state, out_moves, probe_undo_row, False)


@njit(cache=False)
def has_legal_move(board: BoardArray, state: StateArray, probe_undo_row: StateArray) -> bool:
    one = np.empty(1, dtype=np.int32)
    return _nb_generate(board, state, one, probe_undo_row, True) != 0


@njit(cache=False)
def has_legal_ep(board: BoardArray, state: StateArray, probe_undo_row: StateArray) -> bool:
    target = int(state[EP])
    side = int(state[TURN])
    if not _nb_valid(target) or (target >> 4) != (5 if side == 1 else 2) or board[target] != 0:
        return False
    if board[target - side * 16] != -side * PAWN:
        return False
    for delta in (15, 17):
        source = target - side * delta
        if (
            _nb_valid(source)
            and board[source] == side * PAWN
            and _nb_legal(board, state, _nb_pack(source, target, 0, FLAG_EP), probe_undo_row)
        ):
            return True
    return False


@njit(cache=False)
def insufficient_material(board: BoardArray) -> bool:
    """Match standard python-chess material-only insufficiency, not fortress claims."""
    knights = 0
    bishops = 0
    bishop_color = -1
    mixed_bishops = False
    for square in range(128):
        if not _nb_valid(square):
            continue
        piece = abs(int(board[square]))
        if piece in (PAWN, ROOK, QUEEN):
            return False
        if piece == KNIGHT:
            knights += 1
        elif piece == BISHOP:
            bishops += 1
            color = ((square >> 4) + (square & 7)) & 1
            if bishop_color == -1:
                bishop_color = color
            elif color != bishop_color:
                mixed_bishops = True
    return knights + bishops <= 1 or (knights == 0 and not mixed_bishops)


def from_fen(fen: str) -> tuple[BoardArray, StateArray]:
    """Validate standard FEN and create fresh arrays; no history is inferred."""
    parts = fen.split()
    if len(parts) != 6 or "~" in fen or any(c not in "KQkq-" for c in parts[2]):
        raise ValueError("Expected ordinary six-field standard-chess FEN")
    position = chess.Board(fen)
    if not position.is_valid():
        raise ValueError("Invalid chess position")
    board = np.zeros(128, dtype=np.int8)
    square: int | None
    for square, piece in position.piece_map().items():
        numeric = 16 * chess.square_rank(square) + chess.square_file(square)
        board[numeric] = piece.piece_type if piece.color else -piece.piece_type
    state = np.zeros(STATE_WIDTH, dtype=np.int64)
    state[TURN] = 1 if position.turn else -1
    for color, king_side, bit in (
        (True, True, WK),
        (True, False, WQ),
        (False, True, BK),
        (False, False, BQ),
    ):
        allowed = (
            position.has_kingside_castling_rights(color)
            if king_side
            else position.has_queenside_castling_rights(color)
        )
        if allowed:
            state[RIGHTS] |= bit
    square = position.ep_square
    state[EP] = -1 if square is None else 16 * chess.square_rank(square) + chess.square_file(square)
    state[HALF] = position.halfmove_clock
    state[FULL] = position.fullmove_number
    for color, slot in ((True, WK_SQ), (False, BK_SQ)):
        king = position.king(color)
        if king is None:
            raise ValueError("Missing king")
        state[slot] = 16 * chess.square_rank(king) + chess.square_file(king)
    return board, state


def _nb_square_name(square: int) -> str:
    if square < 0 or square >= 128 or square & 0x88:
        raise ValueError("Invalid 0x88 square")
    return chr(97 + (square & 7)) + chr(49 + (square >> 4))


def to_fen(board: BoardArray, state: StateArray, legal_ep: bool = False) -> str:
    """Export raw EP by default, matching fen(en_passant='fen')."""
    ranks: list[str] = []
    symbols = " pnbrqk"
    for rank in range(7, -1, -1):
        row = ""
        empty = 0
        for file in range(8):
            piece = int(board[rank * 16 + file])
            if piece == 0:
                empty += 1
            else:
                if empty:
                    row += str(empty)
                    empty = 0
                symbol = symbols[abs(piece)]
                row += symbol.upper() if piece > 0 else symbol
        if empty:
            row += str(empty)
        ranks.append(row)
    rights = (
        "".join(
            letter
            for bit, letter in ((WK, "K"), (WQ, "Q"), (BK, "k"), (BQ, "q"))
            if int(state[RIGHTS]) & bit
        )
        or "-"
    )
    ep_square = int(state[EP])
    if (
        legal_ep
        and ep_square != -1
        and not has_legal_ep(board, state, np.empty(UNDO_WIDTH, dtype=np.int64))
    ):
        ep_square = -1
    ep = "-" if ep_square == -1 else _nb_square_name(ep_square)
    turn = "w" if state[TURN] == 1 else "b"
    return f"{'/'.join(ranks)} {turn} {rights} {ep} {int(state[HALF])} {int(state[FULL])}"


def move_to_uci(move: int) -> str:
    source = move & 127
    target = (move >> 7) & 127
    promotion = (move >> 14) & 7
    result = _nb_square_name(source) + _nb_square_name(target)
    if promotion:
        if promotion < KNIGHT or promotion > QUEEN:
            raise ValueError("Invalid encoded promotion")
        result += "  nbrq"[promotion]
    return result


def uci_to_move(board: BoardArray, state: StateArray, uci: str) -> int:
    """Resolve legal UCI; reject malformed/illegal input instead of guessing flags."""
    if len(uci) not in (4, 5):
        raise ValueError("Malformed UCI")
    moves = np.empty(MAX_MOVES, dtype=np.int32)
    count = generate_legal(board, state, moves, np.empty(UNDO_WIDTH, dtype=np.int64))
    for index in range(count):
        move = int(moves[index])
        if move_to_uci(move) == uci:
            return move
    raise ValueError("UCI is not legal in this position")


# Original search and public API.


SM_MATE = 100_000
SM_INF = 1_000_000
SM_NONE = 1_000_001
SM_MAX_PLY = 64
SM_TT_SIZE = 1 << 18
SM_HISTORY_LIMIT = 8191
SM_HINT_SIZE = 1 << 16
SM_VALUES = np.array([0, 100, 320, 330, 500, 900, 0], dtype=np.int64)
SMKeyArray = NDArray[np.uint64]
SMWorkspace = tuple[
    MoveArray,
    StateArray,
    StateArray,
    SMKeyArray,
    StateArray,
    SMKeyArray,
    StateArray,
]


# The first 66 entries remain search ply slots; never shift mate-distance ply.
SM_HISTORY_COUNT = 66
SM_HISTORY_DIGEST = 67
SM_HISTORY_KEYS = 68
SM_HISTORY_SLOTS = 256
SM_HISTORY_COUNTS = SM_HISTORY_KEYS + SM_HISTORY_SLOTS
SM_HISTORY_WIDTH = SM_HISTORY_COUNTS + SM_HISTORY_SLOTS


def _history_mix(value: int) -> int:
    mask = (1 << 64) - 1
    value &= mask
    value ^= value >> 30
    value = (value * 0xBF58476D1CE4E5B9) & mask
    value ^= value >> 27
    value = (value * 0x94D049BB133111EB) & mask
    return value ^ (value >> 31)


def _history_key(board: chess.Board) -> int:
    """Pure Python counterpart of _sm_hash; legal EP, turn and castling matter."""
    result = _history_mix(0xA4093822299F31D0 + (2 if board.turn else 0))
    for square, piece in board.piece_map().items():
        numeric = 16 * chess.square_rank(square) + chess.square_file(square)
        value = piece.piece_type if piece.color else -piece.piece_type
        result ^= _history_mix(1 + numeric * 13 + value + 6)
    rights = 0
    for color, king_side, bit in ((True, True, 1), (True, False, 2),
                                  (False, True, 4), (False, False, 8)):
        allowed = (board.has_kingside_castling_rights(color) if king_side
                   else board.has_queenside_castling_rights(color))
        if allowed:
            rights |= bit
    result ^= _history_mix(0x13198A2E03707344 + rights)
    if board.ep_square is not None and board.has_legal_en_passant():
        numeric = 16 * chess.square_rank(board.ep_square) + chess.square_file(board.ep_square)
        result ^= _history_mix(0x243F6A8885A308D3 + numeric)
    return result


class _VerifiedHistory:
    """Only one uniquely verified opponent reply joins consecutive own calls."""

    def __init__(self) -> None:
        self.positions: list[str] = []
        self.moves: list[str] = []
        self.keys: list[int] = []
        self.pending: str | None = None
        self.reason = "explicit_reset"

    def reset_at(self, board: chess.Board, reason: str) -> None:
        self.positions = [board.fen()]
        self.moves = []
        self.keys = [_history_key(board)]
        self.pending = None
        self.reason = reason

    def observe(self, board: chess.Board, deadline: float) -> None:
        current = board.fen()
        if not self.positions:
            self.reset_at(board, "first_observation")
            return
        if current == self.positions[-1]:
            # A duplicate request does not make the position occur again.
            self.reason = "duplicate_request"
            return
        prior = chess.Board(self.positions[-1])
        if (prior.turn != board.turn
                or board.fullmove_number != prior.fullmove_number + 1
                or self.pending is None):
            self.reset_at(board, "unverified_transition")
            return
        own = chess.Move.from_uci(self.pending)
        if own not in prior.legal_moves:
            self.reset_at(board, "unverified_own_move")
            return
        prior.push(own)
        after_own = prior.fen()
        after_own_key = _history_key(prior)
        matching: list[str] = []
        for reply in prior.legal_moves:
            if time.perf_counter() >= deadline:
                self.reset_at(board, "recovery_deadline")
                return
            prior.push(reply)
            matches = prior.fen() == current
            prior.pop()
            if matches:
                matching.append(reply.uci())
        if len(matching) != 1:
            self.reset_at(board, "ambiguous_or_missing_reply")
            return
        if time.perf_counter() >= deadline:
            self.reset_at(board, "recovery_deadline")
            return
        self.moves.extend((self.pending, matching[0]))
        self.positions.extend((after_own, current))
        self.keys.extend((after_own_key, _history_key(board)))
        self.pending = None
        self.reason = "unique_legal_reply"

    def snapshot(self) -> dict[str, Any]:
        return {
            "reason": self.reason,
            "initial_fen": self.positions[0] if self.positions else None,
            "history_uci": self.moves.copy(),
            "positions_fen": self.positions.copy(),
            "pending_own_move": self.pending,
            "known_positions": len(self.positions),
            "current_occurrences": self.keys.count(self.keys[-1]) if self.keys else 0,
            "prefix_before_first_observation": "unknown",
        }


_GAME_HISTORY = _VerifiedHistory()
_LAST_HISTORY: dict[str, Any] = {}


def reset_game_history() -> None:
    """Required explicit game boundary for any local worker reused across games."""
    global _GAME_HISTORY, _LAST_HISTORY
    _GAME_HISTORY = _VerifiedHistory()
    _LAST_HISTORY = {"reason": "explicit_reset", "known_positions": 0}
    _SM_WORK[3][SM_HISTORY_COUNT:].fill(0)


def history_snapshot() -> dict[str, Any]:
    """A copy of the full legally verified suffix, including both sides' moves."""
    return _GAME_HISTORY.snapshot()


def _history_return(move: str) -> str:
    global _LAST_HISTORY
    # Pending only: commit it after a later request uniquely verifies the reply.
    _GAME_HISTORY.pending = move
    _LAST_HISTORY = {
        "reason": _GAME_HISTORY.reason,
        "known_positions": len(_GAME_HISTORY.keys),
        "current_occurrences": (_GAME_HISTORY.keys.count(_GAME_HISTORY.keys[-1])
                                if _GAME_HISTORY.keys else 0),
        "pending_own_move": move,
    }
    return move


def _history_prepare(path: SMKeyArray, board: chess.Board) -> None:
    path[SM_HISTORY_COUNT:].fill(0)
    # Earlier positions before the last pawn move/capture cannot repeat. The
    # complete available suffix remains in _GAME_HISTORY for audit, not the TT.
    count = min(board.halfmove_clock, len(_GAME_HISTORY.keys) - 1, 99)
    if count <= 0:
        return
    prefix = _GAME_HISTORY.keys[-count - 1:-1]
    digest = _history_mix(0x082EFA98EC4E6C89)
    for index, key in enumerate(prefix):
        digest = _history_mix(digest ^ key ^ (index + 1))
        slot = key & (SM_HISTORY_SLOTS - 1)
        while int(path[SM_HISTORY_COUNTS + slot]) != 0:
            if int(path[SM_HISTORY_KEYS + slot]) == key:
                break
            slot = (slot + 1) & (SM_HISTORY_SLOTS - 1)
        path[SM_HISTORY_KEYS + slot] = np.uint64(key)
        path[SM_HISTORY_COUNTS + slot] = np.uint64(
            min(2, int(path[SM_HISTORY_COUNTS + slot]) + 1)
        )
    path[SM_HISTORY_COUNT] = np.uint64(count)
    path[SM_HISTORY_DIGEST] = np.uint64(digest)


@njit(cache=False)
def _sm_prior_occurrences(path: SMKeyArray, key: np.uint64) -> int:
    if path[SM_HISTORY_COUNT] == 0:
        return 0
    slot = np.int64(key & np.uint64(SM_HISTORY_SLOTS - 1))
    for _ in range(SM_HISTORY_SLOTS):
        count = int(path[SM_HISTORY_COUNTS + slot])
        if count == 0:
            return 0
        if path[SM_HISTORY_KEYS + slot] == key:
            return count
        slot = (slot + 1) & (SM_HISTORY_SLOTS - 1)
    return 0


@njit(cache=False)
def _sm_mix(value: np.uint64) -> np.uint64:
    value = np.uint64(value)
    value ^= value >> np.uint64(30)
    value *= np.uint64(0xBF58476D1CE4E5B9)
    value ^= value >> np.uint64(27)
    value *= np.uint64(0x94D049BB133111EB)
    return value ^ (value >> np.uint64(31))


@njit(cache=False)
def _sm_hash(board: BoardArray, state: StateArray, probe: StateArray) -> np.uint64:
    # Canonical repetition identity includes an EP target only if capture is legal.
    result = _sm_mix(np.uint64(0xA4093822299F31D0) + np.uint64(state[0] + 1))
    for rank in range(8):
        for file in range(8):
            square = rank * 16 + file
            piece = int(board[square])
            if piece:
                result ^= _sm_mix(np.uint64(1 + square * 13 + piece + 6))
    result ^= _sm_mix(np.uint64(0x13198A2E03707344) + np.uint64(state[1]))
    if state[2] >= 0 and has_legal_ep(board, state, probe):
        result ^= _sm_mix(np.uint64(0x243F6A8885A308D3) + np.uint64(state[2]))
    return result


@njit(cache=False)
def _sm_context(path: SMKeyArray, ply: int, halfmove: int) -> np.uint64:
    # Conservative entire known path, not just current FEN. Equal boards reached
    # through different reversible histories cannot share an ordinary TT score.
    value = _sm_mix(np.uint64(0x452821E638D01377) + np.uint64(halfmove))
    if path[SM_HISTORY_COUNT] != 0:
        value = _sm_mix(value ^ path[SM_HISTORY_DIGEST] ^ path[SM_HISTORY_COUNT])
    for index in range(ply + 1):
        value = _sm_mix(value ^ path[index] ^ np.uint64(index + 1))
    return value


@njit(cache=False)
def _sm_evaluate(board: BoardArray, state: StateArray) -> int:
    non_pawn = 0
    white_bishops = 0
    black_bishops = 0
    for rank in range(8):
        for file in range(8):
            piece = int(board[rank * 16 + file])
            kind = abs(piece)
            if 2 <= kind <= 5:
                non_pawn += SM_VALUES[kind]
            if piece == 3:
                white_bishops += 1
            elif piece == -3:
                black_bishops += 1
    endgame = non_pawn <= 2600
    white_score = (15 if white_bishops >= 2 else 0) - (15 if black_bishops >= 2 else 0)
    for rank in range(8):
        for file in range(8):
            piece = int(board[rank * 16 + file])
            if not piece:
                continue
            kind = abs(piece)
            advance = rank if piece > 0 else 7 - rank
            center = min(file, 7 - file) + min(rank, 7 - rank)
            score = SM_VALUES[kind]
            if kind == 1:
                score += 5 * advance + 2 * min(file, 7 - file)
            elif kind == 2:
                score += 8 * center
            elif kind == 3:
                score += 5 * center
            elif kind == 4:
                score += 2 * advance
            elif kind == 5:
                score += 2 * center
            elif endgame:
                score += 6 * center
            else:
                score -= 8 * advance
                if advance == 0 and (file == 2 or file == 6):
                    score += 15
            white_score += score if piece > 0 else -score
    return int(white_score * state[0])


@njit(cache=False)
def _sm_order(board: BoardArray, moves: MoveArray, count: int, preferred: int) -> None:
    # Same preferred/promotions/MVV-LVA/UCI policy as released v2.
    keys = np.empty(512, dtype=np.int64)
    for index in range(count):
        move = int(moves[index])
        source = move & 127
        target = (move >> 7) & 127
        promotion = (move >> 14) & 7
        flags = move >> 17
        priority = 100000 if move == preferred else 0
        if promotion:
            priority += 20000 + SM_VALUES[promotion]
        victim = 1 if flags & 1 else abs(int(board[target]))
        if victim:
            priority += 10000 + 10 * SM_VALUES[victim] - SM_VALUES[abs(int(board[source]))]
        from_key = (source & 7) * 8 + (source >> 4)
        to_key = (target & 7) * 8 + (target >> 4)
        promo_key = 0
        if promotion == 2:
            promo_key = 1
        elif promotion == 5:
            promo_key = 2
        elif promotion == 4:
            promo_key = 3
        keys[index] = -priority * 65536 + from_key * 320 + to_key * 5 + promo_key
    for index in range(1, count):
        move = moves[index]
        key = keys[index]
        slot = index
        while slot > 0 and keys[slot - 1] > key:
            keys[slot] = keys[slot - 1]
            moves[slot] = moves[slot - 1]
            slot -= 1
        keys[slot] = key
        moves[slot] = move



@njit(cache=False)
def _sm_order_ordinary(
    board: BoardArray, moves: MoveArray, count: int, preferred: int,
    side: int, ply: int, killers: MoveArray, history: MoveArray,
) -> None:
    # Original v14 tactical priorities and UCI ties; quiet cutoffs supply hints.
    keys = np.empty(512, dtype=np.int64)
    for index in range(count):
        move = int(moves[index])
        source = move & 127
        target = (move >> 7) & 127
        promotion = (move >> 14) & 7
        flags = move >> 17
        priority = 100000 if move == preferred else 0
        if promotion:
            priority += 20000 + SM_VALUES[promotion]
        victim = 1 if flags & 1 else abs(int(board[target]))
        if victim:
            priority += 10000 + 10 * SM_VALUES[victim] - SM_VALUES[abs(int(board[source]))]
        elif not promotion:
            if move == killers[ply, 0]:
                priority += 9000
            elif move == killers[ply, 1]:
                priority += 8500
            else:
                priority += int(history[0 if side == 1 else 1, source, target])
        from_key = (source & 7) * 8 + (source >> 4)
        to_key = (target & 7) * 8 + (target >> 4)
        promo_key = 0
        if promotion == 2:
            promo_key = 1
        elif promotion == 5:
            promo_key = 2
        elif promotion == 4:
            promo_key = 3
        keys[index] = -priority * 65536 + from_key * 320 + to_key * 5 + promo_key
    for index in range(1, count):
        move = moves[index]
        key = keys[index]
        slot = index
        while slot > 0 and keys[slot - 1] > key:
            keys[slot] = keys[slot - 1]
            moves[slot] = moves[slot - 1]
            slot -= 1
        keys[slot] = key
        moves[slot] = move



@njit(cache=False)
def _sm_record_quiet_cutoff(
    board: BoardArray, side: int, move: int, ply: int, depth: int,
    killers: MoveArray, history: MoveArray,
) -> None:
    # Called only after a completed ordinary beta cutoff and parent restoration.
    source = move & 127
    target = (move >> 7) & 127
    promotion = (move >> 14) & 7
    if promotion or board[target] != 0 or ((move >> 17) & FLAG_EP):
        return
    if move != killers[ply, 0]:
        killers[ply, 1] = killers[ply, 0]
        killers[ply, 0] = move
    color = 0 if side == 1 else 1
    history[color, source, target] = min(
        SM_HISTORY_LIMIT, int(history[color, source, target]) + depth * depth
    )


@njit(cache=False)
def _sm_hint_probe(
    position: np.uint64, moves: MoveArray, count: int,
    hint_keys: SMKeyArray, hint_moves: MoveArray, hint_stats: StateArray,
) -> int:
    hint_stats[0] += 1
    slot = int(position & np.uint64(SM_HINT_SIZE - 1))
    if hint_keys[slot] != position:
        return -1
    hint_stats[1] += 1
    preferred = int(hint_moves[slot])
    for index in range(count):
        if int(moves[index]) == preferred:
            hint_stats[2] += 1
            return preferred
    return -1


@njit(cache=False)
def _sm_hint_store(
    position: np.uint64, move: int,
    hint_keys: SMKeyArray, hint_moves: MoveArray, hint_stats: StateArray,
) -> None:
    # Ordering-only data: no depth, score or draw-context conclusion is stored.
    if move < 0:
        return
    slot = int(position & np.uint64(SM_HINT_SIZE - 1))
    hint_keys[slot] = position
    hint_moves[slot] = move
    hint_stats[3] += 1


@njit(cache=False)
def _sm_visit(control: StateArray, deadline: float, quiet: bool) -> bool:
    control[2 if quiet else 1] += 1
    nodes = control[1] + control[2]
    if nodes == 1 or nodes % 64 == 0:
        with objmode(observed="float64"):
            observed = time.perf_counter()
        if observed >= deadline:
            control[0] = 1
    return bool(control[0] != 0)


@njit(cache=False)
def _sm_terminal(
    board: BoardArray,
    state: StateArray,
    moves: MoveArray,
    count: int,
    ply: int,
    path: SMKeyArray,
    probes: StateArray,
) -> int:
    if count == 0:
        return -SM_MATE + ply if in_check(board, state) else 0
    if insufficient_material(board):
        return 0
    if state[3] >= 100:
        return 0
    if state[3] == 99:
        for index in range(count):
            make_move(board, state, moves[index], probes[0])
            drawn = state[3] >= 100 and has_legal_move(board, state, probes[1])
            unmake_move(board, state, probes[0])
            if drawn:
                return 0
    # Actual occurrences only. A legal move that could repeat is an option,
    # not an immediate draw of this parent position. Draw value remains zero.
    if path[SM_HISTORY_COUNT] != 0 or ply >= 8:
        repetitions = _sm_prior_occurrences(path, path[ply])
        for index in range(ply + 1):
            if path[index] == path[ply]:
                repetitions += 1
        if repetitions >= 3:
            return 0
    return SM_NONE


@njit(cache=False)
def _sm_to_tt(score: int, ply: int) -> int:
    if score >= SM_MATE - SM_MAX_PLY:
        return score + ply
    if score <= -SM_MATE + SM_MAX_PLY:
        return score - ply
    return score


@njit(cache=False)
def _sm_from_tt(score: int, ply: int) -> int:
    if score >= SM_MATE - SM_MAX_PLY:
        return score - ply
    if score <= -SM_MATE + SM_MAX_PLY:
        return score + ply
    return score


@njit(cache=False)
def _sm_quiet(
    board: BoardArray,
    state: StateArray,
    alpha: int,
    beta: int,
    ply: int,
    deadline: float,
    move_rows: MoveArray,
    undo_rows: StateArray,
    probes: StateArray,
    path: SMKeyArray,
    control: StateArray,
) -> int:
    if _sm_visit(control, deadline, True):
        return 0
    path[ply] = _sm_hash(board, state, probes[1])
    checked = in_check(board, state)
    # Full lists are needed for evasions and the existing prospective draw logic.
    all_moves = checked or state[3] == 99
    if not all_moves and ply >= 7:
        for left in range((ply + 1) % 2, ply, 2):
            for right in range(left + 2, ply, 2):
                if path[left] == path[right]:
                    all_moves = True
                    break
            if all_moves:
                break
    if all_moves:
        tactical_count = generate_legal(board, state, move_rows[ply], probes[0])
        count = tactical_count
    else:
        tactical_count = _nb_generate_tactical(
            board, state, move_rows[ply], probes[0], False
        )
        # No tactical move does not imply stalemate; one legal quiet move suffices.
        count = tactical_count
        if count == 0 and has_legal_move(board, state, probes[0]):
            count = 1
    terminal = _sm_terminal(board, state, move_rows[ply], count, ply, path, probes)
    if terminal != SM_NONE:
        return terminal
    if ply >= SM_MAX_PLY:
        control[0] = 1
        return 0
    best = -SM_INF
    if not checked:
        best = _sm_evaluate(board, state)
        if best >= beta:
            return best
        alpha = max(alpha, best)
    _sm_order(board, move_rows[ply], tactical_count, -1)
    for index in range(tactical_count):
        move = int(move_rows[ply, index])
        target = (move >> 7) & 127
        promotion = (move >> 14) & 7
        capture = board[target] != 0 or ((move >> 17) & 1) != 0
        if not checked and not capture and not promotion:
            continue
        make_move(board, state, move, undo_rows[ply])
        score = -_sm_quiet(
            board,
            state,
            -beta,
            -alpha,
            ply + 1,
            deadline,
            move_rows,
            undo_rows,
            probes,
            path,
            control,
        )
        unmake_move(board, state, undo_rows[ply])
        if control[0]:
            return 0
        best = max(best, score)
        alpha = max(alpha, score)
        if alpha >= beta:
            break
    return best


@njit(cache=False)
def _sm_search(
    board: BoardArray,
    state: StateArray,
    depth: int,
    alpha: int,
    beta: int,
    ply: int,
    deadline: float,
    move_rows: MoveArray,
    undo_rows: StateArray,
    probes: StateArray,
    path: SMKeyArray,
    control: StateArray,
    tt_keys: SMKeyArray,
    tt_data: StateArray,
    use_tt: bool,
    killers: MoveArray,
    history: MoveArray,
    hint_keys: SMKeyArray,
    hint_moves: MoveArray,
    hint_stats: StateArray,
) -> int:
    if depth <= 0:
        return _sm_quiet(
            board, state, alpha, beta, ply, deadline, move_rows, undo_rows, probes, path, control
        )
    if _sm_visit(control, deadline, False):
        return 0
    count = generate_legal(board, state, move_rows[ply], probes[0])
    position = _sm_hash(board, state, probes[1])
    path[ply] = position
    terminal = _sm_terminal(board, state, move_rows[ply], count, ply, path, probes)
    if terminal != SM_NONE:
        return terminal
    if ply >= SM_MAX_PLY:
        control[0] = 1
        return 0
    context = _sm_context(path, ply, int(state[3]))
    slot = int((position ^ context) & np.uint64(SM_TT_SIZE - 1))
    original_alpha = alpha
    if (
        use_tt
        and tt_data[slot, 0] >= depth
        and tt_keys[slot, 0] == position
        and tt_keys[slot, 1] == context
    ):
        score = _sm_from_tt(int(tt_data[slot, 1]), ply)
        bound = tt_data[slot, 2]
        if bound == 0 or (bound == 1 and score >= beta) or (bound == 2 and score <= alpha):
            control[3] += 1
            return score
    preferred = -1
    if use_tt:
        preferred = _sm_hint_probe(
            position, move_rows[ply], count, hint_keys, hint_moves, hint_stats
        )
    _sm_order_ordinary(
        board, move_rows[ply], count, preferred, int(state[0]), ply, killers, history
    )
    best = -SM_INF
    best_move = -1
    for index in range(count):
        move = move_rows[ply, index]
        make_move(board, state, move, undo_rows[ply])
        if index == 0:
            score = -_sm_search(
                board,
                state,
                depth - 1,
                -beta,
                -alpha,
                ply + 1,
                deadline,
                move_rows,
                undo_rows,
                probes,
                path,
                control,
                tt_keys,
                tt_data,
                use_tt,
                killers,
                history,
                hint_keys,
                hint_moves,
                hint_stats,
            )
        else:
            score = -_sm_search(
                board,
                state,
                depth - 1,
                -alpha - 1,
                -alpha,
                ply + 1,
                deadline,
                move_rows,
                undo_rows,
                probes,
                path,
                control,
                tt_keys,
                tt_data,
                use_tt,
                killers,
                history,
                hint_keys,
                hint_moves,
                hint_stats,
            )
            if not control[0] and alpha < score < beta:
                control[4] += 1
                score = -_sm_search(
                    board,
                    state,
                    depth - 1,
                    -beta,
                    -alpha,
                    ply + 1,
                    deadline,
                    move_rows,
                    undo_rows,
                    probes,
                    path,
                    control,
                    tt_keys,
                    tt_data,
                    use_tt,
                    killers,
                    history,
                    hint_keys,
                    hint_moves,
                    hint_stats,
                )
        unmake_move(board, state, undo_rows[ply])
        if control[0]:
            return 0
        if score > best:
            best = score
            best_move = int(move)
        alpha = max(alpha, score)
        if alpha >= beta:
            _sm_record_quiet_cutoff(
                board, int(state[0]), int(move), ply, depth, killers, history
            )
            break
    if use_tt:
        _sm_hint_store(position, best_move, hint_keys, hint_moves, hint_stats)
        tt_keys[slot, 0] = position
        tt_keys[slot, 1] = context
        tt_data[slot, 0] = depth
        tt_data[slot, 1] = _sm_to_tt(best, ply)
        tt_data[slot, 2] = 2 if best <= original_alpha else 1 if best >= beta else 0
    return best


@njit(cache=False)
def _sm_root(
    board: BoardArray,
    state: StateArray,
    depth: int,
    deadline: float,
    preferred: int,
    move_rows: MoveArray,
    undo_rows: StateArray,
    probes: StateArray,
    path: SMKeyArray,
    control: StateArray,
    tt_keys: SMKeyArray,
    tt_data: StateArray,
    use_tt: bool,
    killers: MoveArray,
    history: MoveArray,
    hint_keys: SMKeyArray,
    hint_moves: MoveArray,
    hint_stats: StateArray,
) -> tuple[int, int]:
    count = generate_legal(board, state, move_rows[0], probes[0])
    path[0] = _sm_hash(board, state, probes[1])
    _sm_order(board, move_rows[0], count, preferred)
    best_move = move_rows[0, 0]
    best_score = -SM_INF
    alpha = -SM_INF
    for index in range(count):
        move = move_rows[0, index]
        make_move(board, state, move, undo_rows[0])
        score = -_sm_search(
            board,
            state,
            depth - 1,
            -SM_INF,
            -alpha,
            1,
            deadline,
            move_rows,
            undo_rows,
            probes,
            path,
            control,
            tt_keys,
            tt_data,
            use_tt,
            killers,
            history,
            hint_keys,
            hint_moves,
            hint_stats,
        )
        unmake_move(board, state, undo_rows[0])
        if control[0]:
            return int(best_move), int(best_score)
        if score > best_score:
            best_move = move
            best_score = score
        alpha = max(alpha, score)
    return int(best_move), int(best_score)


def _sm_workspace() -> SMWorkspace:
    return (
        np.zeros((66, 512), dtype=np.int32),
        np.zeros((66, 16), dtype=np.int64),
        np.zeros((3, 16), dtype=np.int64),
        np.zeros(SM_HISTORY_WIDTH, dtype=np.uint64),
        np.zeros(5, dtype=np.int64),
        np.zeros((SM_TT_SIZE, 2), dtype=np.uint64),
        np.full((SM_TT_SIZE, 3), -1, dtype=np.int64),
    )


_SM_WORK = _sm_workspace()
# Ordinary move-order hints are independent from the unchanged score workspace.
_SM_KILLERS = np.full((66, 2), -1, dtype=np.int32)
_SM_HISTORY = np.zeros((2, 128, 128), dtype=np.int32)
# This per-game cache carries only legal move-order hints, never scores.
_SM_HINT_KEYS = np.zeros(SM_HINT_SIZE, dtype=np.uint64)
_SM_HINT_MOVES = np.full(SM_HINT_SIZE, -1, dtype=np.int32)
_SM_HINT_STATS = np.zeros(4, dtype=np.int64)
_LAST_SEARCH: dict[str, Any] = {}


def reset_game_hints() -> None:
    """Clear only move-hint state at a new game or an independent diagnostic."""
    _SM_HINT_KEYS.fill(0)
    _SM_HINT_MOVES.fill(-1)
    _SM_HINT_STATS.fill(0)


def _sm_reset_ordering() -> None:
    """Forget search-only hints before each independently searched request."""
    _SM_KILLERS.fill(-1)
    _SM_HISTORY.fill(0)


def fixed_depth(fen: str, depth: int, budget_s: float = 5.0, use_tt: bool = True) -> dict[str, Any]:
    """Research diagnostics; public competition entry remains get_move."""
    board, state = from_fen(fen)
    before_board, before_state = board.copy(), state.copy()
    work = _SM_WORK
    work[3][SM_HISTORY_COUNT:].fill(0)
    work[4].fill(0)
    work[6].fill(-1)
    _sm_reset_ordering()
    reset_game_hints()
    preferred = uci_to_move(
        board, state, min(chess.Board(fen).legal_moves, key=chess.Move.uci).uci()
    )
    started = time.perf_counter()
    move, score = _sm_root(
        board, state, depth, started + budget_s, preferred, *work, use_tt,
        _SM_KILLERS, _SM_HISTORY, _SM_HINT_KEYS, _SM_HINT_MOVES, _SM_HINT_STATS,
    )
    restored = bool(np.array_equal(board, before_board) and np.array_equal(state, before_state))
    return {
        "move": move_to_uci(move),
        "score": int(score),
        "depth": depth,
        "aborted": bool(work[4][0]),
        "nodes": int(work[4][1] + work[4][2]),
        "ordinary_nodes": int(work[4][1]),
        "quiescence_nodes": int(work[4][2]),
        "tt_hits": int(work[4][3]),
        "researches": int(work[4][4]),
        "hint_probes": int(_SM_HINT_STATS[0]),
        "hint_key_matches": int(_SM_HINT_STATS[1]),
        "hint_legal_hits": int(_SM_HINT_STATS[2]),
        "hint_stores": int(_SM_HINT_STATS[3]),
        "elapsed_s": time.perf_counter() - started,
        "restored": restored,
    }


_KQK_ASSETS = (
    ("KQvK.rtbw", "517667dff787162dbb1ed9d5d6484d30ee854e686ee0675c08d99ecf045d2d50"),
    ("KQvK.rtbz", "71ea9444fa5bd42897d781a0c356975ea6f23e0f65a4254e470897031c161c8c"),
)
_KQK_TABLEBASE: chess.syzygy.Tablebase | None = None
_KQK_STATUS: dict[str, Any] = {"status": "not_initialized"}
_LAST_KQK: dict[str, Any] = {}


def _kqk_supported(board: chess.Board) -> bool:
    """Exactly one queen and two kings, with no unsupported state rights."""
    return (
        board.occupied.bit_count() == 3
        and board.kings.bit_count() == 2
        and board.queens.bit_count() == 1
        and board.occupied == (board.kings | board.queens)
        and not board.castling_rights
        and board.ep_square is None
        and not board.chess960
        and board.is_valid()
    )


def _kqk_validate_values(wdl: int, dtz: int) -> None:
    """Reject values outside the supported ordinary KQK outcome/distance range."""
    if (
        type(wdl) is not int
        or type(dtz) is not int
        or wdl not in (-2, 0, 2)
        or abs(dtz) > 100
        or (wdl == 0) != (dtz == 0)
        or wdl * dtz < 0
    ):
        raise ValueError("Unexpected KQK WDL/DTZ type, range or sign")


def _kqk_load(directory: Path) -> tuple[chess.syzygy.Tablebase, dict[str, Any]]:
    """Load only hash-pinned assets; on failure close the partial local resource.

    This helper has no global side effects so diagnostics can check invalid data
    directories without replacing the active resource or importing another player.
    """
    started = time.perf_counter()
    identities: dict[str, str] = {}
    for name, expected in _KQK_ASSETS:
        actual = hashlib.sha256((directory / name).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"KQK asset hash mismatch: {name}")
        identities[name] = actual
    table = chess.syzygy.Tablebase(max_fds=2)
    try:
        for name, _ in _KQK_ASSETS:
            if table.add_file(str(directory / name)) != 1:
                raise ValueError(f"KQK table was not registered: {name}")
        # Both turns and colour mirrors warm the lazily opened WDL and DTZ data.
        base = chess.Board("8/8/3k4/7q/8/6K1/8/8 w - - 0 1")
        probes = 0
        for mirrored in (False, True):
            for turn in (chess.WHITE, chess.BLACK):
                board = base.mirror() if mirrored else base.copy(stack=False)
                board.turn = turn
                if not _kqk_supported(board):
                    raise ValueError("Invalid KQK import fixture")
                before = board.fen(en_passant="fen")
                wdl = table.probe_wdl(board)
                dtz = table.probe_dtz(board)
                _kqk_validate_values(wdl, dtz)
                probes += 2
                strong = (
                    chess.WHITE if board.queens & board.occupied_co[chess.WHITE] else chess.BLACK
                )
                if wdl != (2 if turn == strong else -2) or not 1 <= abs(dtz) <= 100:
                    raise ValueError("KQK import probe outcome inconsistent")
                if (dtz > 0) != (wdl > 0) or board.fen(en_passant="fen") != before:
                    raise ValueError("KQK import probe sign/restoration inconsistent")
        return table, {
            "status": "ready", "asset_sha256": identities, "warm_probe_calls": probes,
            "warm_positions": 4, "elapsed_s": time.perf_counter() - started, "error": None,
        }
    except Exception:
        table.close()
        raise


def _kqk_initialize() -> None:
    """Tablebase initialization is charged to import, with a safe v7 fallback."""
    global _KQK_TABLEBASE, _KQK_STATUS
    try:
        _KQK_TABLEBASE, _KQK_STATUS = _kqk_load(Path(__file__).resolve().parent / "tables")
    except Exception as error:
        _KQK_TABLEBASE = None
        _KQK_STATUS = {
            "status": "disabled", "error": f"{type(error).__name__}: {error}",
            "warm_probe_calls": 0, "asset_sha256": {},
        }


def _kqk_select(reference: chess.Board, legal: list[chess.Move], deadline: float) -> str | None:
    """Select from all legal KQK children, or return None for the unchanged core.

    WDL and DTZ are side-to-move values: negate each child, then include this
    nonzeroing move. Positive distance is minimized to convert; negative distance
    is minimized to delay a forced loss. WDL alone would permit non-progress.
    DTZ can round by one ply, so the covered nonterminal line must leave a
    conservative two-ply margin before the fifty-move boundary.
    """
    global _LAST_KQK
    started = time.perf_counter()
    _LAST_KQK = {
        "status": "skipped", "reason": "unsupported_material", "eligible": False,
        "attempted": False, "complete": False, "used": False, "probed_count": 0,
        "legal_count": len(legal), "board_restored": True, "elapsed_s": 0.0,
        "children": [],
    }
    if not _kqk_supported(reference):
        return None
    _LAST_KQK["eligible"] = True
    table = _KQK_TABLEBASE
    if table is None:
        _LAST_KQK["reason"] = "tablebase_disabled"
        return None
    if not legal or reference.outcome(claim_draw=False) is not None:
        _LAST_KQK["reason"] = "root_terminal"
        return None
    before_fen = reference.fen(en_passant="fen")
    before_stack = tuple(reference.move_stack)
    selected: str | None = None
    children: list[dict[str, Any]] = []
    _LAST_KQK.update(status="probing", reason=None, attempted=True, children=children)
    try:
        if time.perf_counter() >= deadline:
            raise TimeoutError("KQK deadline before root probe")
        root_wdl = table.probe_wdl(reference)
        root_dtz = table.probe_dtz(reference)
        _kqk_validate_values(root_wdl, root_dtz)
        _LAST_KQK.update(root_wdl=root_wdl, root_dtz=root_dtz)
        for move in legal:
            if time.perf_counter() >= deadline:
                raise TimeoutError("KQK deadline before child")
            reference.push(move)
            try:
                terminal: str | None = None
                child_wdl: int | None = None
                child_dtz: int | None = None
                if reference.is_checkmate():
                    outcome, distance, terminal = 2, 1, "checkmate"
                elif reference.is_stalemate() or reference.is_insufficient_material():
                    outcome, distance, terminal = 0, 0, "draw"
                else:
                    if not _kqk_supported(reference):
                        raise ValueError("Unexpected material after KQK move")
                    child_wdl = table.probe_wdl(reference)
                    child_dtz = table.probe_dtz(reference)
                    _kqk_validate_values(child_wdl, child_dtz)
                    outcome = -child_wdl
                    distance = -child_dtz
                    if distance:
                        distance += 1 if distance > 0 else -1
            finally:
                reference.pop()
            children.append({
                "move": move.uci(), "wdl": outcome, "dtz": distance,
                "child_wdl": child_wdl, "child_dtz": child_dtz, "terminal": terminal,
            })
            _LAST_KQK["probed_count"] = len(children)
            if time.perf_counter() >= deadline:
                raise TimeoutError("KQK deadline after child")
        if not children:
            raise ValueError("KQK complete legal set is empty")
        best = min(children, key=lambda row: (-int(row["wdl"]), int(row["dtz"]), str(row["move"])))
        if best["wdl"] != root_wdl:
            raise ValueError("KQK root/child outcome disagreement")
        _LAST_KQK.update(
            complete=True, selected_wdl=best["wdl"], selected_dtz=best["dtz"],
            move=best["move"], terminal=best["terminal"],
        )
        if best["terminal"] is None and reference.halfmove_clock + abs(int(best["dtz"])) + 2 >= 100:
            _LAST_KQK.update(status="fallback", reason="fifty_move_margin")
        elif time.perf_counter() >= deadline:
            raise TimeoutError("KQK deadline before selection")
        else:
            selected = str(best["move"])
            _LAST_KQK.update(status="selected", reason=None, used=True)
    except TimeoutError as error:
        _LAST_KQK.update(status="fallback", reason="deadline", error=str(error), used=False)
    except Exception as error:
        _LAST_KQK.update(
            status="fallback", reason="probe_error", error=f"{type(error).__name__}: {error}",
            used=False,
        )
    finally:
        restored = (
            reference.fen(en_passant="fen") == before_fen
            and tuple(reference.move_stack) == before_stack
        )
        _LAST_KQK.update(board_restored=restored, elapsed_s=time.perf_counter() - started)
        if not restored:
            selected = None
            _LAST_KQK.update(status="fallback", reason="restoration_failure", used=False)
    return selected


def get_move(fen: str, time_left_ms: int) -> str:
    """Combined original search with completed-iteration clock policy 02."""
    global _LAST_SEARCH, _LAST_KQK
    _LAST_SEARCH = {}
    _LAST_KQK = {"status": "skipped", "reason": "not_attempted", "used": False}
    started = time.perf_counter()
    reference = chess.Board(fen)
    # This bounded recovery is part of the existing wall-clock allocation.
    recovery_deadline = started + min(0.005, max(0, time_left_ms) * 0.00002)
    _GAME_HISTORY.observe(reference, recovery_deadline)
    legal = sorted(reference.legal_moves, key=chess.Move.uci)
    if not legal:
        raise ValueError("get_move requires a position with a legal move")
    fallback = legal[0].uci()
    if time_left_ms <= 50 or len(legal) == 1:
        _LAST_KQK["reason"] = "low_clock" if time_left_ms <= 50 else "forced_move"
        return _history_return(fallback)
    reserve_ms = max(25.0, min(200.0, 0.02 * time_left_ms))
    available_ms = max(0.0, time_left_ms - reserve_ms)
    normal_ms = min(4000.0, available_ms / 30.0)
    hard_ms = min(8000.0, available_ms / 10.0)
    deadline = started + hard_ms / 1000.0
    # Retain the qualified KQK specialization's original allowance exactly.
    kqk_ms = min(1500.0, time_left_ms / 40.0, time_left_ms - reserve_ms)
    specialized = _kqk_select(reference, legal, started + kqk_ms / 1000.0)
    if specialized is not None:
        return _history_return(specialized)
    if _LAST_KQK.get("reason") == "restoration_failure":
        return _history_return(fallback)
    if reference.is_insufficient_material() or reference.can_claim_fifty_moves():
        return _history_return(fallback)
    board, state = from_fen(fen)
    best = uci_to_move(board, state, fallback)
    work = _SM_WORK
    _history_prepare(work[3], reference)
    work[4].fill(0)
    work[6].fill(-1)
    _sm_reset_ordering()
    _SM_HINT_STATS.fill(0)
    completed_depth = 0
    completed_score = 0
    root_checked = reference.is_check()
    soft_ms = min(hard_ms, normal_ms * (1.75 if root_checked else 1.0))
    signal = "root_check" if root_checked else "normal"
    iterations: list[dict[str, Any]] = []
    leaders: list[int] = []
    scores: list[int] = []
    durations: list[float] = []
    predicted_next_ms = 0.0
    stop_reason = "depth_cap"
    for depth in range(1, 65):
        iteration_started = time.perf_counter()
        elapsed_ms = (iteration_started - started) * 1000.0
        if iteration_started >= deadline:
            stop_reason = "hard_deadline_before_iteration"
            break
        if elapsed_ms >= soft_ms:
            stop_reason = "soft_target"
            break
        if durations and elapsed_ms + predicted_next_ms > hard_ms:
            stop_reason = "predicted_iteration_exceeds_remaining_hard_budget"
            break
        previous_nodes = int(work[4][1] + work[4][2])
        move, score = _sm_root(
            board, state, depth, deadline, best, *work, True,
            _SM_KILLERS, _SM_HISTORY, _SM_HINT_KEYS, _SM_HINT_MOVES, _SM_HINT_STATS,
        )
        finished = time.perf_counter()
        iteration_ms = max(0.0, (finished - iteration_started) * 1000.0)
        iterations.append(
            {
                "depth": depth,
                "complete": not bool(work[4][0]),
                "move": move_to_uci(move) if not work[4][0] else None,
                "score": int(score) if not work[4][0] else None,
                "iteration_ms": iteration_ms,
                "elapsed_ms": (finished - started) * 1000.0,
                "nodes": int(work[4][1] + work[4][2]) - previous_nodes,
                "soft_target_ms_at_start": soft_ms,
                "predicted_next_ms_at_start": predicted_next_ms,
                "elapsed_ms_at_start": elapsed_ms,
                "deadline_reached_at_return": finished >= deadline,
                "signal_at_start": signal,
            }
        )
        if work[4][0]:
            stop_reason = "search_abort_deadline_or_ply_cap"
            break
        best, completed_depth, completed_score = move, depth, score
        leaders.append(int(move))
        scores.append(int(score))
        durations.append(iteration_ms)
        if abs(score) >= SM_MATE - 64:
            stop_reason = "reported_mate"
            break
        severe = len(scores) >= 2 and scores[-1] <= scores[-2] - 75
        recent_leaders = leaders[-3:]
        switched = any(
            recent_leaders[index] != recent_leaders[index - 1]
            for index in range(1, len(recent_leaders))
        )
        easy = (
            depth >= 5
            and len(leaders) >= 3
            and len(set(leaders[-3:])) == 1
            and max(scores[-3:]) - min(scores[-3:]) <= 20
        )
        if severe:
            signal, factor = "completed_score_drop", 2.5
        elif root_checked or switched:
            signal, factor = "root_check" if root_checked else "leader_switch", 1.75
        elif easy:
            signal, factor = "stable_three_iterations", 0.7
        else:
            signal, factor = "normal", 1.0
        soft_ms = min(hard_ms, normal_ms * factor)
        if len(durations) >= 2:
            growth = min(8.0, max(2.0, durations[-1] / max(1.0, durations[-2])))
            predicted_next_ms = 1.25 * durations[-1] * growth
        else:
            predicted_next_ms = 4.0 * durations[-1]
    _LAST_SEARCH = {
        "completed_depth": completed_depth,
        "score": int(completed_score),
        "ordinary_nodes": int(work[4][1]),
        "quiescence_nodes": int(work[4][2]),
        "tt_hits": int(work[4][3]),
        "hint_probes": int(_SM_HINT_STATS[0]),
        "hint_key_matches": int(_SM_HINT_STATS[1]),
        "hint_legal_hits": int(_SM_HINT_STATS[2]),
        "hint_stores": int(_SM_HINT_STATS[3]),
        "elapsed_s": time.perf_counter() - started,
        "clock_policy": "adaptive-combined-clock-02",
        "reserve_ms": reserve_ms,
        "normal_ms": normal_ms,
        "hard_ms": hard_ms,
        "kqk_budget_ms": kqk_ms,
        "final_soft_ms": soft_ms,
        "final_signal": signal,
        "predicted_next_ms": predicted_next_ms,
        "stop_reason": stop_reason,
        "iterations": iterations,
    }
    return _history_return(move_to_uci(best))


def _sm_warm() -> None:
    # No on-disk JIT cache: each game pays compilation inside its import budget.
    fixed_depth(chess.STARTING_FEN, 2, 80.0, True)


_sm_warm()
# Import warmup is not an observed position from the new game.
reset_game_hints()

# Eager table probes also belong to the platform import allowance.
_kqk_initialize()
