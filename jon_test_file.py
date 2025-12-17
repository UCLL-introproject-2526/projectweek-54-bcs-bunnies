import pygame
import time
import random
import math

# Initialize Pygame
pygame.init()

# --- 1. SETTINGS ---
WIDTH, HEIGHT = 1280, 720
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Bunnies: The Forbidden Forest')

# Constants
PLAYER_WIDTH, PLAYER_HEIGHT = 40, 50
BASE_SPEED = 650
DASH_SPEED = 1800
DASH_DURATION = 0.15
DASH_COOLDOWN = 1.5
FOX_SPEED = 180 
BLOCK_SIZE = 80
PORTAL_SIZE = 70
FPS = 60

# Fonts
FONT = pygame.font.SysFont("comicsans", 24, bold=True)
END_FONT = pygame.font.SysFont("comicsans", 80, bold=True)

# --- 2. HELPERS ---
class Particle:
    def __init__(self, x, y, color, lifetime=25):
        self.x, self.y = x, y
        self.color = color
        self.vx, self.vy = random.uniform(-2, 2), random.uniform(-2, 2)
        self.lifetime = lifetime  
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1
    def draw(self, surface, ox=0, oy=0):
        if self.lifetime > 0:
            pygame.draw.circle(surface, self.color, (int(self.x + ox), int(self.y + oy)), 3)

def get_funny_name():
    adj = ["Stinky", "Glorious", "Slippery", "Angry", "Cabbage-Scented", "Mildly Annoying", "Shiny", "Suspicious", "Fluffy", "Extreme"]
    noun = ["Armpit", "Basement", "Toilet", "Paradise", "Doom", "Garden", "Lair", "Swamp", "Elevator", "Buffet"]
    return f"{random.choice(adj)} {random.choice(noun)}"

def get_fox_spawn_pos():
    return random.choice([(50, 50), (WIDTH - 100, 50), (50, HEIGHT - 100), (WIDTH - 100, HEIGHT - 100)])

# --- 3. ROOM GENERATION ---
room_data = {}
visited_rooms = set()

