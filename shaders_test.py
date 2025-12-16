import pygame
import time
import random
import pygame_shaders
pygame.font.init()

# Setting display
WIDTH, HEIGHT = 1000, 800

# Initialize pygame with OPENGL flag
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.OPENGL | pygame.DOUBLEBUF)
display = pygame.Surface((WIDTH, HEIGHT))

# IMPORTANT: Don't use set_colorkey on the main OpenGL surface
# display.set_colorkey((0, 0, 0))  # Remove or comment this line

pygame.display.set_caption('bunnies beta V 1.0')

# Initialize shader - make sure the file path is correct
try:
    screen_shader = pygame_shaders.Shader(size=(WIDTH, HEIGHT), display_size=(WIDTH, HEIGHT), 
                                          pos=(0, 0), fragment_path="shaders/fragment.glsl")
except Exception as e:
    print(f"Shader error: {e}")
    # Fallback to basic rendering
    screen_shader = None

BG = pygame.transform.scale(pygame.image.load("images/bg.png"), (WIDTH, HEIGHT))

PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60  # Fixed typo: HIGHT -> HEIGHT
PLAYER_VEL = 5

FONT = pygame.font.SysFont("comicsans", 30)

def draw(player, elapsed_time):
    # Clear display surface
    display.fill((0, 0, 0))  # Clear with black
    
    # Draw background
    display.blit(BG, (0, 0))
    
    # Draw player
    pygame.draw.rect(display, "red", player)
    
    # Draw text
    time_text = FONT.render(f"Time: {round(elapsed_time)}s", 1, "white")
    display.blit(time_text, (10, 10))
    
    # Apply shader effect if available
    if screen_shader:
        screen_shader.render(display)
    else:
        # Fallback: draw directly to screen (converted for OpenGL)
        # For OpenGL mode, we need to use textures
        tex = pygame_shaders.texture_from_surface(display)
        tex.draw((0, 0))
    
    pygame.display.flip()

def main():
    run = True
    
    # Setting a player
    player = pygame.Rect(
        WIDTH // 2 - PLAYER_WIDTH // 2,
        HEIGHT // 2 - PLAYER_HEIGHT // 2,
        PLAYER_WIDTH,
        PLAYER_HEIGHT
    )
    
    clock = pygame.time.Clock()
    start_time = time.time()
    elapsed_time = 0
    
    while run:
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
        
        draw(player, elapsed_time)
        clock.tick(60)  # Moved clock.tick inside the loop
    
    pygame.quit()

if __name__ == "__main__":
    main()