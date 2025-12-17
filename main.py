import pygame
import sys
import os

from settings import WIDTH, HEIGHT, FPS, WHITE, BLACK
from ui import ImageButton, safe_load_bg, safe_load_png, scale_to_width, draw_text_outline
from game import run_game

# Statessd
MENU = "menu"
HOWTO = "howto"


def main():
    pygame.init()
    pygame.font.init()

    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Bunnies Beta v1.0")

    # Fonts
    FONT = pygame.font.SysFont("pixelfont.ttf", 30, bold=True)
    BIG_FONT = pygame.font.SysFont("pixelfont.ttf", 48, bold=True)
    END_FONT = pygame.font.SysFont("pixelfont.ttf", 80, bold=True)

    # Backgrounds (safe load)
    MENU_BG = safe_load_bg("images/menu_background.png", (30, 120, 80))
    HOWTO_BG = safe_load_bg("images/howtoplay_background.png", (30, 120, 80))

    # Buttons (safe load + scale)
    TARGET_BTN_WIDTH = 480
    PLAY_IMG = scale_to_width(safe_load_png(
        "images/play_button.png"), TARGET_BTN_WIDTH, smooth=False)
    HOW_IMG = scale_to_width(safe_load_png(
        "images/howtoplay_button.png"), TARGET_BTN_WIDTH, smooth=False)
    QUIT_IMG = scale_to_width(safe_load_png(
        "images/quit_button.png"), TARGET_BTN_WIDTH, smooth=False)

    BACK_BTN_WIDTH = 320
    BACK_IMG = scale_to_width(safe_load_png(
        "images/back_button.png"), BACK_BTN_WIDTH, smooth=False)

    # Position buttons
    play_btn = ImageButton(PLAY_IMG, (WIDTH // 2, 470))
    how_btn = ImageButton(HOW_IMG,  (WIDTH // 2, 565))
    quit_btn = ImageButton(QUIT_IMG, (WIDTH // 2, 660))
    back_btn = ImageButton(BACK_IMG, (WIDTH // 2, 620))

    clock = pygame.time.Clock()
    state = MENU

    howto_lines = [
        "Move: WASD or Arrow Keys",
        "Go through portals at the edges to explore new areas",
        "Collect carrots to increase your score",
        "Foxes chase you — getting caught costs a life",
        "Reach the target score to win",
        "ESC pauses the game",
        "ENTER while paused resets the game",
        "SPACE = Dash (cooldown)",
    ]

    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if state == MENU:
                if play_btn.clicked(event):
                    result = run_game(WIN, FONT, END_FONT)
                    if result == "quit":
                        running = False
                    state = MENU
                elif how_btn.clicked(event):
                    state = HOWTO
                elif quit_btn.clicked(event):
                    running = False

            elif state == HOWTO:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    state = MENU
                if back_btn.clicked(event):
                    state = MENU

        # ----- DRAW -----
        if state == MENU:
            WIN.blit(MENU_BG, (0, 0))
            play_btn.draw(WIN)
            how_btn.draw(WIN)
            quit_btn.draw(WIN)

        elif state == HOWTO:
            WIN.blit(HOWTO_BG, (0, 0))
            draw_text_outline(WIN, "HOW TO PLAY", BIG_FONT, WHITE, BLACK,
                              center=(WIDTH // 2, 120), outline_thickness=3)

            y = 220
            for line in howto_lines:
                draw_text_outline(WIN, line, FONT, WHITE, BLACK,
                                  center=(WIDTH // 2, y), outline_thickness=2)
                y += 42

            back_btn.draw(WIN)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
