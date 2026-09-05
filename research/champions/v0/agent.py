"""SearchMate v0: an original, deliberately small Python chess searcher.

The only runtime dependency is python-chess, for legal moves and board rules.
Evaluation terms below are simple arithmetic chosen for this project; no engine
code, piece-square tables, move database, or trained network is embedded.
"""

import time

import chess

_PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0,
}
_MATE_SCORE = 100_000
_INFINITY = 1_000_000
_MAX_DEPTH = 64


class _SearchTimeout(Exception):
    """Unwind an unfinished iteration without replacing the completed result."""


def _check_deadline(deadline: float) -> None:
    if time.perf_counter() >= deadline:
        raise _SearchTimeout


def _terminal_score(board: chess.Board, ply: int) -> int | None:
    """Score rule endings before evaluating a leaf, from the mover's viewpoint.

    The local referee ends games when a draw can be claimed. A FEN has no past
    positions, so repetition detection covers only history in this search. The
    shortest prospective third occurrence needs seven reversible plies; avoiding
    the claim test before that point saves substantial work at shallow leaves.
    """
    if board.is_checkmate():
        return -_MATE_SCORE + ply
    if board.is_stalemate() or board.is_insufficient_material():
        return 0
    if board.halfmove_clock >= 99 and board.can_claim_fifty_moves():
        return 0
    if len(board.move_stack) >= 7 and board.can_claim_threefold_repetition():
        return 0
    return None


def _evaluate(board: chess.Board) -> int:
    """Material plus modest development/centralization, in centipawn-like units."""
    non_pawn_material = sum(
        _PIECE_VALUES[piece_type] * len(board.pieces(piece_type, color))
        for color in chess.COLORS
        for piece_type in (chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN)
    )
    endgame = non_pawn_material <= 2_600
    white_score = 0
    for color in chess.COLORS:
        side_score = 0
        for piece_type in chess.PIECE_TYPES:
            squares = board.pieces(piece_type, color)
            side_score += _PIECE_VALUES[piece_type] * len(squares)
            if piece_type == chess.BISHOP and len(squares) >= 2:
                side_score += 15
            for square in squares:
                file = chess.square_file(square)
                rank = chess.square_rank(square)
                advance = rank if color == chess.WHITE else 7 - rank
                center = min(file, 7 - file) + min(rank, 7 - rank)
                if piece_type == chess.PAWN:
                    side_score += 5 * advance + 2 * min(file, 7 - file)
                elif piece_type == chess.KNIGHT:
                    side_score += 8 * center
                elif piece_type == chess.BISHOP:
                    side_score += 5 * center
                elif piece_type == chess.ROOK:
                    side_score += 2 * advance
                elif piece_type == chess.QUEEN:
                    side_score += 2 * center
                elif endgame:
                    side_score += 6 * center
                else:
                    side_score -= 8 * advance
                    if advance == 0 and file in (2, 6):
                        side_score += 15
        white_score += side_score if color == chess.WHITE else -side_score
    return white_score if board.turn == chess.WHITE else -white_score


def _ordered_moves(board: chess.Board, preferred: chess.Move | None = None) -> list[chess.Move]:
    """Previous root best, then promotions/captures, with a stable UCI tie break."""

    def order_key(move: chess.Move) -> tuple[int, str]:
        priority = 100_000 if move == preferred else 0
        if move.promotion is not None:
            priority += 20_000 + _PIECE_VALUES[move.promotion]
        if board.is_capture(move):
            victim = board.piece_type_at(move.to_square)
            if board.is_en_passant(move):
                victim = chess.PAWN
            attacker = board.piece_type_at(move.from_square)
            if victim is not None and attacker is not None:
                priority += 10_000 + 10 * _PIECE_VALUES[victim] - _PIECE_VALUES[attacker]
        return -priority, move.uci()

    return sorted(board.legal_moves, key=order_key)


def _negamax(
    board: chess.Board,
    depth: int,
    alpha: int,
    beta: int,
    ply: int,
    deadline: float,
) -> int:
    _check_deadline(deadline)
    terminal = _terminal_score(board, ply)
    if terminal is not None:
        return terminal
    if depth <= 0:
        return _evaluate(board)

    best_score = -_INFINITY
    for move in _ordered_moves(board):
        _check_deadline(deadline)
        board.push(move)
        try:
            score = -_negamax(board, depth - 1, -beta, -alpha, ply + 1, deadline)
        finally:
            board.pop()
        best_score = max(best_score, score)
        alpha = max(alpha, score)
        if alpha >= beta:
            break
    return best_score


def _search_root(
    board: chess.Board,
    depth: int,
    deadline: float,
    preferred: chess.Move | None = None,
) -> tuple[chess.Move, int]:
    """Finish one complete root iteration or raise; always restore the board."""
    _check_deadline(deadline)
    moves = _ordered_moves(board, preferred)
    if not moves:
        raise ValueError("Search requires a position with a legal move")
    best_move = moves[0]
    best_score = -_INFINITY
    alpha = -_INFINITY
    for move in moves:
        _check_deadline(deadline)
        board.push(move)
        try:
            score = -_negamax(board, depth - 1, -_INFINITY, -alpha, 1, deadline)
        finally:
            board.pop()
        if score > best_score:
            best_score = score
            best_move = move
        alpha = max(alpha, score)
    return best_move, best_score


def get_move(fen: str, time_left_ms: int) -> str:
    """Return legal UCI using iterative deepening within a conservative deadline.

    Every call reconstructs the board from FEN. No game history is inferred from
    earlier calls. Search time uses only the supplied remaining clock, so local
    games with a different increment do not require a different player build.
    """
    started = time.perf_counter()
    board = chess.Board(fen)
    legal_moves = sorted(board.legal_moves, key=chess.Move.uci)
    if not legal_moves:
        raise ValueError("get_move requires a position with a legal move")
    best_move = legal_moves[0]
    if time_left_ms <= 50 or len(legal_moves) == 1:
        return best_move.uci()

    reserve_ms = max(25.0, min(200.0, 0.02 * time_left_ms))
    budget_ms = min(1_500.0, time_left_ms / 40.0, time_left_ms - reserve_ms)
    deadline = started + budget_ms / 1_000.0
    next_depth_deadline = started + 0.8 * budget_ms / 1_000.0
    if _terminal_score(board, 0) is not None:
        return best_move.uci()

    for depth in range(1, _MAX_DEPTH + 1):
        if time.perf_counter() >= next_depth_deadline:
            break
        try:
            completed_move, score = _search_root(board, depth, deadline, best_move)
        except _SearchTimeout:
            break
        best_move = completed_move
        if abs(score) >= _MATE_SCORE - _MAX_DEPTH:
            break
    return best_move.uci()
