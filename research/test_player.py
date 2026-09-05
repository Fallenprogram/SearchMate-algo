"""Supplementary reliability checks for timeout unwinding and draw boundaries.

Run with ``python -m unittest research.test_player``. These tests use controlled
timeouts instead of relying on machine speed to interrupt a particular node.
"""

import time
import unittest
from unittest.mock import patch

import chess

import agent


class PlayerReliabilityTests(unittest.TestCase):
    def test_nested_timeout_restores_board_and_existing_history(self) -> None:
        board = chess.Board()
        for uci in ("e2e4", "e7e5", "g1f3"):
            board.push_uci(uci)
        original_fen = board.fen()
        original_stack = tuple(board.move_stack)
        largest_stack = len(original_stack)

        def fail_inside_search(deadline: float) -> None:
            nonlocal largest_stack
            largest_stack = max(largest_stack, len(board.move_stack))
            if len(board.move_stack) >= len(original_stack) + 3:
                raise agent._SearchTimeout

        with (
            patch.object(agent, "_check_deadline", new=fail_inside_search),
            self.assertRaises(agent._SearchTimeout),
        ):
            agent._search_root(board, 4, time.perf_counter() + 10)

        self.assertEqual(largest_stack, len(original_stack) + 3)
        self.assertEqual(board.fen(), original_fen)
        self.assertEqual(tuple(board.move_stack), original_stack)

    def test_timeout_retains_last_completed_iteration(self) -> None:
        completed_move = chess.Move.from_uci("e2e4")
        with (
            patch("agent.time.perf_counter", return_value=0.0),
            patch.object(
                agent,
                "_search_root",
                side_effect=[(completed_move, 10), agent._SearchTimeout],
            ) as search,
        ):
            result = agent.get_move(chess.STARTING_FEN, 10_000)

        self.assertEqual(result, completed_move.uci())
        self.assertEqual(search.call_count, 2)

    def test_timeout_before_completed_iteration_retains_legal_fallback(self) -> None:
        with (
            patch("agent.time.perf_counter", return_value=0.0),
            patch.object(agent, "_search_root", side_effect=agent._SearchTimeout) as search,
        ):
            result = agent.get_move(chess.STARTING_FEN, 10_000)

        self.assertIn(chess.Move.from_uci(result), chess.Board().legal_moves)
        self.assertEqual(search.call_count, 1)

    def test_prospective_repetition_at_seven_plies(self) -> None:
        board = chess.Board()
        for uci in ("g1f3", "g8f6", "f3g1", "f6g8", "g1f3", "g8f6", "f3g1"):
            board.push_uci(uci)
        original_fen = board.fen()
        original_stack = tuple(board.move_stack)

        self.assertFalse(board.is_repetition(3))
        self.assertTrue(board.can_claim_threefold_repetition())
        self.assertEqual(agent._terminal_score(board, 7), 0)
        self.assertEqual(
            agent._negamax(board, 0, -1_000_000, 1_000_000, 7, time.perf_counter() + 10),
            0,
        )
        self.assertEqual(board.fen(), original_fen)
        self.assertEqual(tuple(board.move_stack), original_stack)

    def test_prospective_fifty_move_draw_at_99_halfmoves(self) -> None:
        board = chess.Board("4k3/8/8/8/8/8/8/R3K3 w - - 99 51")
        original_fen = board.fen()

        self.assertFalse(board.is_fifty_moves())
        self.assertTrue(board.can_claim_fifty_moves())
        self.assertEqual(agent._terminal_score(board, 0), 0)
        self.assertEqual(
            agent._negamax(board, 0, -1_000_000, 1_000_000, 0, time.perf_counter() + 10),
            0,
        )
        self.assertEqual(board.fen(), original_fen)
        self.assertFalse(board.move_stack)

    def test_fifty_move_draw_not_claimable_at_98_halfmoves(self) -> None:
        board = chess.Board("4k3/8/8/8/8/8/8/R3K3 w - - 98 51")

        self.assertFalse(board.can_claim_fifty_moves())
        self.assertIsNone(board.outcome(claim_draw=True))
        self.assertIsNone(agent._terminal_score(board, 0))
        self.assertGreater(
            agent._negamax(board, 0, -1_000_000, 1_000_000, 0, time.perf_counter() + 10),
            0,
        )


if __name__ == "__main__":
    unittest.main()
