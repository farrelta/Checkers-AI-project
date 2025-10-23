import pygame as pg
from sys import exit
from pygame.locals import *
from board_gui import BoardGUI
from game_control import GameControl

def setup_game():
    print("Welcome to Checkers!")
    print("1. Player vs Player (PvP)")
    print("2. Player vs AI (PvAI)")
    mode = input("Choose mode (1 or 2): ").strip()
    
    if mode == "1":
        return "pvp", "W", None  # Default color for PvP, no difficulty
    elif mode == "2":
        print("Choose your piece color:")
        print("1. White")
        print("2. Black")
        color_choice = input("Choose color (1 or 2): ").strip()
        player_color = "W" if color_choice == "1" else "B"
        
        print("Choose AI difficulty:")
        print("1. Easy (faster, weaker AI)")
        print("2. Medium (balanced)")
        print("3. Hard (slower, stronger AI)")
        diff_choice = input("Choose difficulty (1, 2, or 3): ").strip()
        difficulty = {"1": "easy", "2": "medium", "3": "hard"}.get(diff_choice, "medium")
        
        return "pvai", player_color, difficulty
    else:
        print("Invalid choice. Defaulting to PvP.")
        return "pvp", "W", None

def main(gamemode, player_color, difficulty):
    import pygame as pg

    # --- Main setup ---
    pg.init()
    FPS = 30
    DISPLAYSURF = pg.display.set_mode((700, 500))
    pg.display.set_caption('Checkers in Python')
    fps_clock = pg.time.Clock()
    game_control = GameControl(player_color, gamemode == "pvai", difficulty)

    # Font setup
    main_font = pg.font.SysFont("Arial", 25)
    turn_rect = (509, 26)
    winner_rect = (509, 152)

    # --- Handle AI first move immediately if AI goes first ---
    if gamemode == "pvai" and game_control.turn != player_color:
        # If AI is white and first move
        game_control.move_ai_first_random()

    # --- Main loop ---
    while True:
        # GUI
        DISPLAYSURF.fill((0, 0, 0))
        game_control.draw_screen(DISPLAYSURF)

        # Display turn
        turn_display_text = "White's turn" if game_control.get_turn() == "W" else "Black's turn"
        DISPLAYSURF.blit(main_font.render(turn_display_text, True, (255, 255, 255)), turn_rect)

        # Display winner if exists
        if game_control.get_winner() is not None:
            winner_text = f"{'White' if game_control.get_winner() == 'W' else 'Black'} wins!"
            DISPLAYSURF.blit(main_font.render(winner_text, True, (255, 255, 255)), winner_rect)

        pg.display.update()
        fps_clock.tick(FPS)

        # --- Handle AI moves ---
        if gamemode == "pvai" and game_control.get_turn() != player_color and game_control.get_winner() is None:
            pg.time.delay(50)  # allow GUI update before heavy AI
            game_control.move_ai()

        # --- Handle user input ---
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                return
            if event.type == pg.MOUSEBUTTONDOWN:
                game_control.hold_piece(event.pos)
            if event.type == pg.MOUSEBUTTONUP:
                game_control.release_piece()

if __name__ == '__main__':
    gamemode, player_color, difficulty = setup_game()
    main(gamemode, player_color, difficulty)
    exit()