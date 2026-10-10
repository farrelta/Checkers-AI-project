import unittest

from ai import AI
from board import Board
from piece import Piece


class BoardRuleTests(unittest.TestCase):
    def test_capture_is_mandatory_across_all_pieces(self):
        board = Board(
            [Piece("21WN"), Piece("22WN"), Piece("17BN")],
            color_up="W",
        )

        legal_moves = board.get_legal_moves("W")

        self.assertEqual(len(legal_moves), 1)
        self.assertEqual(legal_moves[0]["move"], {"position": "12", "eats_piece": True})
        self.assertEqual(board.get_pieces()[legal_moves[0]["piece"]].get_position(), "21")

    def test_capture_chain_is_restricted_to_the_capturing_piece(self):
        board = Board(
            [Piece("21WN"), Piece("22WN"), Piece("17BN"), Piece("9BN")],
            color_up="W",
        )
        board.move_piece(0, 12)

        continuation = board.get_legal_moves("W", forced_piece_position="12")

        self.assertEqual(len(continuation), 1)
        self.assertEqual(continuation[0]["move"], {"position": "5", "eats_piece": True})
        self.assertEqual(board.get_legal_moves("W", forced_piece_position="22"), [])

    def test_empty_board_has_no_winner(self):
        self.assertIsNone(Board([], color_up="W").get_winner())


class AISearchTests(unittest.TestCase):
    def test_ai_chooses_the_forced_capture(self):
        board = Board(
            [Piece("21WN"), Piece("22WN"), Piece("17BN")],
            color_up="W",
        )
        ai = AI("W", "easy")

        move = ai.get_move(board)

        self.assertEqual(move, {"position_to": "12", "position_from": "21"})

    def test_ai_returns_no_move_when_its_pieces_are_blocked(self):
        board = Board([Piece("0WN"), Piece("31BN")], color_up="W")
        ai = AI("W", "easy")

        self.assertIsNone(ai.get_move(board))

    def test_ai_continues_a_forced_capture_chain(self):
        board = Board(
            [Piece("12WN"), Piece("22WN"), Piece("9BN")],
            color_up="W",
        )
        ai = AI("W", "easy")

        move = ai.get_move(board, forced_piece_position="12")

        self.assertEqual(move, {"position_to": "5", "position_from": "12"})


if __name__ == "__main__":
    unittest.main()
