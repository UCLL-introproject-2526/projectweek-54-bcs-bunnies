import pygame
import time
import random
import math

# Initialize Pygame
pygame.init()

# --- 1. SETTINGS ---
WIDTH, HEIGHT = 1280, 720
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Bunnies: The Quest for the Golden Cabbage')

# Constants
PLAYER_WIDTH, PLAYER_HEIGHT = 40, 50
PLAYER_SPEED = 450
FOX_WIDTH, FOX_HEIGHT = 50, 50
FOX_SPEED = 180 
BLOCK_SIZE = 80
PORTAL_SIZE = 70
FPS = 60

# Fonts
FONT = pygame.font.SysFont("comicsans", 30, bold=True)
END_FONT = pygame.font.SysFont("comicsans", 80, bold=True)

# --- 2. FUNNY NAME GENERATOR ---
ADJECTIVES = ["Stinky", "Glorious", "Slippery", "Angry", "Cabbage-Scented", "Mildly Annoying", "Shiny", "Suspicious", "Fluffy", "Extreme"]
NOUNS = ["Armpit", "Basement", "Toilet", "Paradise", "Doom", "Garden", "Lair", "Swamp", "Elevator", "Buffet"]

def get_funny_name():
    return f"{random.choice(ADJECTIVES)} {random.choice(NOUNS)}"

# --- 3. ROOM GENERATION ---
room_data = {}

