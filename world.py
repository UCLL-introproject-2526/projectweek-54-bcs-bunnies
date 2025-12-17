
import random
import math
import pygame
from settings import WIDTH, HEIGHT, BLOCK_SIZE, PORTAL_SIZE, FOX_WIDTH, FOX_HEIGHT

ADJECTIVES = ["Stinky", "Glorious", "Slippery", "Angry", "Cabbage-Scented", "Mildly Annoying", "Shiny", "Suspicious", "Fluffy", "Extreme"]
NOUNS = ["Armpit", "Basement", "Toilet", "Paradise", "Doom", "Garden", "Lair", "Swamp", "Elevator", "Buffet"]

def get_funny_name() -> str:
    return f"{random.choice(ADJECTIVES)} {random.choice(NOUNS)}"

room_data = {}

def generate_room(coords):
    if coords not in room_data:
        bg_colors = [(34, 139, 34), (101, 67, 33), (20, 80, 80), (107, 142, 35), (47, 79, 79)]
        theme = random.choice(["trees", "rocks", "blocks"])

        blocks = []
        safe_zone = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 150, 300, 300)

        # Boundary walls
        walls = [
            pygame.Rect(0, 0, WIDTH, 20),
            pygame.Rect(0, HEIGHT-20, WIDTH, 20),
            pygame.Rect(0, 0, 20, HEIGHT),
            pygame.Rect(WIDTH-20, 0, 20, HEIGHT),
        ]
        blocks.extend(walls)

        for _ in range(random.randint(8, 14)):
            bx = (random.randint(2, (WIDTH // BLOCK_SIZE) - 3)) * BLOCK_SIZE
            by = (random.randint(2, (HEIGHT // BLOCK_SIZE) - 3)) * BLOCK_SIZE
            block_rect = pygame.Rect(bx, by, BLOCK_SIZE, BLOCK_SIZE)
            if not block_rect.colliderect(safe_zone):
                blocks.append(block_rect)

        foxes = [pygame.Rect(random.randint(100, 300), random.randint(100, 600), FOX_WIDTH, FOX_HEIGHT)]
        carrots = [pygame.Rect(random.randint(100, 1100), random.randint(100, 600), 25, 25) for _ in range(random.randint(3, 6))]

        portals = {
            "top": pygame.Rect(WIDTH//2 - PORTAL_SIZE//2, 0, PORTAL_SIZE, 30),
            "bottom": pygame.Rect(WIDTH//2 - PORTAL_SIZE//2, HEIGHT-30, PORTAL_SIZE, 30),
            "left": pygame.Rect(0, HEIGHT//2 - PORTAL_SIZE//2, 30, PORTAL_SIZE),
            "right": pygame.Rect(WIDTH-30, HEIGHT//2 - PORTAL_SIZE//2, 30, PORTAL_SIZE),
        }

        room_data[coords] = {
            "blocks": blocks,
            "foxes": foxes,
            "carrots": carrots,
            "color": random.choice(bg_colors),
            "theme": theme,
            "portals": portals,
            "name": get_funny_name(),
        }
    return room_data[coords]

def move_with_collision(rect: pygame.Rect, blocks, dx: float, dy: float):
    rect.x += int(dx)
    for block in blocks:           
        if rect.colliderect(block):
            if dx > 0: rect.right = block.left
            if dx < 0: rect.left = block.right

    rect.y += int(dy)
    for block in blocks:
        if rect.colliderect(block):
            if dy > 0: rect.bottom = block.top
            if dy < 0: rect.top = block.bottom

def portal_transition(side: str, coords, player: pygame.Rect):
    x, y = coords
    if side == "top":
        coords = (x, y + 1); player.y = HEIGHT - 120
    elif side == "bottom":
        coords = (x, y - 1); player.y = 120
    elif side == "left":
        coords = (x - 1, y); player.x = WIDTH - 120
    elif side == "right":
        coords = (x + 1, y); player.x = 120
    return coords

def respawn_player(player, room, WIDTH, HEIGHT):
    while True:
        # Pick a random position inside the room
        new_x = random.randint(50, WIDTH - 50)
        new_y = random.randint(50, HEIGHT - 50)
        # Move the player rect to position
        player.center = (new_x, new_y)

        # Check collision with foxes
        collision = any(player.colliderect(fox) for fox in room["foxes"])

        if not collision:
            break 