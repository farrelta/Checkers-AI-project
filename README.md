# Checkers AI

A Python checkers game with player-versus-player and player-versus-AI modes. The graphical interface is built with Pygame CE.

## Features

- Play against another person or the computer.
- Choose to play as white or black in player-versus-AI mode.
- Select an AI difficulty level.
- Follow mandatory captures and chained jumps.
- Promote pieces to kings.

## Requirements

- Python 3
- pip

## Installation

Create and activate a virtual environment, then install the dependencies:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirement.txt
```

On macOS or Linux, activate the environment with:

```bash
source .venv/bin/activate
```

## Run the game

From the project directory, run:

```bash
python checkers.py
```

Choose a game mode in the terminal. In player-versus-AI mode, choose your color and the AI difficulty. Drag a piece to a marked square to make a move. The game enforces captures and requires you to complete a chained jump with the same piece.

## AI difficulty

The AI uses iterative deepening with a maximum search depth and time budget for each move. It may stop before reaching the maximum depth when the time limit is reached.

| Level | Maximum search depth | Time limit |
| --- | ---: | ---: |
| Easy | 3 | 1 second |
| Medium | 5 | 2 seconds |
| Hard | 8 | 3 seconds |

## AI method

The computer opponent uses minimax search with alpha-beta pruning. It evaluates positions using piece count, king value, center control, and available legal moves. Iterative deepening searches progressively deeper while respecting the time limit, and a transposition table reuses search results for repeated positions. This is a search-based game AI; it does not train a machine-learning model.

## Tests

Run the rule and AI tests with:

```bash
python -m unittest -v
```

## Project structure

- `checkers.py` — starts the game and handles the main loop.
- `game_control.py` — manages turns, player input, and AI moves.
- `board.py` and `piece.py` — represent the board, pieces, and legal moves.
- `ai.py` — contains the minimax search, evaluation, and difficulty settings.
- `board_gui.py` and `held_piece.py` — draw the board and handle dragged pieces.
- `utils.py` — coordinate conversion helpers.
- `test_checkers.py` — rule and AI search tests.

## Credits

The original game design was adapted from [lucaskenji/python-checkers](https://github.com/lucaskenji/python-checkers).

## AI references

- Russell, S. J., and Norvig, P. *Artificial Intelligence: A Modern Approach*, 4th edition. See the sections on minimax, alpha-beta pruning, and iterative deepening in the [table of contents](https://aima.cs.berkeley.edu/~russell/aima/contents.html).
- Knuth, D. E., and Moore, R. W. “An Analysis of Alpha-Beta Pruning.” *Artificial Intelligence*, 6(4), 293–326, 1975. [https://doi.org/10.1016/0004-3702(75)90019-3](https://doi.org/10.1016/0004-3702(75)90019-3).