def generate_room(coords):
    if coords not in room_data:
        bg_colors = [(34, 139, 34), (101, 67, 33), (20, 80, 80), (107, 142, 35), (47, 79, 79)]
        theme = random.choice(["trees", "rocks", "blocks"])
        
        blocks = []
        safe_zone = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 150, 300, 300)
        
        # Boundary Walls
        walls = [
            pygame.Rect(0, 0, WIDTH, 20),
            pygame.Rect(0, HEIGHT-20, WIDTH, 20),
            pygame.Rect(0, 0, 20, HEIGHT),
            pygame.Rect(WIDTH-20, 0, 20, HEIGHT)
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
            "right": pygame.Rect(WIDTH-30, HEIGHT//2 - PORTAL_SIZE//2, 30, PORTAL_SIZE)
        }

        room_data[coords] = {
            "blocks": blocks, 
            "foxes": foxes, 
            "carrots": carrots, 
            "color": random.choice(bg_colors),
            "theme": theme,
            "portals": portals,
            "name": get_funny_name() # Assign a funny name!
        }
    return room_data[coords]

# --- 4. PHYSICS ---
def move_with_collision(rect, blocks, dx, dy):
    rect.x += dx
    for block in blocks:
        if rect.colliderect(block):
            if dx > 0: rect.right = block.left
            if dx < 0: rect.left = block.right
    rect.y += dy
    for block in blocks:
        if rect.colliderect(block):
            if dy > 0: rect.bottom = block.top
            if dy < 0: rect.top = block.bottom

def main():
    run = True
    clock = pygame.time.Clock()
    player = pygame.Rect(WIDTH//2, HEIGHT//2, PLAYER_WIDTH, PLAYER_HEIGHT)
    current_coords = (0, 0)
    score = 0
    lives = 3
    game_state = "PLAYING"
    
    # Pulse animation variable
    pulse_timer = 0

    while run:
        dt = clock.tick(FPS) / 1000.0
        pulse_timer += dt * 5 # Control pulse speed
        room = generate_room(current_coords)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        if game_state == "PLAYING":
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0
            if keys[pygame.K_a] or keys[pygame.K_LEFT]: dx = -PLAYER_SPEED * dt
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx = PLAYER_SPEED * dt
            if keys[pygame.K_w] or keys[pygame.K_UP]: dy = -PLAYER_SPEED * dt
            if keys[pygame.K_s] or keys[pygame.K_DOWN]: dy = PLAYER_SPEED * dt
            
            move_with_collision(player, room["blocks"], dx, dy)

            # Portal Logic
            for side, p_rect in room["portals"].items():
                if player.colliderect(p_rect):
                    if side == "top":
                        current_coords = (current_coords[0], current_coords[1] + 1)
                        player.y = HEIGHT - 120
                    elif side == "bottom":
                        current_coords = (current_coords[0], current_coords[1] - 1)
                        player.y = 120
                    elif side == "left":
                        current_coords = (current_coords[0] - 1, current_coords[1])
                        player.x = WIDTH - 120
                    elif side == "right":
                        current_coords = (current_coords[0] + 1, current_coords[1])
                        player.x = 120

            # Fox AI
            for fox in room["foxes"]:
                fdx = (FOX_SPEED * dt) if fox.x < player.x else (-FOX_SPEED * dt)
                fdy = (FOX_SPEED * dt) if fox.y < player.y else (-FOX_SPEED * dt)
                move_with_collision(fox, room["blocks"], fdx, fdy)
                
                if fox.colliderect(player):
                    lives -= 1
                    new_fox = pygame.Rect(random.randint(100, 300), random.randint(100, 300), FOX_WIDTH, FOX_HEIGHT)
                    room["foxes"].append(new_fox)
                    player.center = (WIDTH//2, HEIGHT//2)
                    if lives <= 0: game_state = "LOST"

            # Score
            for carrot in room["carrots"][:]:
                if player.colliderect(carrot):
                    room["carrots"].remove(carrot)
                    score += 1
                    if score >= 15: game_state = "WON"

        # --- DRAWING ---
        WIN.fill(room["color"])
        
        # Pulse Calculation (Shiny Portals)
        pulse_val = (math.sin(pulse_timer) + 1) / 2 # Normalize between 0 and 1
        glow_color = (0, 200 + int(55 * pulse_val), 200 + int(55 * pulse_val))

        for p_rect in room["portals"].values():
            # Draw glow ring
            glow_rect = p_rect.inflate(10 * pulse_val, 10 * pulse_val)
            pygame.draw.ellipse(WIN, (255, 255, 255), glow_rect) # Outer white glow
            pygame.draw.ellipse(WIN, glow_color, p_rect) # Inner pulsing cyan

        # Nature Objects
        for block in room["blocks"]:
            if block.width == WIDTH or block.height == HEIGHT:
                pygame.draw.rect(WIN, (30, 30, 30), block)
            elif room["theme"] == "trees":
                pygame.draw.rect(WIN, (80, 50, 20), (block.centerx - 10, block.centery, 20, 40))
                pygame.draw.circle(WIN, (20, 100, 20), (block.centerx, block.centery), 40)
            elif room["theme"] == "rocks":
                pygame.draw.rect(WIN, (100, 100, 100), block, border_radius=20)
            else:
                pygame.draw.rect(WIN, (139, 69, 19), block)
            
        for carrot in room["carrots"]:
            pygame.draw.circle(WIN, (255, 165, 0), carrot.center, 12)

        pygame.draw.rect(WIN, (255, 255, 255), player) 
        for fox in room["foxes"]:
            pygame.draw.rect(WIN, (255, 50, 50), fox)

        # UI with Funny Name
        ui_text = FONT.render(f"Lives: {lives} | Score: {score}/15 | Location: {room['name']}", True, (255, 255, 255))
        WIN.blit(ui_text, (30, 30))

        if game_state != "PLAYING":
            overlay = pygame.Surface((WIDTH, HEIGHT)); overlay.set_alpha(200); overlay.fill((0, 0, 0))
            WIN.blit(overlay, (0, 0))
            text = "YOU LOST LIL BRO" if game_state == "LOST" else "YOU WON CHAMP"
            msg = END_FONT.render(text, True, (255, 255, 255))
            WIN.blit(msg, msg.get_rect(center=(WIDTH//2, HEIGHT//2)))

        pygame.display.update()
    pygame.quit()

if __name__ == "__main__":
    main()