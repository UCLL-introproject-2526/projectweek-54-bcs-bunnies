import pygame
import time
import random
import sys

#helper function to help resize the button pictures
def scale_to_width(image, target_width):
    w, h = image.get_size()
    scale = target_width / w
    return pygame.transform.smoothscale(image, (int(w * scale), int(h * scale)))

# ---------------- INIT ----------------
pygame.init()
pygame.font.init()

# ---------------- DISPLAY ----------------
WIDTH, HEIGHT = 1280, 720
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bunnies Beta v1.0")

# Background safe-load
try:
    BG = pygame.transform.scale(pygame.image.load("images/bg.png"), (WIDTH, HEIGHT))
except:
    BG = pygame.Surface((WIDTH, HEIGHT))
    BG.fill((34, 139, 34))

# ---------------- CONSTANTS ----------------
FPS = 60

PLAYER_WIDTH, PLAYER_HEIGHT = 40, 60
PLAYER_SPEED = 500

FOX_WIDTH, FOX_HEIGHT = 50, 50
FOX_SPEED = 220

CARROT_SIZE = 25
TOTAL_CARROTS = 5

LIVES_START = 2
HIT_COOLDOWN = 1.0  # seconds (prevents double hits)

#menu
class ImageButton:
    def __init__(self, image, center):
        self.image = image
        self.rect = self.image.get_rect(center=center)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(event.pos))
    
MENU_BG = pygame.transform.scale(pygame.image.load("images/menu_background.png").convert(), (WIDTH, HEIGHT))
HOWTO_BG =  pygame.transform.scale(pygame.image.load("images/howtoplay_background.png").convert(),(WIDTH, HEIGHT))

PLAY_IMG = pygame.image.load("images/play_button.png").convert_alpha()
HOW_IMG  = pygame.image.load("images/howtoplay_button.png").convert_alpha()
QUIT_IMG = pygame.image.load("images/quit_button.png").convert_alpha()

TARGET_BTN_WIDTH = 480

PLAY_IMG = scale_to_width(PLAY_IMG, TARGET_BTN_WIDTH)
HOW_IMG  = scale_to_width(HOW_IMG,  TARGET_BTN_WIDTH)
QUIT_IMG = scale_to_width(QUIT_IMG, TARGET_BTN_WIDTH)

# ---------------- FONTS ----------------
FONT = pygame.font.SysFont("comicsans", 30)
BIG_FONT = pygame.font.SysFont("comicsans", 48)
TITLE_FONT = pygame.font.SysFont("comicsans", 72)
END_FONT = pygame.font.SysFont("comicsans", 80)

# ---------------- STATES ----------------
MENU = "menu"
HOWTO = "howto"
PLAYING = "playing"
PAUSED = "paused"

# ---------------- UI HELPERS ----------------
def draw_text_center(text, font, color, y):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(WIDTH // 2, y))
    WIN.blit(surf, rect)

class Button:
    def __init__(self, text, center, size=(320, 60)):
        self.text = text
        self.rect = pygame.Rect(0, 0, *size)
        self.rect.center = center

    def draw(self, mouse):
        hover = self.rect.collidepoint(mouse)
        bg = (90, 90, 90) if hover else (60, 60, 60)
        pygame.draw.rect(WIN, bg, self.rect, border_radius=10)
        pygame.draw.rect(WIN, (220, 220, 220), self.rect, 2, border_radius=10)
        label = FONT.render(self.text, True, (255, 255, 255))
        WIN.blit(label, label.get_rect(center=self.rect.center))

    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)

# ---------------- GAME HELPERS ----------------
def spawn_fox():
    side = random.choice(["left", "right", "top", "bottom"])
    if side == "left":
        return pygame.Rect(0, random.randint(0, HEIGHT - FOX_HEIGHT), FOX_WIDTH, FOX_HEIGHT)
    if side == "right":
        return pygame.Rect(WIDTH - FOX_WIDTH, random.randint(0, HEIGHT - FOX_HEIGHT), FOX_WIDTH, FOX_HEIGHT)
    if side == "top":
        return pygame.Rect(random.randint(0, WIDTH - FOX_WIDTH), 0, FOX_WIDTH, FOX_HEIGHT)
    return pygame.Rect(random.randint(0, WIDTH - FOX_WIDTH), HEIGHT - FOX_HEIGHT, FOX_WIDTH, FOX_HEIGHT)


def spawn_carrots():
    carrots = []
    for _ in range(TOTAL_CARROTS):
        x = random.randint(50, WIDTH - 50)
        y = random.randint(50, HEIGHT - 50)
        carrots.append(pygame.Rect(x, y, CARROT_SIZE, CARROT_SIZE))
    return carrots


