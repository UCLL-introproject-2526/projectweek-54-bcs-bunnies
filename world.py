import random
import pygame
import os
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


# --- ADD THIS AT THE TOP OF world.py ---
import os

# ... (keep your existing imports and helper functions like safe_load_png, scale_to_max, make_obstacle) ...

def generate_room(coords):
    if coords not in room_data:
        # 1. SETUP: Default values
        bg_colors = [(34, 139, 34), (101, 67, 33), (20, 80, 80)]
        
        # 2. PICK THEME & LOAD FOLDER IMAGES
        theme_folders = ["grassanddirt", "mudandgloomy", "meadow"]
        selected_theme = random.choice(theme_folders)
        
        # FIX: Variable name changed from theme_paths to theme_path to match usages below
        theme_path = os.path.join("images", selected_theme)

        bg_image = None
        asset_images = []

        # Scan the chosen folder
        if os.path.exists(theme_path):
            for filename in os.listdir(theme_path):
                if filename.endswith(".png"):
                    full_path = os.path.join(theme_path, filename)
                    img = safe_load_png(full_path)
                    
                    if img:
                        if filename.endswith("_bg.png"):
                            # It's a background
                            bg_image = pygame.transform.scale(img, (WIDTH, HEIGHT))
                        else:
                            # --- SCALING LOGIC START ---
                            fname_lower = filename.lower()
                            
                            if "tree" in fname_lower:
                                # MAKE TREES BIGGER
                                img = scale_to_max(img, max_w=180, max_h=180)
                            elif "rock" in fname_lower or "stone" in fname_lower:
                                # MAKE ROCKS SMALLER
                                img = scale_to_max(img, max_w=60, max_h=60)
                            else:
                                # BUSHES AND OTHERS
                                img = scale_to_max(img, max_w=80, max_h=80)
                            # --- SCALING LOGIC END ---
                            
                            asset_images.append(img)
        
        # Fallback if no background found
        if not bg_image:
            bg_image = pygame.Surface((WIDTH, HEIGHT))
            bg_image.fill((34, 139, 34))
        
        bg_color = random.choice(bg_colors)

        # 3. SETUP ROOM ESSENTIALS
        blocks = []
        obstacles = []
        traps = []
        
        safe_zone = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 150, 300, 300)

        # Boundary walls
        walls = [
            pygame.Rect(0, 0, WIDTH, 20),
            pygame.Rect(0, HEIGHT-20, WIDTH, 20),
            pygame.Rect(0, 0, 20, HEIGHT),
            pygame.Rect(WIDTH-20, 0, 20, HEIGHT),
        ]
        blocks.extend(walls)

        portals = {
            "top": pygame.Rect(WIDTH//2 - PORTAL_SIZE//2, 0, PORTAL_SIZE, 30),
            "bottom": pygame.Rect(WIDTH//2 - PORTAL_SIZE//2, HEIGHT-30, PORTAL_SIZE, 30),
            "left": pygame.Rect(0, HEIGHT//2 - PORTAL_SIZE//2, 30, PORTAL_SIZE),
            "right": pygame.Rect(WIDTH-30, HEIGHT//2 - PORTAL_SIZE//2, 30, PORTAL_SIZE),
        }

        # 4. GENERATE OBSTACLES
        # Random generic blocks (These are the brown squares you see!)
        # If you ONLY want pictures, you can comment this loop out.
        for _ in range(random.randint(4, 8)):
            bx = (random.randint(2, (WIDTH // BLOCK_SIZE) - 3)) * BLOCK_SIZE
            by = (random.randint(2, (HEIGHT // BLOCK_SIZE) - 3)) * BLOCK_SIZE
            block_rect = pygame.Rect(bx, by, BLOCK_SIZE, BLOCK_SIZE)
            
            if not block_rect.colliderect(safe_zone) and not any(block_rect.colliderect(p) for p in portals.values()):
                blocks.append(block_rect)

        # Place the picture assets
        if asset_images:
            for _ in range(random.randint(5, 10)):
                img = random.choice(asset_images)
                
                for attempt in range(100):
                    x = random.randint(60, WIDTH - 60 - img.get_width())
                    y = random.randint(120, HEIGHT - 80 - img.get_height())
                    
                    ob = make_obstacle(img, x, y, "tree")
                    coll = ob["coll_rect"]

                    if coll.colliderect(safe_zone): continue
                    if any(coll.colliderect(p) for p in portals.values()): continue
                    if any(coll.colliderect(b) for b in blocks): continue
                    if any(coll.colliderect(o["coll_rect"]) for o in obstacles): continue
                    
                    obstacles.append(ob)
                    blocks.append(coll)
                    break 

        # 5. ENTITIES
        foxes = [pygame.Rect(random.randint(100, 300), random.randint(100, 600), FOX_WIDTH, FOX_HEIGHT)]
        
        carrots = []
        tries = 0
        while len(carrots) < random.randint(3, 6) and tries < 400:
            tries += 1
            cx = random.randint(80, WIDTH - 80)
            cy = random.randint(120, HEIGHT - 80)
            carrot = pygame.Rect(cx, cy, 16, 16)

            if carrot.colliderect(safe_zone): continue
            if any(carrot.colliderect(p) for p in portals.values()): continue
            if any(carrot.colliderect(b) for b in blocks): continue
            if any(carrot.colliderect(o["coll_rect"]) for o in obstacles): continue
            if any(carrot.colliderect(f) for f in foxes): continue
            if any(carrot.colliderect(c) for c in carrots): continue

            carrots.append(carrot)

        # Traps
        for _ in range(random.randint(2, 5)):
            tries = 0
            while tries < 200:
                tries += 1
                tx = random.randint(80, WIDTH - 80)
                ty = random.randint(120, HEIGHT - 80)
                tr = pygame.Rect(tx - 20, ty - 20, 40, 40)

                if tr.colliderect(safe_zone): continue
                if any(tr.colliderect(p) for p in portals.values()): continue
                if any(tr.colliderect(b) for b in blocks): continue
                if any(tr.colliderect(c) for c in carrots): continue
                if any(tr.colliderect(f) for f in foxes): continue

                traps.append(tr)
                break

        # 6. SAVE DATA
        room_data[coords] = {
            "blocks": blocks,
            "obstacles": obstacles,
            "traps": traps,
            "foxes": foxes,
            "carrots": carrots,
            "color": bg_color,
            "bg_image": bg_image,
            "theme": selected_theme,
            "portals": portals,
            "name": get_funny_name(),
            "fox_frames": [0] * len(foxes),
            "fox_directions": [1] * len(foxes),
            "fox_paths": [[] for _ in foxes],
            "fox_anim_timer": [0.0] * len(foxes),
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
