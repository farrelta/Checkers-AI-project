from ai import AI
from board import Board
from board_gui import BoardGUI
from held_piece import HeldPiece
from piece import Piece
from utils import get_surface_mouse_offset


class GameControl:
    def __init__(self, player_color, is_computer_opponent, difficulty=None):
        self.turn = "W"
        self.winner = None
        self.board = None
        self.board_draw = None
        self.held_piece = None
        self.forced_piece_position = None
        ai_color = "B" if player_color == "W" else "W"
        self.ai_control = AI(ai_color, difficulty) if is_computer_opponent else None
        self.setup()

    def get_turn(self):
        return self.turn

    def get_winner(self):
        return self.winner

    def setup(self):
        pieces = [Piece(str(position) + "BN") for position in range(12)]
        pieces.extend(Piece(str(position) + "WN") for position in range(20, 32))
        self.board = Board(pieces, self.turn)
        self.board_draw = BoardGUI(self.board)

    def draw_screen(self, display_surface):
        self.board_draw.draw_board(display_surface)
        self.board_draw.draw_pieces(display_surface)
        if self.held_piece is not None:
            self.held_piece.draw_piece(display_surface)

    def hold_piece(self, mouse_pos):
        if self.winner is not None:
            return
        clicked = self.board_draw.get_piece_on_mouse(mouse_pos)
        if clicked is None or clicked["piece"]["color"] != self.turn:
            return

        index = clicked["index"]
        piece = self.board.get_piece_by_index(index)
        if self.forced_piece_position is not None and piece.get_position() != self.forced_piece_position:
            return

        legal_moves = self.board.get_legal_moves(self.turn, self.forced_piece_position)
        piece_moves = [item["move"] for item in legal_moves if item["piece"] == index]
        if not piece_moves:
            return

        marks = []
        for move in piece_moves:
            position = int(move["position"])
            marks.append((self.board.get_row_number(position), self.board.get_col_number(position)))
        self.board_draw.set_move_marks(marks)
        self.board_draw.hide_piece(index)
        surface = self.board_draw.get_surface(piece)
        offset = get_surface_mouse_offset(self.board_draw.get_piece_by_index(index)["rect"], mouse_pos)
        self.held_piece = HeldPiece(surface, offset)

    def has_legal_moves(self, color):
        return bool(self.board.get_legal_moves(color))

    def _finish_turn(self):
        self.forced_piece_position = None
        next_turn = "B" if self.turn == "W" else "W"
        if self.board.get_winner() is not None:
            self.winner = self.board.get_winner()
        elif not self.has_legal_moves(next_turn):
            self.winner = self.turn
        else:
            self.turn = next_turn
        self.board_draw.set_move_marks([])

    def release_piece(self):
        if self.held_piece is None:
            return

        destination_rect = self.held_piece.check_collision(self.board_draw.get_move_marks())
        moved_index = self.board_draw.show_piece()
        if destination_rect is None:
            self.board_draw.set_pieces(self.board_draw.get_piece_properties(self.board))
            if self.forced_piece_position is None:
                self.board_draw.set_move_marks([])
            self.held_piece = None
            return

        destination = self.board_draw.get_position_by_rect(destination_rect)
        moved_piece = self.board.get_piece_by_index(moved_index)
        self.board.move_piece(moved_index, destination)
        self.board_draw.set_pieces(self.board_draw.get_piece_properties(self.board))
        self.held_piece = None

        if self.board.get_winner() is not None:
            self.winner = self.board.get_winner()
            self.forced_piece_position = None
            self.board_draw.set_move_marks([])
            return

        continuations = self.board.get_legal_moves(self.turn, moved_piece.get_position())
        if moved_piece.get_has_eaten() and continuations:
            self.forced_piece_position = moved_piece.get_position()
            marks = []
            for item in continuations:
                position = int(item["move"]["position"])
                marks.append((self.board.get_row_number(position), self.board.get_col_number(position)))
            self.board_draw.set_move_marks(marks)
            return

        self._finish_turn()

    def move_ai(self):
        if self.ai_control is None or self.turn != self.ai_control.color or self.winner is not None:
            return

        move = self.ai_control.get_move(self.board, self.forced_piece_position)
        if move is None:
            self.winner = "B" if self.turn == "W" else "W"
            return

        for index, piece in enumerate(self.board.get_pieces()):
            if piece.get_position() == move["position_from"]:
                moved_index = index
                moved_piece = piece
                break
        else:
            raise RuntimeError("The AI selected a piece that is not on the board.")

        self.board.move_piece(moved_index, int(move["position_to"]))
        self.board_draw.set_pieces(self.board_draw.get_piece_properties(self.board))

        if self.board.get_winner() is not None:
            self.winner = self.board.get_winner()
            self.forced_piece_position = None
            return

        continuations = self.board.get_legal_moves(self.turn, moved_piece.get_position())
        if moved_piece.get_has_eaten() and continuations:
            self.forced_piece_position = moved_piece.get_position()
            return

        self._finish_turn()

    def move_ai_first_random(self):
        """Compatibility wrapper; opening moves now use the normal AI search."""
        self.move_ai()
