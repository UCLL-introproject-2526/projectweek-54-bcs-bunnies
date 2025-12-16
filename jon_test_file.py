import pygame
import time
import random

# Initialize Pygame and Font
pygame.init()
pygame.font.init()

# --- 1. SETTINGS & DISPLAY ---
WIDTH, HEIGHT = 1280, 720
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Bunnies Beta V 1.0')

# Try to load BG, fallback to green if file is missing
try:
    BG = pygame.transform.scale(pygame.image.load("images/bg.png"), (WIDTH, HEIGHT))
except:
    BG = pygame.Surface((WIDTH, HEIGHT))
    BG.fill((34, 139, 34)) # Forest Green

# Constants
PLAYER_WIDTH, PLAYER_HEIGHT = 40, 60
PLAYER_SPEED = 500
FOX_WIDTH, FOX_HEIGHT = 50, 50
FOX_SPEED = 220
CARROT_SIZE = 25
FPS = 60

FONT = pygame.font.SysFont("comicsans", 30)
END_FONT = pygame.font.SysFont("comicsans", 80)

# --- 2. HELPER FUNCTIONS ---

def display_message(text):
    """Fills the screen and displays the end-game text for 7 seconds."""
    WIN.fill((0, 0, 0))
    msg = END_FONT.render(text, 1, "white")
    # Centers the text perfectly
    msg_rect = msg.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    WIN.blit(msg, msg_rect)
    pygame.display.update()
    pygame.time.delay(7000) # 7-second pause

def draw(player, elapsed_time, foxes, carrots, lives, score):
    """Draws all game elements to the screen."""
    WIN.blit(BG, (0, 0))
    
    # Draw Golden Carrots
    for carrot in carrots:
        pygame.draw.rect(WIN, "gold", carrot)

    # Draw Player (Bunny)
    pygame.draw.rect(WIN, "red", player)

    # Draw Foxes
    for fox in foxes:
        pygame.draw.rect(WIN, "orange", fox)

    # Draw UI
    time_text = FONT.render(f"Time: {round(elapsed_time)}s", 1, "white")
    lives_text = FONT.render(f"Lives: {lives}", 1, "red")
    score_text = FONT.render(f"Carrots: {score}/5", 1, "gold")

    WIN.blit(time_text, (10, 10))
    WIN.blit(lives_text, (10, 50))
    WIN.blit(score_text, (WIDTH - 200, 10))
    
    pygame.display.update()

# --- 3. MAIN GAME LOOP ---

def main():
    run = True
    player = pygame.Rect(WIDTH // 2, HEIGHT // 2, PLAYER_WIDTH, PLAYER_HEIGHT)
    clock = pygame.time.Clock()
    start_time = time.time()

    lives = 2
    score = 0
    
    # Enemies and Collectibles
    foxes = [pygame.Rect(100, 100, FOX_WIDTH, FOX_HEIGHT)]
    carrots = []
    for _ in range(5):
        x = random.randint(50, WIDTH - 50)
        y = random.randint(50, HEIGHT - 50)
        carrots.append(pygame.Rect(x, y, CARROT_SIZE, CARROT_SIZE))

    while run:
        dt = clock.tick(FPS) / 1000.0
        elapsed_time = time.time() - start_time

        # Event Queue
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                return

        # Player Movement Logic
        keys = pygame.key.get_pressed()
        x_input = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
        y_input = (keys[pygame.K_DOWN] or keys[pygame.K_s]) - (keys[pygame.K_UP] or keys[pygame.K_w])
        
        move = pygame.math.Vector2(x_input, y_input)
        if move.length_squared() > 0:
            move = move.normalize() * PLAYER_SPEED * dt
            player.x += int(move.x)
            player.y += int(move.y)

        # Boundary Clamping
        player.x = max(0, min(player.x, WIDTH - PLAYER_WIDTH))
        player.y = max(0, min(player.y, HEIGHT - PLAYER_HEIGHT))

        # Fox AI and Collision
        for fox in foxes:
            # Simple chase logic
            if fox.x < player.x: fox.x += FOX_SPEED * dt
            if fox.x > player.x: fox.x -= FOX_SPEED * dt
            if fox.y < player.y: fox.y += FOX_SPEED * dt
            if fox.y > player.y: fox.y -= FOX_SPEED * dt

            if fox.colliderect(player):
                lives -= 1
                # Spawn an additional fox at a random edge
                new_x = random.choice([0, WIDTH - FOX_WIDTH])
                new_y = random.randint(0, HEIGHT - FOX_HEIGHT)
                foxes.append(pygame.Rect(new_x, new_y, FOX_WIDTH, FOX_HEIGHT))
                
                # Reset Bunny to center to avoid instant multi-hits
                player.x, player.y = WIDTH // 2, HEIGHT // 2
                
                if lives > 0:
                    draw(player, elapsed_time, foxes, carrots, lives, score)
                    pygame.time.delay(500) # Brief pause after hit

        # Carrot Collection
        for carrot in carrots[:]:
            if player.colliderect(carrot):
                carrots.remove(carrot)
                score += 1

        # Win/Loss Checking
        if lives <= 0:
            draw(player, elapsed_time, foxes, carrots, lives, score)
            display_message("You lost bitch")
            run = False
        
        elif score >= 5:
            draw(player, elapsed_time, foxes, carrots, lives, score)
            display_message("You won champ")
            run = False

        if run:
            draw(player, elapsed_time, foxes, carrots, lives, score)

    pygame.quit()

if __name__ == "__main__":
    main()