def generate_room(coords):
    if coords not in room_data:
        visited_rooms.add(coords)
        bg_colors = [(34, 139, 34), (101, 67, 33), (20, 80, 80), (107, 142, 35), (47, 79, 79)]
        theme = random.choice(["trees", "rocks", "blocks"])
        blocks = []
        safe_zone = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 150, 300, 300)
        
        walls = [pygame.Rect(0, 0, WIDTH, 20), pygame.Rect(0, HEIGHT-20, WIDTH, 20),
                 pygame.Rect(0, 0, 20, HEIGHT), pygame.Rect(WIDTH-20, 0, 20, HEIGHT)]
        blocks.extend(walls)

        for _ in range(random.randint(6, 12)):
            bx = (random.randint(2, (WIDTH // BLOCK_SIZE) - 3)) * BLOCK_SIZE
            by = (random.randint(2, (HEIGHT // BLOCK_SIZE) - 3)) * BLOCK_SIZE
            br = pygame.Rect(bx, by, BLOCK_SIZE, BLOCK_SIZE)
            if not br.colliderect(safe_zone): blocks.append(br)

        thorns = []
        for _ in range(random.randint(2, 5)):
            tx = random.randint(100, WIDTH-100)
            ty = random.randint(100, HEIGHT-100)
            tr = pygame.Rect(tx, ty, 40, 40)
            if not tr.colliderect(safe_zone): thorns.append(tr)

        foxes = [pygame.Rect(*get_fox_spawn_pos(), 50, 50)]
        carrots = [pygame.Rect(random.randint(100, 1100), random.randint(100, 600), 25, 25) for _ in range(random.randint(3, 6))]
        
        portals = {
            "top": pygame.Rect(WIDTH//2-35, 0, 70, 30), "bottom": pygame.Rect(WIDTH//2-35, HEIGHT-30, 70, 30),
            "left": pygame.Rect(0, HEIGHT//2-35, 30, 70), "right": pygame.Rect(WIDTH-30, HEIGHT//2-35, 30, 70)
        }

        room_data[coords] = {"blocks": blocks, "thorns": thorns, "foxes": foxes, "carrots": carrots, 
                             "color": random.choice(bg_colors), "theme": theme, "portals": portals, "name": get_funny_name()}
    return room_data[coords]

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
    global room_data, visited_rooms
    run = True
    clock = pygame.time.Clock()
    player = pygame.Rect(WIDTH//2, HEIGHT//2, PLAYER_WIDTH, PLAYER_HEIGHT)
    coords = (0, 0)
    score, lives = 0, 3
    game_state = "PLAYING"
    
    pulse_timer = 0
    hit_flash_timer = 0
    shake_timer = 0
    shake_intensity = 0
    transition_alpha = 0
    is_transitioning = False
    target_coords = None
    particles = []
    
    dash_timer = 0
    dash_cooldown = 0
    has_shield = False
    speed_boost = 1.0

    btn_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 100, 300, 60)

    while run:
        dt = clock.tick(FPS) / 1000.0
        pulse_timer += dt * 5 
        if hit_flash_timer > 0: hit_flash_timer -= dt
        if shake_timer > 0: shake_timer -= dt
        if dash_timer > 0: dash_timer -= dt
        if dash_cooldown > 0: dash_cooldown -= dt

        room = generate_room(coords)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: run = False
            if event.type == pygame.MOUSEBUTTONDOWN and game_state != "PLAYING":
                if btn_rect.collidepoint(event.pos):
                    room_data, visited_rooms = {}, set()
                    player.center = (WIDTH//2, HEIGHT//2)
                    coords = (0, 0)
                    score, lives, has_shield, speed_boost = 0, 3, False, 1.0
                    game_state = "PLAYING"

        if game_state == "PLAYING" and not is_transitioning:
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0
            if keys[pygame.K_a] or keys[pygame.K_LEFT]: dx = -1
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx = 1
            if keys[pygame.K_w] or keys[pygame.K_UP]: dy = -1
            if keys[pygame.K_s] or keys[pygame.K_DOWN]: dy = 1

            if keys[pygame.K_SPACE] and dash_cooldown <= 0 and (dx != 0 or dy != 0):
                dash_timer, dash_cooldown = DASH_DURATION, DASH_COOLDOWN

            final_speed = (DASH_SPEED if dash_timer > 0 else BASE_SPEED) * speed_boost
            move_with_collision(player, room["blocks"], dx * final_speed * dt, dy * final_speed * dt)

            for thorn in room["thorns"]:
                if player.colliderect(thorn) and dash_timer <= 0:
                    hit_flash_timer, shake_timer, shake_intensity = 0.4, 0.2, 8
                    player.center = (WIDTH//2, HEIGHT//2)

            for fox in room["foxes"]:
                fdx = (FOX_SPEED * dt) if fox.x < player.x else (-FOX_SPEED * dt)
                fdy = (FOX_SPEED * dt) if fox.y < player.y else (-FOX_SPEED * dt)
                move_with_collision(fox, room["blocks"], fdx, fdy)
                
                if fox.colliderect(player):
                    if dash_timer <= 0:
                        if has_shield:
                            has_shield = False
                            hit_flash_timer, shake_timer, shake_intensity = 0.3, 0.2, 5
                        else:
                            lives -= 1
                            hit_flash_timer, shake_timer, shake_intensity = 0.5, 0.3, 15
                            room["foxes"].append(pygame.Rect(*get_fox_spawn_pos(), 50, 50))
                        player.center = (WIDTH//2, HEIGHT//2)
                        if lives <= 0: game_state = "LOST"

            if score == 5 and speed_boost == 1.0: speed_boost = 1.25 
            if score == 10 and not has_shield: has_shield = True 

            for carrot in room["carrots"][:]:
                if player.colliderect(carrot):
                    for _ in range(8): particles.append(Particle(carrot.centerx, carrot.centery, (255, 165, 0)))
                    room["carrots"].remove(carrot)
                    score += 1
                    if score >= 20: game_state = "WON"

            for side, p_rect in room["portals"].items():
                if player.colliderect(p_rect):
                    is_transitioning = True
                    if side == "top": target_coords = (coords[0], coords[1] + 1)
                    elif side == "bottom": target_coords = (coords[0], coords[1] - 1)
                    elif side == "left": target_coords = (coords[0] - 1, coords[1])
                    elif side == "right": target_coords = (coords[0] + 1, coords[1])

        for p in particles[:]:
            p.update()
            if p.lifetime <= 0: particles.remove(p)
        cx, cy = (random.randint(-shake_intensity, shake_intensity), random.randint(-shake_intensity, shake_intensity)) if shake_timer > 0 else (0,0)

        # --- DRAWING ---
        WIN.fill(room["color"])
        
        pv = (math.sin(pulse_timer) + 1) / 2 
        for pr in room["portals"].values():
            pygame.draw.ellipse(WIN, (255, 255, 255), pr.inflate(10*pv, 10*pv).move(cx, cy))
            pygame.draw.ellipse(WIN, (0, 200, 255), pr.move(cx, cy))

        for block in room["blocks"]:
            dr = block.move(cx, cy)
            if block.width == WIDTH or block.height == HEIGHT: pygame.draw.rect(WIN, (30, 30, 30), dr)
            elif room["theme"] == "trees": 
                pygame.draw.rect(WIN, (80, 50, 20), (dr.centerx - 10, dr.centery, 20, 40))
                pygame.draw.circle(WIN, (20, 100, 20), (dr.centerx, dr.centery), 40)
            elif room["theme"] == "rocks": pygame.draw.rect(WIN, (100, 100, 100), dr, border_radius=20)
            else: pygame.draw.rect(WIN, (139, 69, 19), dr)

        for thorn in room["thorns"]:
            pygame.draw.circle(WIN, (150, 0, 0), (thorn.centerx + cx, thorn.centery + cy), 20, 5)

        for c in room["carrots"]: pygame.draw.circle(WIN, (255, 165, 0), (c.centerx + cx, c.centery + cy), 12)

        pygame.draw.rect(WIN, (0, 255, 255) if dash_timer > 0 else (255,255,255), player.move(cx, cy))
        if has_shield: pygame.draw.circle(WIN, (0, 150, 255), player.center, 40, 3)

        for fox in room["foxes"]: pygame.draw.rect(WIN, (255, 50, 50), fox.move(cx, cy))
        for p in particles: p.draw(WIN, cx, cy)

        # UI & MINI-MAP
        ui = FONT.render(f"Lives: {lives} | Score: {score}/20 | {room['name']}", True, (255, 255, 255))
        WIN.blit(ui, (30, 30))
        if speed_boost > 1.0: WIN.blit(FONT.render("SNEAKERS ACTIVE", True, (0, 255, 0)), (30, 60))
        
        MAP_SIZE = 10
        for rx, ry in visited_rooms:
            mx, my = 1200 + (rx * MAP_SIZE), 80 - (ry * MAP_SIZE)
            color = (255, 255, 255) if (rx, ry) == coords else (100, 100, 100)
            pygame.draw.rect(WIN, color, (mx, my, MAP_SIZE-2, MAP_SIZE-2))

        if hit_flash_timer > 0:
            o = pygame.Surface((WIDTH, HEIGHT)); o.set_alpha(int((hit_flash_timer/0.5)*150)); o.fill((255,0,0)); WIN.blit(o, (0,0))

        if is_transitioning:
            transition_alpha += 15
            if transition_alpha >= 255: coords = target_coords; player.center = (WIDTH//2, HEIGHT//2); is_transitioning = False
            o = pygame.Surface((WIDTH, HEIGHT)); o.set_alpha(transition_alpha); o.fill((0,0,0)); WIN.blit(o, (0,0))
        elif transition_alpha > 0:
            transition_alpha -= 15
            o = pygame.Surface((WIDTH, HEIGHT)); o.set_alpha(transition_alpha); o.fill((0,0,0)); WIN.blit(o, (0,0))

        if game_state != "PLAYING":
            o = pygame.Surface((WIDTH, HEIGHT)); o.set_alpha(200); o.fill((0,0,0)); WIN.blit(o, (0,0))
            is_win = game_state == "WON"
            msg = END_FONT.render("YOU WON CHAMP" if is_win else "YOU LOST LIL BRO", True, (255,255,255))
            WIN.blit(msg, msg.get_rect(center=(WIDTH//2, HEIGHT//2)))
            pygame.draw.rect(WIN, (218, 165, 32) if is_win else (200, 0, 0), btn_rect, border_radius=10)
            btn_surf = FONT.render("PLAY AGAIN CHAMP" if is_win else "Try again loser", True, (255, 255, 255))
            WIN.blit(btn_surf, btn_surf.get_rect(center=btn_rect.center))

        pygame.display.update()
    pygame.quit()

if __name__ == "__main__":
    main()