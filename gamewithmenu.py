import pygame
import time
import sys

pygame.init()
pygame.font.init()

# --- Display ---
WIDTH, HEIGHT = 1280, 720
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("bunnies beta V 1.0")

# change background picture later
BG = pygame.transform.scale(pygame.image.load("images/bg.png"), (WIDTH, HEIGHT))

# --- Player ---
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60
PLAYER_SPEED = 500  # pixels/sec

# --- Fonts ---
FONT = pygame.font.SysFont("comicsans", 30)
TITLE_FONT = pygame.font.SysFont("comicsans", 72)
BIG_FONT = pygame.font.SysFont("comicsans", 48)

# --- States ---
MENU = "menu"
HOWTO = "howto"
PLAYING = "playing"
PAUSED = "paused"
GAMEOVER = "gameover"

# ---------------- UI Helpers ----------------

def draw_text_center(text, font, color, y):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(WIDTH // 2, y))
    WIN.blit(surf, rect)

class Button:
    def __init__(self, text, center, size=(320, 60)):
        self.text = text
        self.rect = pygame.Rect(0, 0, size[0], size[1])
        self.rect.center = center

    def draw(self, mouse_pos):
        hover = self.rect.collidepoint(mouse_pos)
        bg = (80, 80, 80) if hover else (50, 50, 50)
        pygame.draw.rect(WIN, bg, self.rect, border_radius=10)
        pygame.draw.rect(WIN, (200, 200, 200), self.rect, 2, border_radius=10)

        label = FONT.render(self.text, True, (255, 255, 255))
        label_rect = label.get_rect(center=self.rect.center)
        WIN.blit(label, label_rect)

    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)

# ---------------- Screens ----------------

def draw_game(player, elapsed_time, caught_count):
    WIN.blit(BG, (0, 0))
    pygame.draw.rect(WIN, "red", player)

    time_text = FONT.render(f"Time: {round(elapsed_time)}s", True, "white")
    caught_text = FONT.render(f"Caught: {caught_count}", True, "white")

    WIN.blit(time_text, (10, 10))
    WIN.blit(caught_text, (10, 45))
    pygame.display.update()

