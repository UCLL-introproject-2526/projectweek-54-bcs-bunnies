import pygame
import time
import random
pygame.font.init()

# Setting display
WIDTH, HEIGHT = 1000, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('bunnies beta V 1.0')

BG = pygame.transform.scale(pygame.image.load("images/bg.png"), (WIDTH, HEIGHT))

PLAYER_WIDTH = 40
PLAYER_HIGHT = 60
PLAYER_VEL = 5

FONT = pygame.font.SysFont("comicsans", 30)

FOX_WIDTH = 40
FOX_HEIGHT = 40
FOX_VEL = 1

MAX_FOXES = 6          # Maximum number of foxes before game over
FOX_RESET_TIME = 2     # Seconds without touching a fox before reset to 1

def draw(player, foxes, elapsed_time):
    WIN.blit(BG, (0, 0))
    pygame.draw.rect(WIN, "red", player)

    # Draw every fox on the screen
    for fox in foxes:
        pygame.draw.rect(WIN, "orange", fox)

    time_text = FONT.render(f"Time: {round(elapsed_time)}s", 1, "white")
    WIN.blit(time_text, (10, 10))

    pygame.display.update()

# Creates a fox at a random position on the screen
def spawn_fox():
    x = random.randint(0, WIDTH - FOX_WIDTH)
    y = random.randint(0, HEIGHT - FOX_HEIGHT)
    return pygame.Rect(x, y, FOX_WIDTH, FOX_HEIGHT)

# Defining gameplay loop
def main():

    foxes = []                 # List that stores all active fox enemies
    foxes.append(spawn_fox())  # Spawn the first fox when the game starts

    run = True

    # Setting a player
    player = pygame.Rect(WIDTH // 2 - PLAYER_WIDTH // 2,
                         HEIGHT // 2 - PLAYER_HIGHT // 2,
                         PLAYER_WIDTH, PLAYER_HIGHT)

    clock = pygame.time.Clock()

    start_time = time.time()
    elapsed_time = 0

    last_fox_touch_time = time.time()  # Time of the last fox collision

    # Quit game using X
    while run:
        clock.tick(130)
        elapsed_time = time.time() - start_time
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        # Moving the player 
        keys = pygame.key.get_pressed() 
        if keys[pygame.K_LEFT] and player.x - PLAYER_VEL >= 0:
            player.x -= PLAYER_VEL
        if keys[pygame.K_RIGHT] and player.x + PLAYER_VEL + player.width <= WIDTH:
            player.x += PLAYER_VEL  
        if keys[pygame.K_UP] and player.y - PLAYER_VEL >= 0:
            player.y -= PLAYER_VEL   
        if keys[pygame.K_DOWN] and player.y + PLAYER_VEL + player.height <= HEIGHT:
            player.y += PLAYER_VEL     

        # Move foxes to chase the player
        for fox in foxes:
            if fox.x < player.x:
                fox.x += FOX_VEL
            if fox.x > player.x:
                fox.x -= FOX_VEL
            if fox.y < player.y:
                fox.y += FOX_VEL
            if fox.y > player.y:
                fox.y -= FOX_VEL

        # Fox collision and spawning logic with max and game over
        for fox in foxes[:]:
            if player.colliderect(fox):
                last_fox_touch_time = time.time()   # Update last collision time

                if len(foxes) < MAX_FOXES:
                    # Spawn 2 new foxes only if total is under maximum foxes
                    foxes.append(spawn_fox())
                    foxes.append(spawn_fox())
                    foxes.remove(fox)
                else:
                    # If already reached maximum no foxes, end the game
                    print("GAME OVER - Bunny got caught")
                    run = False
                    break

        # Reset foxes if no collision occurs
        if time.time() - last_fox_touch_time >= FOX_RESET_TIME:
            foxes.clear()
            foxes.append(spawn_fox())  # Leave only 1 fox
            last_fox_touch_time = time.time()  # Reset timer

        draw(player, foxes, elapsed_time)    

    pygame.quit()

if __name__ == "__main__":
    main()
