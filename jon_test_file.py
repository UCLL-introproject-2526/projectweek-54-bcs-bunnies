import pygame
import time
import random

# Initialize Pygame
pygame.init()

# --- 1. SETTINGS ---
WIDTH, HEIGHT = 1280, 720
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Bunnies: Forest Dungeon')

# Constants
PLAYER_WIDTH, PLAYER_HEIGHT = 40, 50
PLAYER_SPEED = 450
FOX_WIDTH, FOX_HEIGHT = 50, 50
FOX_SPEED = 400
CARROT_SIZE = 15
FPS = 60
BLOCK_SIZE = 50

# Fonts
FONT = pygame.font.SysFont("comicsans", 30, bold=True)
END_FONT = pygame.font.SysFont("comicsans", 80, bold=True)

# --- 2. ROOM GENERATION ---
room_data = {}

def generate_room(coords):
    if coords not in room_data:
        tint = (random.randint(20, 50), random.randint(80, 130), random.randint(20, 50))
        
        blocks = []
        # Safe Zone for spawning
        safe_zone = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 150, 300, 300)
        
        for _ in range(random.randint(6, 15)):
            bx = (random.randint(1, (WIDTH // BLOCK_SIZE) - 2)) * BLOCK_SIZE
            by = (random.randint(1, (HEIGHT // BLOCK_SIZE) - 2)) * BLOCK_SIZE
            block_rect = pygame.Rect(bx, by, BLOCK_SIZE, BLOCK_SIZE)
            
            if not block_rect.colliderect(safe_zone):
                blocks.append(block_rect)

        # Starts with exactly 1 fox
        foxes = [pygame.Rect(random.randint(100, 300), random.randint(100, 600), FOX_WIDTH, FOX_HEIGHT)]

        carrots = []
        for _ in range(random.randint(3, 6)):
            c_rect = pygame.Rect(random.randint(100, 1100), random.randint(100, 600), 25, 25)
            carrots.append(c_rect)

        room_data[coords] = {"blocks": blocks, "foxes": foxes, "carrots": carrots, "color": tint}
    return room_data[coords]

# --- 3. PHYSICS ---
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

# --- 4. MAIN GAME ---
def main():
    run = True
    clock = pygame.time.Clock()
    player = pygame.Rect(WIDTH//2, HEIGHT//2, PLAYER_WIDTH, PLAYER_HEIGHT)
    current_coords = (0, 0)
    score = 0
    lives = 3
    game_state = "PLAYING" # Can be "PLAYING", "WON", "LOST"

    while run:
        dt = clock.tick(FPS) / 1000.0
        room = generate_room(current_coords)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        if game_state == "PLAYING":
            # Movement
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0
            if keys[pygame.K_a] or keys[pygame.K_LEFT]: dx = -PLAYER_SPEED * dt
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx = PLAYER_SPEED * dt
            if keys[pygame.K_w] or keys[pygame.K_UP]: dy = -PLAYER_SPEED * dt
            if keys[pygame.K_s] or keys[pygame.K_DOWN]: dy = PLAYER_SPEED * dt
            
            move_with_collision(player, room["blocks"], dx, dy)

            # Room Swapping
            if player.x > WIDTH:
                current_coords = (current_coords[0] + 1, current_coords[1])
                player.x = 20
            elif player.x < -PLAYER_WIDTH:
                current_coords = (current_coords[0] - 1, current_coords[1])
                player.x = WIDTH - 20
            elif player.y > HEIGHT:
                current_coords = (current_coords[0], current_coords[1] - 1)
                player.y = 20
            elif player.y < -PLAYER_HEIGHT:
                current_coords = (current_coords[0], current_coords[1] + 1)
                player.y = HEIGHT - 20

            # Fox AI
            for fox in room["foxes"]:
                fdx = (FOX_SPEED * dt) if fox.x < player.x else (-FOX_SPEED * dt)
                fdy = (FOX_SPEED * dt) if fox.y < player.y else (-FOX_SPEED * dt)
                move_with_collision(fox, room["blocks"], fdx, fdy)
                
                if fox.colliderect(player):
                    lives -= 1
                    # SPAWN ANOTHER FOX
                    new_fox = pygame.Rect(random.randint(50, 200), random.randint(50, 200), FOX_WIDTH, FOX_HEIGHT)
                    room["foxes"].append(new_fox)
                    
                    player.center = (WIDTH//2, HEIGHT//2)
                    if lives <= 0:
                        game_state = "LOST"

            # Score logic
            for carrot in room["carrots"][:]:
                if player.colliderect(carrot):
                    room["carrots"].remove(carrot)
                    score += 1
                    if score >= 15: # Win condition
                        game_state = "WON"

        # --- DRAWING ---
        WIN.fill(room["color"])
        
        for block in room["blocks"]:
            pygame.draw.rect(WIN, (101, 67, 33), block)
            pygame.draw.rect(WIN, (60, 40, 20), block, 3) 
            
        for carrot in room["carrots"]:
            pygame.draw.circle(WIN, (255, 165, 0), carrot.center, 12)

        pygame.draw.rect(WIN, (255, 0, 0), player) 
        for fox in room["foxes"]:
            pygame.draw.rect(WIN, (255, 140, 0), fox)

        # UI
        ui_text = FONT.render(f"Lives: {lives} | Carrots: {score}/15 | Room: {current_coords}", True, (255, 255, 255))
        WIN.blit(ui_text, (20, 20))

        # End Game Messages
        if game_state != "PLAYING":
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            WIN.blit(overlay, (0, 0))
            
            text = "YOU LOST LIL BRO" if game_state == "LOST" else "YOU WON CHAMP"
            color = (255, 0, 0) if game_state == "LOST" else (0, 255, 0)
            
            msg = END_FONT.render(text, True, color)
            msg_rect = msg.get_rect(center=(WIDTH//2, HEIGHT//2))
            WIN.blit(msg, msg_rect)

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()