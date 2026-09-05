"""Frozen, hand-authored opening positions for the v0 development campaign.

These common-opening SAN sequences were written for this project. No engine
moves, evaluations, or published opening database were used. They are local
test inputs, never part of the submitted player. All 32 belong to the evolution
set: none is a final holdout or a sample of the platform's private openings.
"""

from dataclasses import dataclass

import chess


@dataclass(frozen=True)
class Opening:
    identifier: str
    name: str
    san: str
    fen: str


_LINES = (
    ("Ruy Lopez", "e4 e5 Nf3 Nc6 Bb5 a6 Ba4 Nf6"),
    ("Italian", "e4 e5 Nf3 Nc6 Bc4 Bc5 c3 Nf6"),
    ("Scotch", "e4 e5 Nf3 Nc6 d4 exd4 Nxd4 Nf6"),
    ("Petroff", "e4 e5 Nf3 Nf6 Nxe5 d6 Nf3 Nxe4"),
    ("Vienna", "e4 e5 Nc3 Nf6 f4 d5 fxe5 Nxe4"),
    ("King's Gambit", "e4 e5 f4 exf4 Nf3 g5 h4 g4"),
    ("Philidor", "e4 e5 Nf3 d6 d4 Nf6 Nc3 Nbd7"),
    ("Four Knights", "e4 e5 Nf3 Nc6 Nc3 Nf6 Bb5"),
    ("Open Sicilian", "e4 c5 Nf3 d6 d4 cxd4 Nxd4 Nf6 Nc3 a6"),
    ("Closed Sicilian", "e4 c5 Nc3 Nc6 g3 g6 Bg2 Bg7"),
    ("Alapin Sicilian", "e4 c5 c3 d5 exd5 Qxd5 d4 Nf6"),
    ("French Advance", "e4 e6 d4 d5 e5 c5 c3 Nc6"),
    ("French Tarrasch", "e4 e6 d4 d5 Nd2 c5 exd5 exd5"),
    ("Caro-Kann Advance", "e4 c6 d4 d5 e5 Bf5 Nf3 e6"),
    ("Caro-Kann Exchange", "e4 c6 d4 d5 exd5 cxd5 Bd3 Nc6"),
    ("Pirc", "e4 d6 d4 Nf6 Nc3 g6 f4 Bg7"),
    ("Alekhine", "e4 Nf6 e5 Nd5 d4 d6 Nf3 Bg4"),
    ("Scandinavian", "e4 d5 exd5 Qxd5 Nc3 Qa5 d4 c6"),
    ("Queen's Gambit Declined", "d4 d5 c4 e6 Nc3 Nf6 Bg5 Be7"),
    ("Queen's Gambit Accepted", "d4 d5 c4 dxc4 Nf3 Nf6 e3 e6"),
    ("Slav", "d4 d5 c4 c6 Nf3 Nf6 Nc3 dxc4"),
    ("Semi-Slav", "d4 d5 c4 c6 Nf3 Nf6 Nc3 e6"),
    ("Nimzo-Indian", "d4 Nf6 c4 e6 Nc3 Bb4 e3 O-O"),
    ("King's Indian", "d4 Nf6 c4 g6 Nc3 Bg7 e4 d6"),
    ("Gruenfeld", "d4 Nf6 c4 g6 Nc3 d5 cxd5 Nxd5"),
    ("Dutch", "d4 f5 g3 Nf6 Bg2 e6 Nf3 Be7"),
    ("London", "d4 d5 Nf3 Nf6 Bf4 e6 e3 c5"),
    ("Catalan", "d4 Nf6 c4 e6 g3 d5 Bg2 Be7"),
    ("English Symmetrical", "c4 c5 Nc3 Nc6 g3 g6 Bg2 Bg7"),
    ("English Reversed Sicilian", "c4 e5 Nc3 Nf6 g3 d5 cxd5 Nxd5"),
    ("Reti", "Nf3 d5 c4 e6 g3 Nf6 Bg2 Be7"),
    ("Queen's Indian", "d4 Nf6 c4 e6 Nf3 b6 g3 Bb7 Bg2"),
)


def openings() -> tuple[Opening, ...]:
    """Build and validate the frozen SAN lines without consulting any engine."""
    result = []
    seen: set[str] = set()
    for index, (name, san) in enumerate(_LINES, 1):
        board = chess.Board()
        for token in san.split():
            board.push_san(token)
        fen = board.fen()
        if not board.is_valid() or board.is_game_over(claim_draw=True) or fen in seen:
            raise ValueError(f"invalid, terminal, or duplicate opening: {name}")
        seen.add(fen)
        result.append(Opening(f"o{index:02d}", name, san, fen))
    if len(result) != 32:
        raise ValueError("v0 requires exactly 32 frozen openings")
    return tuple(result)
