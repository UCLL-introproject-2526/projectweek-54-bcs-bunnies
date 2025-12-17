import random
import pygame
from settings import WIDTH, HEIGHT, BLOCK_SIZE, PORTAL_SIZE, FOX_WIDTH, FOX_HEIGHT

ADJECTIVES = ["Stinky", "Glorious", "Slippery", "Angry", "Cabbage-Scented",
              "Mildly Annoying", "Shiny", "Suspicious", "Fluffy", "Extreme"]
NOUNS = ["Armpit", "Basement", "Toilet", "Paradise",
         "Doom", "Garden", "Lair", "Swamp", "Elevator", "Buffet"]


def get_funny_name() -> str:
    return f"{random.choice(ADJECTIVES)} {random.choice(NOUNS)}"


room_data = {}


def reset_world():
    room_data.clear()


def safe_load_png(path: str):
    try:
        return pygame.image.load(path).convert_alpha()
    except:
        return None


def scale_to_max(img: pygame.Surface, max_w: int, max_h: int) -> pygame.Surface:
    w, h = img.get_size()
    if w == 0 or h == 0:
        return img
    scale = min(max_w / w, max_h / h)
    new_size = (max(1, int(w * scale)), max(1, int(h * scale)))
    return pygame.transform.smoothscale(img, new_size)


def make_obstacle(img: pygame.Surface, x: int, y: int, kind: str):
    draw_rect = img.get_rect(topleft=(x, y))

    if kind == "tree":
        cw = int(draw_rect.width * 0.55)
        ch = int(draw_rect.height * 0.35)
        cx = draw_rect.centerx - cw // 2
        cy = draw_rect.bottom - ch
        coll = pygame.Rect(cx, cy, cw, ch)
    else:
        cw = int(draw_rect.width * 0.70)
        ch = int(draw_rect.height * 0.45)
        cx = draw_rect.centerx - cw // 2
        cy = draw_rect.bottom - ch
        coll = pygame.Rect(cx, cy, cw, ch)

    return {"img": img, "draw_rect": draw_rect, "coll_rect": coll, "kind": kind}


def theme_index(coords):
    x, y = coords
    return abs(x * 31 + y * 17) % 3  # 0..2


