from board import Board
from copy import deepcopy
from random import choice
import time

class AI:
    def __init__(self, color, difficulty="medium"):
        self.color = color
        self.transposition_table = {}
        
        # Set difficulty-based parameters
        if difficulty == "easy":
            self.max_depth = 3
            self.time_limit = 1.0
        elif difficulty == "hard":
            self.max_depth = 8
            self.time_limit = 3.0
        else:  # medium
            self.max_depth = 5
            self.time_limit = 2.0

    def minimax(self, current_board, is_maximizing, depth, turn, alpha=-float('inf'), beta=float('inf')):
        # Alpha-beta pruning added for efficiency
        board_hash = self._hash_board(current_board)
        key = (board_hash, depth, is_maximizing)
        if key in self.transposition_table:
            return self.transposition_table[key]

        if depth == 0 or current_board.get_winner() is not None:
            value = self.get_value(current_board)
            self.transposition_table[key] = value
            return value

        next_turn = 'B' if turn == 'W' else 'W'
        board_color_up = current_board.get_color_up()
        current_pieces = current_board.get_pieces()
        piece_moves = list(map(lambda piece: piece.get_moves(current_board) if piece.get_color() == turn else False, current_pieces))

        if is_maximizing:
            maximum = -float('inf')
            for index, moves in enumerate(piece_moves):
                if moves == False:
                    continue
                for move in moves:
                    aux_board = Board(deepcopy(current_pieces), board_color_up)
                    aux_board.move_piece(index, int(move["position"]))
                    eval = self.minimax(aux_board, False, depth - 1, next_turn, alpha, beta)
                    maximum = max(maximum, eval)
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break  # Prune
            self.transposition_table[key] = maximum
            return maximum
        else:
            minimum = float('inf')
            for index, moves in enumerate(piece_moves):
                if moves == False:
                    continue
                for move in moves:
                    aux_board = Board(deepcopy(current_pieces), board_color_up)
                    aux_board.move_piece(index, int(move["position"]))
                    eval = self.minimax(aux_board, True, depth - 1, next_turn, alpha, beta)
                    minimum = min(minimum, eval)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break  # Prune
            self.transposition_table[key] = minimum
            return minimum

    def get_move(self, current_board):
        # Iterative deepening with time limit for responsiveness
        board_color_up = current_board.get_color_up()
        current_pieces = current_board.get_pieces()
        next_turn = "W" if self.color == "B" else "B"
        player_pieces = list(map(lambda piece: piece if piece.get_color() == self.color else False, current_pieces))
        possible_moves = []
        start_time = time.time()

        for index, piece in enumerate(player_pieces):
            if piece == False:
                continue
            for move in piece.get_moves(current_board):
                possible_moves.append({"piece": index, "move": move})

        # Enforce jump rules
        jump_moves = list(filter(lambda move: move["move"]["eats_piece"] == True, possible_moves))
        if len(jump_moves) != 0:
            possible_moves = jump_moves

        # If no moves available, return None (indicates loss)
        if not possible_moves:
            return None

        best_move = None
        best_score = -float('inf')

        # Iterative deepening: try depths 1 to self.max_depth, but stop if time > self.time_limit
        for depth in range(1, self.max_depth + 1):  
            if time.time() - start_time > self.time_limit:  
                break
            current_best_score = -float('inf')
            current_best_move = None
            for move in possible_moves:
                aux_board = Board(deepcopy(current_pieces), board_color_up)
                aux_board.move_piece(move["piece"], int(move["move"]["position"]))
                score = self.minimax(aux_board, False, depth, next_turn)
                if score > current_best_score:
                    current_best_score = score
                    current_best_move = move
            if current_best_move:
                best_move = current_best_move
                best_score = current_best_score

        if not best_move:
            # Fallback to random if no move found (rare)
            best_move = choice(possible_moves)

        return {"position_to": best_move["move"]["position"], "position_from": player_pieces[best_move["piece"]].get_position()}

    def get_value(self, board):
        # Enhanced evaluation: considers wins, piece counts, kings, positions, and mobility
        board_pieces = board.get_pieces()
        winner = board.get_winner()

        if winner is not None:
            return 100 if winner == self.color else -100  # Strong win/loss bonus

        score = 0
        player_pieces = [p for p in board_pieces if p.get_color() == self.color]
        opponent_pieces = [p for p in board_pieces if p.get_color() != self.color]

        # Piece count and king bonus
        for piece in player_pieces:
            value = 5 if piece.is_king() else 1
            score += value
            # Center bonus (rows 2-5, cols 2-5 are strategic)
            row = board.get_row_number(int(piece.get_position()))
            col = board.get_col_number(int(piece.get_position()))
            if 2 <= row <= 5 and 2 <= col <= 5:
                score += 0.5
        for piece in opponent_pieces:
            value = 5 if piece.is_king() else 1
            score -= value
            row = board.get_row_number(int(piece.get_position()))
            col = board.get_col_number(int(piece.get_position()))
            if 2 <= row <= 5 and 2 <= col <= 5:
                score -= 0.5

        # Mobility bonus: number of possible moves
        player_moves = sum(len(p.get_moves(board)) for p in player_pieces)
        opponent_moves = sum(len(p.get_moves(board)) for p in opponent_pieces)
        score += 0.1 * player_moves
        score -= 0.1 * opponent_moves

        return score

    def _hash_board(self, board):
        # Simple hash for transposition: tuple of piece names (includes position, color, king status)
        return tuple(piece.get_name() for piece in board.get_pieces())