def draw_menu(mouse_pos):
    WIN.blit(BG, (0, 0))
    draw_text_center("BUNNIES", TITLE_FONT, (255, 255, 255), 160)
    draw_text_center("beta v1.0", FONT, (220, 220, 220), 220)

    btn_play = Button("Play", (WIDTH//2, 340))
    btn_how  = Button("How to Play", (WIDTH//2, 420))
    btn_quit = Button("Quit", (WIDTH//2, 500))

    for b in (btn_play, btn_how, btn_quit):
        b.draw(mouse_pos)

    pygame.display.update()
    return btn_play, btn_how, btn_quit

def draw_howto(mouse_pos):
    WIN.blit(BG, (0, 0))
    draw_text_center("HOW TO PLAY", BIG_FONT, (255, 255, 255), 130)

    lines = [
        "Move: WASD or Arrow Keys",
        "Goal: Find portals at the sides, then reach the bunny hole.",
        "Avoid foxes. First catch spawns more foxes.",
        "Second catch = Game Over.",
        "",
        "Press ESC to pause during the game.",
    ]
    y = 220
    for line in lines:
        draw_text_center(line, FONT, (235, 235, 235), y)
        y += 38

    btn_back = Button("Back", (WIDTH//2, 580))
    btn_back.draw(mouse_pos)

    pygame.display.update()
    return btn_back

def draw_pause(mouse_pos):
    # Dark overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    WIN.blit(overlay, (0, 0))

    draw_text_center("PAUSED", BIG_FONT, (255, 255, 255), 200)

    btn_resume = Button("Resume", (WIDTH//2, 330))
    btn_restart = Button("Restart", (WIDTH//2, 410))
    btn_menu = Button("Main Menu", (WIDTH//2, 490))

    for b in (btn_resume, btn_restart, btn_menu):
        b.draw(mouse_pos)

    pygame.display.update()
    return btn_resume, btn_restart, btn_menu

def draw_gameover(mouse_pos, elapsed_time, caught_count):
    WIN.blit(BG, (0, 0))
    draw_text_center("GAME OVER", BIG_FONT, (255, 80, 80), 180)
    draw_text_center(f"Survived: {round(elapsed_time)}s", FONT, (255, 255, 255), 250)
    draw_text_center(f"Caught: {caught_count}", FONT, (255, 255, 255), 290)

    btn_restart = Button("Restart", (WIDTH//2, 410))
    btn_menu = Button("Main Menu", (WIDTH//2, 490))
    btn_quit = Button("Quit", (WIDTH//2, 570))

    for b in (btn_restart, btn_menu, btn_quit):
        b.draw(mouse_pos)

    pygame.display.update()
    return btn_restart, btn_menu, btn_quit

# ---------------- Game Setup ----------------

def new_run():
    player = pygame.Rect(
        WIDTH // 2 - PLAYER_WIDTH // 2,
        HEIGHT // 2 - PLAYER_HEIGHT // 2,
        PLAYER_WIDTH,
        PLAYER_HEIGHT
    )
    start_time = time.time()
    caught_count = 0
    return player, start_time, caught_count

# ---------------- Main Loop ----------------

def main():
    clock = pygame.time.Clock()
    state = MENU

    player, start_time, caught_count = new_run()
    elapsed_time = 0

    run = True
    while run:
        dt = clock.tick(80) / 1000.0
        mouse_pos = pygame.mouse.get_pos()

        # --- Events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            # ESC handling - needs fixing
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if state == PLAYING:
                    state = PAUSED
                elif state == PAUSED:
                    state = PLAYING
                elif state == HOWTO:
                    state = MENU

            # --- State-specific clicks ---
            if state == MENU:
                btn_play, btn_how, btn_quit = draw_menu(mouse_pos)
                if btn_play.clicked(event):
                    player, start_time, caught_count = new_run()
                    state = PLAYING
                elif btn_how.clicked(event):
                    state = HOWTO
                elif btn_quit.clicked(event):
                    run = False

            elif state == HOWTO:
                btn_back = draw_howto(mouse_pos)
                if btn_back.clicked(event):
                    state = MENU

            elif state == PAUSED:
                btn_resume, btn_restart, btn_menu = draw_pause(mouse_pos)
                if btn_resume.clicked(event):
                    state = PLAYING
                elif btn_restart.clicked(event):
                    player, start_time, caught_count = new_run()
                    state = PLAYING
                elif btn_menu.clicked(event):
                    state = MENU

            elif state == GAMEOVER:
                btn_restart, btn_menu, btn_quit = draw_gameover(mouse_pos, elapsed_time, caught_count)
                if btn_restart.clicked(event):
                    player, start_time, caught_count = new_run()
                    state = PLAYING
                elif btn_menu.clicked(event):
                    state = MENU
                elif btn_quit.clicked(event):
                    run = False

        # --- Update + Draw ---
        if state == PLAYING:
            elapsed_time = time.time() - start_time

            # Movement
            keys = pygame.key.get_pressed()
            x_input = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
            y_input = (keys[pygame.K_DOWN] or keys[pygame.K_s]) - (keys[pygame.K_UP] or keys[pygame.K_w])

            move = pygame.math.Vector2(x_input, y_input)
            if move.length_squared() > 0:
                move = move.normalize() * PLAYER_SPEED * dt
                player.x += int(move.x)
                player.y += int(move.y)

            # Clamp bounds
            player.x = max(0, min(player.x, WIDTH - PLAYER_WIDTH))
            player.y = max(0, min(player.y, HEIGHT - PLAYER_HEIGHT))

            # ---- PLACEHOLDER: simulate getting caught ----
            # Replace this with your fox collision logic later.
            # Press C to "get caught".
            if keys[pygame.K_c]:
                caught_count += 1
                pygame.time.delay(150)  # prevents instant double increments
                if caught_count >= 2:
                    state = GAMEOVER
                # else: this is where you'd spawn more foxes

            draw_game(player, elapsed_time, caught_count)

        elif state == MENU:
            draw_menu(mouse_pos)

        elif state == HOWTO:
            draw_howto(mouse_pos)

        elif state == PAUSED:
            # Draw the game under pause overlay (optional)
            draw_game(player, elapsed_time, caught_count)
            draw_pause(mouse_pos)

        elif state == GAMEOVER:
            draw_gameover(mouse_pos, elapsed_time, caught_count)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
