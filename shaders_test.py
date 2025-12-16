import pygame
import time
import random
import pygame_shaders
pygame.font.init()

#setting display
WIDTH,HEIGHT= 1000,800
screen = pygame.display.set_mode((WIDTH,HEIGHT),pygame.OPENGL )
display=pygame.Surface(WIDTH,HEIGHT)
display.set_colorkey((0,0,0))
pygame.display.set_caption('bunnies beta V 1.0')

screen_shader = pygame_shaders.Shader((WIDTH,HEIGHT),(WIDTH,HEIGHT),(0,0),"shaders\vertex.glsl","shaders\fragment.glsl")

BG =pygame.transform.scale(pygame.image.load("images/bg.png"), (WIDTH, HEIGHT))

PLAYER_WIDTH = 40
PLAYER_HIGHT = 60
PLAYER_VEL = 5

FONT = pygame.font.SysFont("comicsans",30)

def draw (player, elapsed_time):
    screen.blit(BG,(0,0))
    pygame.draw.rect(WIN,"red", player)

    time_text = FONT.render(f"Time: {round(elapsed_time)}s",1,"white")
    screen.blit(time_text, (10,10))

    pygame.display.update()
#defining gameplay loop
def main():
    run = True

# setting a player
    player = pygame.Rect(    WIDTH // 2 - PLAYER_WIDTH // 2,HEIGHT // 2 - PLAYER_HIGHT // 2,PLAYER_WIDTH,PLAYER_HIGHT)

    clock = pygame.time.Clock()

    start_time = time.time()
    elapsed_time = 0

    #quit game using X
    while run:
        pygame_shaders.clear((0,0,0))
        clock.tick(80)
        elapsed_time = time.time() - start_time
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
    # moving the player 
        keys = pygame.key.get_pressed() 
        if keys[pygame.K_LEFT] and player.x - PLAYER_VEL>=0:
            player.x -= PLAYER_VEL
        if keys[pygame.K_RIGHT] and player.x + PLAYER_VEL + player.width <= WIDTH:
            player.x += PLAYER_VEL  
        if keys[pygame.K_UP] and player.y - PLAYER_VEL >= 0:
            player.y -= PLAYER_VEL   
        if keys[pygame.K_DOWN] and player.y + PLAYER_VEL + player.height <= HEIGHT:
            player.y += PLAYER_VEL           
        draw(player, elapsed_time)    
    pygame.quit()

if __name__ == "__main__":
    main()
