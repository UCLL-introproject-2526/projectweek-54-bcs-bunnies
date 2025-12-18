import pygame
import sys
import os

from settings import WIDTH, HEIGHT, FPS, WHITE, BLACK
from ui import ImageButton, safe_load_bg, safe_load_png, scale_to_width, draw_text_outline
from game import run_game

# States
MENU = "menu"
HOWTO = "howto"


def main():
    pygame.init()
    pygame.font.init()

    # ---------------- MENU MUSIC ----------------
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        menu_music = pygame.mixer.Sound("sound/menu.mp3")
        menu_music.set_volume(0.6)
    except Exception as e:
        print("[AUDIO] Menu music failed:", e)
        menu_music = None
    # --------------------------------------------

    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Bunnies Beta v1.0")

    # Fonts (load from .ttf file)
    def load_font(size):
        try:
            return pygame.font.Font("font.ttf", size)
        except:
            return pygame.font.SysFont(None, size, bold=True)

    FONT = load_font(30)
    BIG_FONT = load_font(48)
    END_FONT = load_font(80)

    # Backgrounds
    MENU_BG = safe_load_bg("images/menu_background.png", (30, 120, 80))
    HOWTO_BG = safe_load_bg("images/howtoplay_background.png", (30, 120, 80))

    # Buttons
    TARGET_BTN_WIDTH = 480
    PLAY_IMG = scale_to_width(safe_load_png("images/play_button.png"), TARGET_BTN_WIDTH)
    HOW_IMG  = scale_to_width(safe_load_png("images/howtoplay_button.png"), TARGET_BTN_WIDTH)
    QUIT_IMG = scale_to_width(safe_load_png("images/quit_button.png"), TARGET_BTN_WIDTH)

    BACK_BTN_WIDTH = 320
    BACK_IMG = scale_to_width(safe_load_png("images/back_button.png"), BACK_BTN_WIDTH)

    play_btn = ImageButton(PLAY_IMG, (WIDTH // 2, 470))
    how_btn  = ImageButton(HOW_IMG,  (WIDTH // 2, 565))
    quit_btn = ImageButton(QUIT_IMG, (WIDTH // 2, 660))
    back_btn = ImageButton(BACK_IMG, (WIDTH // 2, 620))

    clock = pygame.time.Clock()
    state = MENU

    # ▶️ START menu music
    if menu_music:
        menu_music.play(loops=-1)

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
                    if menu_music:
                        menu_music.stop()   # 🔇 stop menu music
                    result = run_game(WIN, FONT, END_FONT)
                    if result == "quit":
                        running = False
                    else:
                        state = MENU
                        if menu_music:
                            menu_music.play(loops=-1)

                elif how_btn.clicked(event):
                    if menu_music:
                        menu_music.stop()
                    state = HOWTO

                elif quit_btn.clicked(event):
                    running = False

            elif state == HOWTO:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    state = MENU
                    if menu_music:
                        menu_music.play(loops=-1)

                if back_btn.clicked(event):
                    state = MENU
                    if menu_music:
                        menu_music.play(loops=-1)

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
