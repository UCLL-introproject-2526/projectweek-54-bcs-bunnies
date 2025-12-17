import pygame
import random
import math
import os
from heapq import heappush, heappop
from settings import WIDTH, HEIGHT, BLOCK_SIZE  

def a_star(start, goal, obstacles, cell_size):
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def get_neighbors(pos):
        x, y = pos
        neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
        return [n for n in neighbors if 0 <= n[0] < (WIDTH // cell_size) and 0 <= n[1] < (HEIGHT // cell_size) and not any(ob.colliderect(pygame.Rect(n[0]*cell_size, n[1]*cell_size, cell_size, cell_size)) for ob in obstacles)]
    
    start_cell = (int(start[0] // cell_size), int(start[1] // cell_size))
    goal_cell = (int(goal[0] // cell_size), int(goal[1] // cell_size))
    
    frontier = []
    heappush(frontier, (0, start_cell))
    came_from = {start_cell: None}
    cost_so_far = {start_cell: 0}
    
    while frontier:
        _, current = heappop(frontier)
        if current == goal_cell:
            break
        for neighbor in get_neighbors(current):
            new_cost = cost_so_far[current] + 1
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost + heuristic(goal_cell, neighbor)
                heappush(frontier, (priority, neighbor))
                came_from[neighbor] = current
    
    if goal_cell not in came_from:
        return []
    
    path = []
    current = goal_cell
    while current != start_cell:
        path.append((current[0] * cell_size + cell_size // 2, current[1] * cell_size + cell_size // 2))
        current = came_from[current]
    path.reverse()
    return path

from settings import (
    WIDTH, HEIGHT, FPS,
    PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_SPEED,
    FOX_SPEED, LIVES_START, TARGET_SCORE,
    WHITE, BLACK,
    HIT_FLASH_DURATION, HIT_FLASH_MAX_ALPHA,
    SHAKE_DURATION_FOX, SHAKE_INTENSITY_FOX,
    SHAKE_DURATION_TRAP, SHAKE_INTENSITY_TRAP,
    INVINCIBILITY_DURATION, KNOCKBACK_PIXELS,
    # DASH + SPEED BOOST
    DASH_SPEED, DASH_DURATION, DASH_COOLDOWN,
    SPEED_BOOST_SCORE_1, SPEED_BOOST_MULT_1
)

from ui import draw_text_outline, ImageButton, safe_load_png, scale_to_width
from world import generate_room, move_with_collision, portal_transition, reset_world
from bunny import Bunny  # ✅ NEW


def _knockback(player: pygame.Rect, source_center, blocks, pixels: int):
    sx, sy = source_center
    px, py = player.centerx, player.centery
    vx, vy = (px - sx), (py - sy)

    if vx == 0 and vy == 0:
        vx = random.choice([-1, 1])
        vy = random.choice([-1, 1])

    length = math.hypot(vx, vy)
    nx, ny = vx / length, vy / length
    move_with_collision(player, blocks, nx * pixels, ny * pixels)


def run_game(WIN: pygame.Surface, FONT: pygame.font.Font, END_FONT: pygame.font.Font) -> str:
    clock = pygame.time.Clock()

    #Foxes
    fox_files = sorted(os.listdir("images/fox"))
    fox_images = [pygame.image.load(os.path.join("images/fox", f)).convert_alpha() for f in fox_files]
    scale_factor = 2  # <-- adjust for bigger (e.g., 1.5 for 50% bigger, 3 for triple)
    fox_images = [pygame.transform.scale(img, (int(img.get_width() * scale_factor), int(img.get_height() * scale_factor))) for img in fox_images]

    #Carrots
    carrot_img = pygame.image.load("images/carrot.png").convert_alpha()
    carrot_img = pygame.transform.scale(carrot_img, (50, 50))

    # Pause resume button (under PAUSED)
    RESUME_IMG = scale_to_width(safe_load_png(
        "images/back_button.png"), 260, smooth=False)
    resume_btn = ImageButton(RESUME_IMG, (WIDTH // 2, HEIGHT // 2 + 140))

    while True:  # restart loop
        reset_world()

        player = pygame.Rect(WIDTH // 2, HEIGHT // 2,
                             PLAYER_WIDTH, PLAYER_HEIGHT)

        # ✅ Bunny sprite that replaces the white rect
        bunny = Bunny(player.center, white_square_size=(
            PLAYER_WIDTH, PLAYER_HEIGHT))

        current_coords = (0, 0)
        score = 0
        lives = LIVES_START
        state = "PLAYING"
        pulse_timer = 0.0

        # effects
        hit_flash_timer = 0.0
        shake_timer = 0.0
        shake_intensity = 0

        # trap + invincibility
        trap_cooldown = 0.0
        invuln_timer = 0.0

        # dash + speed boost
        dash_timer = 0.0
        dash_cooldown = 0.0
        speed_boost = 1.0

        # room transition fade (Jon style)
        transition_alpha = 0
        is_transitioning = False
        transition_phase = "out"     # "out" then "in"
        pending_portal_side = None

        while True:
            dt = clock.tick(FPS) / 1000.0
            dt_ms = dt * 1000.0

            if state == "PLAYING" and not is_transitioning:
                pulse_timer += dt * 5.0

            room = generate_room(current_coords)

            # timers decay
            if hit_flash_timer > 0:
                hit_flash_timer = max(0.0, hit_flash_timer - dt)
            if shake_timer > 0:
                shake_timer = max(0.0, shake_timer - dt)
            if trap_cooldown > 0:
                trap_cooldown = max(0.0, trap_cooldown - dt)
            if invuln_timer > 0:
                invuln_timer = max(0.0, invuln_timer - dt)

            if dash_timer > 0:
                dash_timer = max(0.0, dash_timer - dt)
            if dash_cooldown > 0:
                dash_cooldown = max(0.0, dash_cooldown - dt)

            # ---------------- EVENTS ----------------
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"

                # ESC toggles pause/resume (not during transition)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if not is_transitioning:
                        if state == "PLAYING":
                            state = "PAUSED"
                        elif state == "PAUSED":
                            state = "PLAYING"

                # While paused: ENTER resets game (both Enter keys)
                if state == "PAUSED" and event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    state = "RESTART"
                    break

                # While paused: click button resumes
                if state == "PAUSED" and resume_btn.clicked(event):
                    state = "PLAYING"

            if state == "RESTART":
                break

            # ---------------- UPDATE ----------------
            ix = iy = 0.0

            if state == "PLAYING" and not is_transitioning:
                keys = pygame.key.get_pressed()

                # input direction
                if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                    ix = -1.0
                if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                    ix = 1.0
                if keys[pygame.K_w] or keys[pygame.K_UP]:
                    iy = -1.0
                if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                    iy = 1.0

                # dash (SPACE)
                if keys[pygame.K_SPACE] and dash_cooldown <= 0 and (ix != 0.0 or iy != 0.0):
                    dash_timer = DASH_DURATION
                    dash_cooldown = DASH_COOLDOWN

                # speed boost milestone
                speed_boost = SPEED_BOOST_MULT_1 if score >= SPEED_BOOST_SCORE_1 else 1.0

                final_speed = (DASH_SPEED if dash_timer >
                               0 else PLAYER_SPEED) * speed_boost
                move_with_collision(
                    player, room["blocks"], ix * final_speed * dt, iy * final_speed * dt)

                # start portal fade (don’t switch instantly)
                for side, p_rect in room["portals"].items():
                    if player.colliderect(p_rect):
                        is_transitioning = True
                        transition_phase = "out"
                        transition_alpha = 0
                        pending_portal_side = side
                        break

                # TRAPS: take life + invincibility + knockback (no teleport)
                if invuln_timer <= 0 and trap_cooldown <= 0:
                    for trap in room.get("traps", []):
                        if player.colliderect(trap):
                            lives -= 1

                            hit_flash_timer = max(
                                hit_flash_timer, HIT_FLASH_DURATION)
                            shake_timer = max(shake_timer, SHAKE_DURATION_TRAP)
                            shake_intensity = max(
                                shake_intensity, SHAKE_INTENSITY_TRAP)

                            invuln_timer = INVINCIBILITY_DURATION
                            _knockback(player, trap.center,
                                       room["blocks"], KNOCKBACK_PIXELS)

                            trap_cooldown = 0.6

                            if lives <= 0:
                                state = "LOST"
                            break

               # fox AI
                for i, fox in enumerate(room["foxes"]):
                    # Calculate path every few frames to avoid lag (e.g., every 10 frames)
                    if len(room["fox_paths"][i]) <= 1 or random.random() < 0.1:  # Recalculate occasionally
                        room["fox_paths"][i] = a_star(fox.center, player.center, room["blocks"], BLOCK_SIZE)
                    
                    if room["fox_paths"][i] and len(room["fox_paths"][i]) > 1:
                        next_pos = room["fox_paths"][i][1]
                        dx = (next_pos[0] - fox.centerx) / max(1, abs(next_pos[0] - fox.centerx)) * FOX_SPEED * dt
                        dy = (next_pos[1] - fox.centery) / max(1, abs(next_pos[1] - fox.centery)) * FOX_SPEED * dt
                        move_with_collision(fox, room["blocks"], dx, dy)
                        # Update direction for animation
                        direction = 1 if dx > 0 else (-1 if dx < 0 else room["fox_directions"][i])
                        room["fox_directions"][i] = direction
                    else:
                        # Fallback to direct movement if no path
                        fdx = (FOX_SPEED * dt) if fox.x < player.x else (-FOX_SPEED * dt)
                        fdy = (FOX_SPEED * dt) if fox.y < player.y else (-FOX_SPEED * dt)
                        move_with_collision(fox, room["blocks"], fdx, fdy)
                        direction = 1 if fdx > 0 else (-1 if fdx < 0 else room["fox_directions"][i])
                        room["fox_directions"][i] = direction
                    
                    room["fox_frames"][i] = (room["fox_frames"][i] + 1) % len(fox_images)
                    
                    if invuln_timer <= 0 and fox.colliderect(player):
                        lives -= 1

                        hit_flash_timer = HIT_FLASH_DURATION
                        shake_timer = SHAKE_DURATION_FOX
                        shake_intensity = SHAKE_INTENSITY_FOX

                        invuln_timer = INVINCIBILITY_DURATION
                        _knockback(player, fox.center, room["blocks"], KNOCKBACK_PIXELS)

                        # keep your "spawn another fox" logic
                        room["foxes"].append(
                            pygame.Rect(
                                random.randint(100, 300),
                                random.randint(100, 300),
                                fox.width,
                                fox.height
                            )
                        )
                        room["fox_frames"].append(0)
                        room["fox_directions"].append(1)
                        room["fox_paths"].append([])

                        if lives <= 0:
                            state = "LOST"
                        break

                # carrots
                for carrot in room["carrots"][:]:
                    if player.colliderect(carrot):
                        room["carrots"].remove(carrot)
                        score += 1
                        if score >= TARGET_SCORE:
                            state = "WON"

            # ✅ Bunny animation update (uses velocity for direction/frames)
            # Bunny.update() moves bunny internally, so we update it for animation,
            # then we snap its position back to the collision rect center.
            bunny.set_velocity((ix * PLAYER_SPEED, iy * PLAYER_SPEED))
            bunny.update(dt_ms)
            bunny.set_pos(player.center)

            # ---------------- TRANSITION UPDATE (fade) ----------------
            if is_transitioning and state == "PLAYING":
                if transition_phase == "out":
                    transition_alpha += 15
                    if transition_alpha >= 255:
                        transition_alpha = 255
                        if pending_portal_side is not None:
                            current_coords = portal_transition(
                                pending_portal_side, current_coords, player)
                        pending_portal_side = None
                        transition_phase = "in"
                else:
                    transition_alpha -= 15
                    if transition_alpha <= 0:
                        transition_alpha = 0
                        is_transitioning = False

            # ---------------- SHAKE OFFSET ----------------
            cx = cy = 0
            if shake_timer > 0 and shake_intensity > 0:
                cx = random.randint(-shake_intensity, shake_intensity)
                cy = random.randint(-shake_intensity, shake_intensity)

            # ---------------- DRAW ----------------
            WIN.fill(room["color"])

            # portal glow
            pulse_val = (math.sin(pulse_timer) + 1) / 2
            glow_color = (0, 200 + int(55 * pulse_val),
                          200 + int(55 * pulse_val))
            for p_rect in room["portals"].values():
                glow_rect = p_rect.inflate(
                    int(10 * pulse_val), int(10 * pulse_val)).move(cx, cy)
                pygame.draw.ellipse(WIN, WHITE, glow_rect)
                pygame.draw.ellipse(WIN, glow_color, p_rect.move(cx, cy))

            # blocks
            for block in room["blocks"]:
                b = block.move(cx, cy)
                if block.width == WIDTH or block.height == HEIGHT:
                    pygame.draw.rect(WIN, (30, 30, 30), b)
                elif room["theme"] == "trees":
                    pygame.draw.rect(WIN, (80, 50, 20),
                                     (b.centerx - 10, b.centery, 20, 40))
                    pygame.draw.circle(WIN, (20, 100, 20),
                                       (b.centerx, b.centery), 40)
                elif room["theme"] == "rocks":
                    pygame.draw.rect(WIN, (100, 100, 100), b, border_radius=20)
                else:
                    pygame.draw.rect(WIN, (139, 69, 19), b)

            # image obstacles
            for ob in room.get("obstacles", []):
                WIN.blit(ob["img"], ob["draw_rect"].move(cx, cy))

            # traps
            for trap in room.get("traps", []):
                pygame.draw.circle(
                    WIN, (150, 0, 0), (trap.centerx + cx, trap.centery + cy), 20, 5)

            # carrots
            for carrot in room["carrots"]:
                rect = carrot_img.get_rect(center=(carrot.centerx + cx, carrot.centery + cy))
                WIN.blit(carrot_img, rect)

            # invincibility blink
            blink_hide = False
            if invuln_timer > 0:
                blink_hide = (pygame.time.get_ticks() // 100) % 2 == 0

            # ✅ draw Bunny instead of white rect (with shake offset)
            if not blink_hide:
                base_center = player.center
                bunny.set_pos((base_center[0] + cx, base_center[1] + cy))
                bunny.draw(WIN)
                bunny.set_pos(base_center)

            # foxes
            for i, fox in enumerate(room["foxes"]):
                img = fox_images[room["fox_frames"][i]]
                if room["fox_directions"][i] == -1:
                    img = pygame.transform.flip(img, True, False)
                rect = img.get_rect(center=(fox.centerx + cx, fox.centery + cy))
                WIN.blit(img, rect)

            # red flash overlay
            if hit_flash_timer > 0:
                strength = hit_flash_timer / HIT_FLASH_DURATION
                alpha = int(HIT_FLASH_MAX_ALPHA * strength)
                flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                flash.fill((255, 0, 0, alpha))
                WIN.blit(flash, (0, 0))

            # transition overlay
            if transition_alpha > 0:
                o = pygame.Surface((WIDTH, HEIGHT))
                o.set_alpha(transition_alpha)
                o.fill((0, 0, 0))
                WIN.blit(o, (0, 0))

            # UI
            ui = f"Lives: {lives} | Score: {score}/{TARGET_SCORE} | Location: {room['name']}"
            draw_text_outline(WIN, ui, FONT, WHITE, BLACK,
                              pos=(30, 30), outline_thickness=2)

            if speed_boost > 1.0:
                draw_text_outline(WIN, "SNEAKERS ACTIVE", FONT, (0, 255, 0), BLACK, pos=(
                    30, 60), outline_thickness=2)

            if dash_cooldown <= 0:
                draw_text_outline(WIN, "DASH READY (SPACE)", FONT, (255, 255, 255), BLACK, pos=(
                    30, 90), outline_thickness=2)
            else:
                draw_text_outline(WIN, f"DASH COOLDOWN: {dash_cooldown:.1f}s", FONT, (
                    200, 200, 200), BLACK, pos=(30, 90), outline_thickness=2)

            # PAUSE
            if state == "PAUSED":
                overlay = pygame.Surface((WIDTH, HEIGHT))
                overlay.set_alpha(180)
                overlay.fill((0, 0, 0))
                WIN.blit(overlay, (0, 0))

                draw_text_outline(WIN, "PAUSED", END_FONT, WHITE, BLACK,
                                  center=(WIDTH // 2, HEIGHT // 2 - 60), outline_thickness=4)
                draw_text_outline(WIN, "ESC or click button = Resume", FONT, WHITE, BLACK,
                                  center=(WIDTH // 2, HEIGHT // 2 + 20), outline_thickness=2)
                draw_text_outline(WIN, "ENTER = Reset game", FONT, WHITE, BLACK,
                                  center=(WIDTH // 2, HEIGHT // 2 + 60), outline_thickness=2)

                resume_btn.draw(WIN)
                pygame.display.flip()
                continue

            # WIN / LOSE
            if state in ("WON", "LOST"):
                overlay = pygame.Surface((WIDTH, HEIGHT))
                overlay.set_alpha(200)
                overlay.fill((0, 0, 0))
                WIN.blit(overlay, (0, 0))

                msg = "YOU LOST LIL BRO" if state == "LOST" else "YOU WON CHAMP"
                draw_text_outline(WIN, msg, END_FONT, WHITE, BLACK,
                                  center=(WIDTH // 2, HEIGHT // 2), outline_thickness=4)
                draw_text_outline(WIN, "Press ENTER to restart", FONT, WHITE, BLACK,
                                  center=(WIDTH // 2, HEIGHT // 2 + 90), outline_thickness=2)

                pygame.display.flip()

                while True:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            return "quit"
                        if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                            break
                    else:
                        clock.tick(30)
                        continue
                    break

                break  # restart

            pygame.display.flip()
