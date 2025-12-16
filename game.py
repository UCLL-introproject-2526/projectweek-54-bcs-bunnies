import pygame
import time
import random
import math
pygame.font.init()

#setting display
WIDTH,HEIGHT= 1280,720
WIN = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption('bunnies beta V 1.0')

BG = pygame.transform.scale(pygame.image.load("images/bg.png"), (WIDTH, HEIGHT))

#saving the player characters width and height
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60
# Using pixels per second for frame-indepent movement
PLAYER_SPEED = 500

FONT = pygame.font.SysFont("comicsans", 30)

#function making sure that at any given moment any changing
#element actually changes rather than overlapping with "past" versions of itself
def draw (player, elapsed_time):
    #setting the background
    WIN.blit(BG,(0,0))
    #creating the player character
    pygame.draw.rect(WIN,"red", player)
    #timer specifications
    time_text = FONT.render(f"Time: {round(elapsed_time)}s",1,"white")

    WIN.blit(time_text, (10,10))
    pygame.display.update()


#defining gameplay loop
def main():
    run = True

# setting a player
    player = pygame.Rect(    WIDTH // 2 - PLAYER_WIDTH // 2,HEIGHT // 2 - PLAYER_HEIGHT // 2,PLAYER_WIDTH,PLAYER_HEIGHT)

    clock = pygame.time.Clock()

    start_time = time.time()
    elapsed_time = 0

    #quit game using X
    while run:
        dt = clock.tick(80) / 1000.0
        elapsed_time = time.time() - start_time


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break


    # moving the player (Arrow keys + WASD combined)

        keys = pygame.key.get_pressed() 

        x_input = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
        y_input = (keys[pygame.K_DOWN] or keys[pygame.K_s]) - (keys[pygame.K_UP] or keys[pygame.K_w])

        move = pygame.math.Vector2(x_input, y_input)

        if move.length_squared() > 0:
            move = move.normalize() * PLAYER_SPEED * dt
            player.x += int(move.x)
            player.y += int(move.y)

        # Clamp to window bounds
        player.x = max(0, min(player.x, WIDTH - PLAYER_WIDTH))
        player.y = max(0, min(player.y, HEIGHT - PLAYER_HEIGHT))

        draw(player, elapsed_time)    
    
    pygame.quit()

if __name__ == "__main__":
    main()