def generate_room(coords):
    if coords not in room_data:
        bg_colors = [(34, 139, 34), (101, 67, 33), (20, 80, 80),
                     (107, 142, 35), (47, 79, 79)]
        theme = random.choice(["trees", "rocks", "blocks"])

        blocks = []
        obstacles = []
        traps = []  # NEW

        safe_zone = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 150, 300, 300)

        # Boundary walls
        walls = [
            pygame.Rect(0, 0, WIDTH, 20),
            pygame.Rect(0, HEIGHT-20, WIDTH, 20),
            pygame.Rect(0, 0, 20, HEIGHT),
            pygame.Rect(WIDTH-20, 0, 20, HEIGHT),
        ]
        blocks.extend(walls)

        # Random block obstacles (existing)
        for _ in range(random.randint(8, 14)):
            bx = (random.randint(2, (WIDTH // BLOCK_SIZE) - 3)) * BLOCK_SIZE
            by = (random.randint(2, (HEIGHT // BLOCK_SIZE) - 3)) * BLOCK_SIZE
            block_rect = pygame.Rect(bx, by, BLOCK_SIZE, BLOCK_SIZE)
            if not block_rect.colliderect(safe_zone):
                blocks.append(block_rect)

        foxes = [pygame.Rect(random.randint(100, 300),
                             random.randint(100, 600), FOX_WIDTH, FOX_HEIGHT)]


        carrot_w, carrot_h = 32, 32  # <-- edit to your image's width/height
        carrots = [pygame.Rect(random.randint(100, 1100), random.randint(
        100, 600), 16, 16) for _ in range(random.randint(3, 6))]  # <-- match scaled size

        portals = {
            "top": pygame.Rect(WIDTH//2 - PORTAL_SIZE//2, 0, PORTAL_SIZE, 30),
            "bottom": pygame.Rect(WIDTH//2 - PORTAL_SIZE//2, HEIGHT-30, PORTAL_SIZE, 30),
            "left": pygame.Rect(0, HEIGHT//2 - PORTAL_SIZE//2, 30, PORTAL_SIZE),
            "right": pygame.Rect(WIDTH-30, HEIGHT//2 - PORTAL_SIZE//2, 30, PORTAL_SIZE),
        }

        # --- Image obstacles (trees/bushes) ---
        idx = theme_index(coords)
        tree_img = safe_load_png(f"images/tree_sheet_room{idx+1}.png")
        bush_img = safe_load_png(f"images/bush_sheet_room{idx+1}.png")

        if tree_img is None:
            tree_img = pygame.Surface((96, 96), pygame.SRCALPHA)
            tree_img.fill((40, 140, 40))
        if bush_img is None:
            bush_img = pygame.Surface((80, 80), pygame.SRCALPHA)
            bush_img.fill((20, 110, 20))

        tree_scaled = scale_to_max(tree_img, max_w=110, max_h=110)
        bush_scaled = scale_to_max(bush_img, max_w=85,  max_h=85)

        def place(kind: str, img_scaled: pygame.Surface, count: int):
            placed = 0
            tries = 0
            while placed < count and tries < 500:
                tries += 1
                x = random.randint(60, WIDTH - 60 - img_scaled.get_width())
                y = random.randint(120, HEIGHT - 80 - img_scaled.get_height())

                ob = make_obstacle(img_scaled, x, y, kind)
                coll = ob["coll_rect"]

                if coll.colliderect(safe_zone):
                    continue
                if any(coll.colliderect(p) for p in portals.values()):
                    continue
                if any(coll.colliderect(b) for b in blocks):
                    continue
                if any(coll.colliderect(o["coll_rect"]) for o in obstacles):
                    continue

                obstacles.append(ob)
                blocks.append(coll)
                placed += 1

        place("tree", tree_scaled, 2)
        place("bush", bush_scaled, 3)

        # --- NEW: traps (red circles) ---
        # These are hazards, NOT walls, so do NOT add them to blocks.
        for _ in range(random.randint(2, 5)):
            tries = 0
            while tries < 200:
                tries += 1
                tx = random.randint(80, WIDTH - 80)
                ty = random.randint(120, HEIGHT - 80)
                tr = pygame.Rect(tx - 20, ty - 20, 40, 40)

                if tr.colliderect(safe_zone):
                    continue
                if any(tr.colliderect(p) for p in portals.values()):
                    continue
                if any(tr.colliderect(b) for b in blocks):
                    continue
                if any(tr.colliderect(c) for c in carrots):
                    continue
                if any(tr.colliderect(f) for f in foxes):
                    continue

                traps.append(tr)
                break

        room_data[coords] = {
            "blocks": blocks,
            "obstacles": obstacles,
            "traps": traps,        # NEW
            "foxes": foxes,
            "carrots": carrots,
            "color": random.choice(bg_colors),
            "theme": theme,
            "portals": portals,
            "name": get_funny_name(),
            "fox_frames": [0] * len(foxes),  # <-- add here
            "fox_directions": [1] * len(foxes),
            "fox_paths": [[] for _ in foxes],
            
        }
    return room_data[coords]


def move_with_collision(rect: pygame.Rect, blocks, dx: float, dy: float):
    rect.x += int(dx)
    for block in blocks:
        if rect.colliderect(block):
            if dx > 0:
                rect.right = block.left
            if dx < 0:
                rect.left = block.right

    rect.y += int(dy)
    for block in blocks:
        if rect.colliderect(block):
            if dy > 0:
                rect.bottom = block.top
            if dy < 0:
                rect.top = block.bottom


def portal_transition(side: str, coords, player: pygame.Rect):
    x, y = coords
    if side == "top":
        coords = (x, y + 1)
        player.y = HEIGHT - 120
    elif side == "bottom":
        coords = (x, y - 1)
        player.y = 120
    elif side == "left":
        coords = (x - 1, y)
        player.x = WIDTH - 120
    elif side == "right":
        coords = (x + 1, y)
        player.x = 120
    return coords
