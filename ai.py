"""A time-bounded minimax player for the game's checkers rules."""

from copy import deepcopy
import time

from board import Board


class _SearchTimeout(Exception):
    """Raised when an iterative-deepening search reaches its time budget."""


class AI:
    MATE_SCORE = 10_000

    def __init__(self, color, difficulty="medium"):
        self.color = color
        self.transposition_table = {}
        settings = {
            "easy": (3, 1.0),
            "medium": (5, 2.0),
            "hard": (8, 3.0),
        }
        self.max_depth, self.time_limit = settings.get(difficulty, settings["medium"])
        self._deadline = None

    def _check_time(self):
        if self._deadline is not None and time.monotonic() >= self._deadline:
            raise _SearchTimeout

    def _state_key(self, board, turn, maximizing, depth, forced_piece_position):
        pieces = tuple(sorted(piece.get_name() for piece in board.get_pieces()))
        return (pieces, board.get_color_up(), turn, maximizing, depth, forced_piece_position)

    def minimax(
        self, current_board, is_maximizing, depth, turn,
        alpha=-float("inf"), beta=float("inf"), forced_piece_position=None,
    ):
        """Search legal moves, keeping the same turn during a capture chain."""
        self._check_time()
        if current_board.get_winner() is not None:
            return self.get_value(current_board)

        original_alpha, original_beta = alpha, beta
        key = self._state_key(current_board, turn, is_maximizing, depth, forced_piece_position)
        cached = self.transposition_table.get(key)
        if cached is not None:
            value, bound = cached
            if bound == "exact":
                return value
            if bound == "lower":
                alpha = max(alpha, value)
            else:  # upper bound
                beta = min(beta, value)
            if alpha >= beta:
                return value

        legal_moves = current_board.get_legal_moves(turn, forced_piece_position)
        if not legal_moves:
            return -self.MATE_SCORE if turn == self.color else self.MATE_SCORE
        if depth <= 0 and forced_piece_position is None:
            return self.get_value(current_board)

        maximizing = turn == self.color
        best_value = -float("inf") if maximizing else float("inf")
        next_turn = "B" if turn == "W" else "W"

        for candidate in legal_moves:
            self._check_time()
            next_board = Board(deepcopy(current_board.get_pieces()), current_board.get_color_up())
            piece = next_board.get_pieces()[candidate["piece"]]
            next_board.move_piece(candidate["piece"], int(candidate["move"]["position"]))

            # A capture chain is still the same player's turn and does not
            # consume a search ply until that chain is complete.
            if candidate["move"]["eats_piece"]:
                continuation = next_board.get_legal_moves(turn, piece.get_position())
            else:
                continuation = []

            if continuation:
                child_turn = turn
                child_maximizing = maximizing
                child_depth = depth
                child_forced = piece.get_position()
            else:
                child_turn = next_turn
                child_maximizing = not maximizing
                child_depth = depth - 1
                child_forced = None

            value = self.minimax(
                next_board, child_maximizing, child_depth, child_turn,
                alpha, beta, child_forced,
            )
            if maximizing:
                best_value = max(best_value, value)
                alpha = max(alpha, best_value)
            else:
                best_value = min(best_value, value)
                beta = min(beta, best_value)
            if alpha >= beta:
                break

        if best_value <= original_alpha:
            bound = "upper"
        elif best_value >= original_beta:
            bound = "lower"
        else:
            bound = "exact"
        self.transposition_table[key] = (best_value, bound)
        return best_value

    def get_move(self, current_board, forced_piece_position=None):
        legal_moves = current_board.get_legal_moves(self.color, forced_piece_position)
        if not legal_moves:
            return None

        # Keep a legal fallback so a timeout can never leave the AI without a move.
        best_move = legal_moves[0]
        self.transposition_table.clear()
        self._deadline = time.monotonic() + self.time_limit
        opponent = "B" if self.color == "W" else "W"

        try:
            for depth in range(1, self.max_depth + 1):
                self._check_time()
                depth_best_move = None
                depth_best_score = -float("inf")
                for candidate in legal_moves:
                    self._check_time()
                    next_board = Board(deepcopy(current_board.get_pieces()), current_board.get_color_up())
                    piece = next_board.get_pieces()[candidate["piece"]]
                    next_board.move_piece(candidate["piece"], int(candidate["move"]["position"]))
                    continuation = (
                        next_board.get_legal_moves(self.color, piece.get_position())
                        if candidate["move"]["eats_piece"] else []
                    )
                    if continuation:
                        child_turn, child_depth, child_forced = self.color, depth, piece.get_position()
                    else:
                        child_turn, child_depth, child_forced = opponent, depth - 1, None
                    score = self.minimax(
                        next_board, child_turn == self.color, child_depth,
                        child_turn, forced_piece_position=child_forced,
                    )
                    if score > depth_best_score:
                        depth_best_score = score
                        depth_best_move = candidate
                if depth_best_move is not None:
                    best_move = depth_best_move
        except _SearchTimeout:
            pass
        finally:
            self._deadline = None

        piece = current_board.get_pieces()[best_move["piece"]]
        return {
            "position_to": best_move["move"]["position"],
            "position_from": piece.get_position(),
        }

    def get_value(self, board):
        winner = board.get_winner()
        if winner is not None:
            return self.MATE_SCORE if winner == self.color else -self.MATE_SCORE

        score = 0.0
        for piece in board.get_pieces():
            sign = 1 if piece.get_color() == self.color else -1
            score += sign * (5 if piece.is_king() else 1)
            position = int(piece.get_position())
            row = board.get_row_number(position)
            col = board.get_col_number(position)
            if 2 <= row <= 5 and 2 <= col <= 5:
                score += sign * 0.5

        own_mobility = len(board.get_legal_moves(self.color))
        opponent = "B" if self.color == "W" else "W"
        opponent_mobility = len(board.get_legal_moves(opponent))
        score += 0.1 * (own_mobility - opponent_mobility)
        return score
