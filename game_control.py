from piece import Piece
from board import Board
from board_gui import BoardGUI
from held_piece import HeldPiece
from ai import AI
from utils import get_surface_mouse_offset, get_piece_position
import random

class GameControl:
    def __init__(self, player_color, is_computer_opponent, difficulty=None):
        # Determine AI color
        ai_color = "B" if player_color == "W" else "W"
        self.ai_control = AI(ai_color, difficulty) if is_computer_opponent else None

        # Turn starts with white by default
        self.turn = "W"
        self.winner = None
        self.board = None
        self.board_draw = None
        self.held_piece = None
        self.ai_control = None

        if is_computer_opponent:
            ai_color = "B" if player_color == "W" else "W"
            starting_turn = "W"  # White always starts in Checkers
            self.turn = starting_turn
            self.ai_control = AI(ai_color, difficulty)  # Pass difficulty to AI

        self.setup()

    def get_turn(self):
        return self.turn

    def get_winner(self):
        return self.winner

    def setup(self):
        # Initial setup
        pieces = []

        for opponent_piece in range(0, 12):
            pieces.append(Piece(str(opponent_piece) + 'BN'))
        
        for player_piece in range(20, 32):
            pieces.append(Piece(str(player_piece) + 'WN'))
        
        self.board = Board(pieces, self.turn)
        self.board_draw = BoardGUI(self.board)        
        pass
    
    def draw_screen(self, display_surface):
        self.board_draw.draw_board(display_surface)
        self.board_draw.draw_pieces(display_surface)

        if self.held_piece is not None:
            self.held_piece.draw_piece(display_surface)

    def hold_piece(self, mouse_pos):
        piece_clicked = self.board_draw.get_piece_on_mouse(mouse_pos)
        board_pieces = self.board.get_pieces()
        has_jump_restraint = False # True if any piece can jump in one of its moves, forcing the player to jump

        if piece_clicked is None:
            return
        
        if piece_clicked["piece"]["color"] != self.turn:
            return
        
        # Determines if player has a jump restraint
        for piece in board_pieces:
            for move in piece.get_moves(self.board):
                if move["eats_piece"]:
                    if piece.get_color() == piece_clicked["piece"]["color"]:
                        has_jump_restraint = True
            else:
                continue
            break
        
        piece_moves = board_pieces[piece_clicked["index"]].get_moves(self.board)

        if has_jump_restraint:
            piece_moves = list(filter(lambda move: move["eats_piece"] == True, piece_moves))

        move_marks = []

        # Gets possible moving positions and tells BoardGUI to draw them
        for possible_move in piece_moves:
            row = self.board.get_row_number(int(possible_move["position"]))
            column = self.board.get_col_number(int(possible_move["position"]))
            move_marks.append((row, column))

        self.board_draw.set_move_marks(move_marks)

        self.board_draw.hide_piece(piece_clicked["index"])
        self.set_held_piece(piece_clicked["index"], board_pieces[piece_clicked["index"]], mouse_pos)

    def has_legal_moves(self, color):
            for piece in self.board.get_pieces():
                if piece.get_color() != color:
                    continue
                if piece.get_moves(self.board):  # If any piece has moves
                    return True
            return False
    
    def release_piece(self):
        if self.held_piece is None:
            return

        position_released = self.held_piece.check_collision(self.board_draw.get_move_marks())
        moved_index = self.board_draw.show_piece()
        piece_moved = self.board.get_piece_by_index(moved_index)

        # Only moves the piece if dropped in a proper move mark        
        if position_released is not None:
            self.board.move_piece(moved_index, self.board_draw.get_position_by_rect(position_released))
            self.board_draw.set_pieces(self.board_draw.get_piece_properties(self.board))
            self.winner = self.board.get_winner()

            # Check if player can eat another piece, granting an extra turn.
            jump_moves = list(filter(lambda move: move["eats_piece"] == True, piece_moved.get_moves(self.board)))
            
            # Determine next turn
            next_turn = "B" if self.turn == "W" else "W"

            # Check if next player has legal moves
            if not self.has_legal_moves(next_turn):
                # Next player cannot move → current player wins
                self.winner = self.turn
            else:
                # Switch turn normally
                self.turn = next_turn

        self.held_piece = None
        self.board_draw.set_move_marks([])

    def set_held_piece(self, index, piece, mouse_pos):
        # Creates a HeldPiece object to follow the mouse
        surface = self.board_draw.get_surface(piece)
        offset = get_surface_mouse_offset(self.board_draw.get_piece_by_index(index)["rect"], mouse_pos)
        self.held_piece = HeldPiece(surface, offset)

    def move_ai(self):
        # Gets best move from an AI instance and moves it.
        if self.turn != self.ai_control.color:
            return

        optimal_move = self.ai_control.get_move(self.board)

        # If no move possible, AI loses
        if optimal_move is None:
            self.winner = "B" if self.turn == "W" else "W"
            return
        

        index_moved = -1
        piece_moved = None

        for index, piece in enumerate(self.board.get_pieces()):
            if piece.get_position() == optimal_move["position_from"]:
                index_moved = index
                piece_moved = piece
                break
        else:
            raise RuntimeError("AI was supposed to return a move from an existing piece but found none.")
        
        self.board.move_piece(index_moved, int(optimal_move["position_to"]))
        self.board_draw.set_pieces(self.board_draw.get_piece_properties(self.board))
        self.winner = self.board.get_winner()

        # Check if AI can eat another piece, granting an extra turn.
        jump_moves = list(filter(lambda move: move["eats_piece"] == True, piece_moved.get_moves(self.board)))

        if len(jump_moves) == 0 or piece_moved.get_has_eaten() == False:
            self.turn = "B" if self.turn == "W" else "W"

    def move_ai_first_random(self):
        """Make a random move for AI (used for first move)"""
        if not self.ai_control:
            return

        ai_color = self.ai_control.color
        player_pieces = [p for p in self.board.get_pieces() if p.get_color() == ai_color]
        possible_moves = []

        for idx, piece in enumerate(self.board.get_pieces()):
            if piece.get_color() != ai_color:
                continue
            for move in piece.get_moves(self.board):
                possible_moves.append({"piece": idx, "move": move})

        if not possible_moves:
            # AI cannot move → human wins
            self.winner = "B" if ai_color == "W" else "W"
            return

        move = random.choice(possible_moves)
        self.board.move_piece(move["piece"], int(move["move"]["position"]))
        self.board_draw.set_pieces(self.board_draw.get_piece_properties(self.board))
        self.winner = self.board.get_winner()
        self.turn = "B" if ai_color == "W" else "W"