def new_run():
    player = pygame.Rect(WIDTH // 2, HEIGHT // 2, PLAYER_WIDTH, PLAYER_HEIGHT)
    foxes = [spawn_fox()]
    carrots = spawn_carrots()
    lives = LIVES_START
    score = 0
    start_time = time.time()
    last_hit_time = 0
    return player, foxes, carrots, lives, score, start_time, last_hit_time

# ---------------- DRAWING ----------------
def draw_game(player, foxes, carrots, elapsed, lives, score):
    WIN.blit(BG, (0, 0))

    for carrot in carrots:
        pygame.draw.rect(WIN, "gold", carrot)

    for fox in foxes:
        pygame.draw.rect(WIN, "orange", fox)

    pygame.draw.rect(WIN, "red", player)

    WIN.blit(FONT.render(f"Time: {round(elapsed)}s", True, "white"), (10, 10))
    WIN.blit(FONT.render(f"Lives: {lives}", True, "red"), (10, 45))
    WIN.blit(FONT.render(f"Carrots: {score}/{TOTAL_CARROTS}", True, "gold"), (WIDTH - 220, 10))

    pygame.display.update()


def draw_menu(mouse, play_btn, how_btn, quit_btn):
    WIN.blit(MENU_BG, (0, 0))

    play_btn.draw(WIN)
    how_btn.draw(WIN)
    quit_btn.draw(WIN)
    pygame.display.update()


def draw_howto(mouse):
    WIN.blit(HOWTO_BG, (0, 0))
    draw_text_center("HOW TO PLAY", BIG_FONT, (255, 255, 255), 130)

    lines = [
        "Move with WASD or Arrow Keys",
        "Collect all golden carrots to win",
        "You start with 1 fox",
        "Each hit costs 1 life and spawns 1 fox",
        "You have 2 lives total",
        "ESC to pause",
    ]

    y = 230
    for line in lines:
        draw_text_center(line, FONT, (235, 235, 235), y)
        y += 40

    back = Button("Back", (WIDTH // 2, 580))
    back.draw(mouse)
    pygame.display.update()
    return back


def draw_pause(mouse):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    WIN.blit(overlay, (0, 0))

    draw_text_center("PAUSED", BIG_FONT, (255, 255, 255), 200)

    r = Button("Resume", (WIDTH // 2, 330))
    re = Button("Restart", (WIDTH // 2, 410))
    m = Button("Main Menu", (WIDTH // 2, 490))

    for b in (r, re, m): b.draw(mouse)
    pygame.display.update()
    return r, re, m


def end_screen(text):
    WIN.fill((0, 0, 0))
    msg = END_FONT.render(text, True, "white")
    WIN.blit(msg, msg.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
    pygame.display.update()
    pygame.time.delay(4000)

# ---------------- MAIN LOOP ----------------
def main():
    clock = pygame.time.Clock()
    state = MENU

    #create buttons
    play_btn = ImageButton(PLAY_IMG, (WIDTH // 2, 470))
    how_btn  = ImageButton(HOW_IMG,  (WIDTH // 2, 565))
    quit_btn = ImageButton(QUIT_IMG, (WIDTH // 2, 660))

    #start run
    player, foxes, carrots, lives, score, start_time, last_hit_time = new_run()
    elapsed = 0

    run = True
    while run:
        dt = clock.tick(FPS) / 1000.0
        mouse = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if state == PLAYING: state = PAUSED
                elif state == PAUSED: state = PLAYING
                elif state == HOWTO: state = MENU

            #menu clicking
            if state == MENU:
                if play_btn.clicked(event):
                    player, foxes, carrots, lives, score, start_time, last_hit_time = new_run()
                    state = PLAYING
                elif how_btn.clicked(event): state = HOWTO
                elif quit_btn.clicked(event): run = False

            #howto clicking
            elif state == HOWTO:
                b = draw_howto(mouse)
                if b.clicked(event): state = MENU

            #pause clicking
            elif state == PAUSED:
                r, re, m = draw_pause(mouse)
                if r.clicked(event): state = PLAYING
                elif re.clicked(event):
                    player, foxes, carrots, lives, score, start_time, last_hit_time = new_run()
                    state = PLAYING
                elif m.clicked(event): state = MENU

        if state == PLAYING:
            elapsed = time.time() - start_time

            keys = pygame.key.get_pressed()
            x = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
            y = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])

            move = pygame.math.Vector2(x, y)
            if move.length_squared() > 0:
                move = move.normalize() * PLAYER_SPEED * dt
                player.x += int(move.x)
                player.y += int(move.y)

            player.x = max(0, min(player.x, WIDTH - PLAYER_WIDTH))
            player.y = max(0, min(player.y, HEIGHT - PLAYER_HEIGHT))

            for fox in foxes:
                if fox.x < player.x: fox.x += FOX_SPEED * dt
                if fox.x > player.x: fox.x -= FOX_SPEED * dt
                if fox.y < player.y: fox.y += FOX_SPEED * dt
                if fox.y > player.y: fox.y -= FOX_SPEED * dt

                if fox.colliderect(player) and time.time() - last_hit_time > HIT_COOLDOWN:
                    last_hit_time = time.time()
                    lives -= 1
                    foxes.append(spawn_fox())
                    player.center = (WIDTH // 2, HEIGHT // 2)
                    pygame.time.delay(300)

            for c in carrots[:]:
                if player.colliderect(c):
                    carrots.remove(c)
                    score += 1

            if lives <= 0:
                draw_game(player, foxes, carrots, elapsed, lives, score)
                end_screen("GAME OVER")
                state = MENU

            elif score >= TOTAL_CARROTS:
                draw_game(player, foxes, carrots, elapsed, lives, score)
                end_screen("YOU WIN")
                state = MENU

            draw_game(player, foxes, carrots, elapsed, lives, score)

        elif state == MENU:
            draw_menu(mouse, play_btn, how_btn, quit_btn)
        elif state == HOWTO:
            draw_howto(mouse)
        elif state == PAUSED:
            draw_game(player, foxes, carrots, elapsed, lives, score)
            draw_pause(mouse)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()