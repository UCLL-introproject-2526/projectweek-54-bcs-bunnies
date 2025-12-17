import pygame
import random
import math
from bunny import Bunny

from settings import (
    WIDTH, HEIGHT, FPS,
    PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_SPEED,
    FOX_SPEED, LIVES_START, TARGET_SCORE,
    WHITE, BLACK,
    HIT_FLASH_DURATION, HIT_FLASH_MAX_ALPHA,
    SHAKE_DURATION_FOX, SHAKE_INTENSITY_FOX,
    SHAKE_DURATION_TRAP, SHAKE_INTENSITY_TRAP,
    INVINCIBILITY_DURATION, KNOCKBACK_PIXELS
)
from ui import draw_text_outline, ImageButton, safe_load_png, scale_to_width
from world import generate_room, move_with_collision, portal_transition, reset_world


def _knockback(player: pygame.Rect, source_center, blocks, pixels: int):
    """Push player away from source_center by 'pixels', respecting collisions."""
    sx, sy = source_center
    px, py = player.centerx, player.centery
    vx, vy = (px - sx), (py - sy)

    # if perfectly overlapping, pick a random direction
    if vx == 0 and vy == 0:
        vx = random.choice([-1, 1])
        vy = random.choice([-1, 1])

    length = math.hypot(vx, vy)
    nx, ny = vx / length, vy / length

    dx = nx * pixels
    dy = ny * pixels
    move_with_collision(player, blocks, dx, dy)


def run_game(WIN: pygame.Surface, FONT: pygame.font.Font, END_FONT: pygame.font.Font) -> str:
    """
    - ESC pauses/resumes
    - Pause screen has button under PAUSED to resume
    - ENTER while paused resets game
    - ENTER on win/lose restarts
    - Screen shake + red flash on hits
    - Traps are red circles
    - NEW: NO teleport on hit, knockback instead
    - NEW: 3s invincibility after hit (fox or trap)
    """
    bunny = Bunny((WIDTH//2, HEIGHT//2), white_square_size=(64, 64))  # adjust size/pos as needed

    clock = pygame.time.Clock()
    dt = clock.tick(FPS) / 1000.0
    

    # Button shown ONLY on pause screen (under the paused text) -> resumes
    RESUME_IMG = scale_to_width(safe_load_png("images/back_button.png"), 260, smooth=False)
    resume_btn = ImageButton(RESUME_IMG, (WIDTH // 2, HEIGHT // 2 + 140))

    while True:  # restart loop
        reset_world()

        player = pygame.Rect(WIDTH // 2, HEIGHT // 2, PLAYER_WIDTH, PLAYER_HEIGHT)
        bunny.set_pos(player.center)
        current_coords = (0, 0)
        score = 0
        lives = LIVES_START
        state = "PLAYING"   # PLAYING / PAUSED / WON / LOST
        pulse_timer = 0.0

        # red hit flash
        hit_flash_timer = 0.0

        # screen shake
        shake_timer = 0.0
        shake_intensity = 0

        # trap cooldown (prevents spam)
        trap_cooldown = 0.0

        # NEW: invincibility timer
        invuln_timer = 0.0

        while True:
            dt = clock.tick(FPS) / 1000.0

            if state == "PLAYING":
                pulse_timer += dt * 5.0

            room = generate_room(current_coords)

            # timers decay (even while paused so effects fade nicely)
            if hit_flash_timer > 0:
                hit_flash_timer = max(0.0, hit_flash_timer - dt)
            if shake_timer > 0:
                shake_timer = max(0.0, shake_timer - dt)
            if trap_cooldown > 0:
                trap_cooldown = max(0.0, trap_cooldown - dt)
            if invuln_timer > 0:
                invuln_timer = max(0.0, invuln_timer - dt)

            # ---------------- EVENTS ----------------
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"

                # ESC toggles pause/resume
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if state == "PLAYING":
                        state = "PAUSED"
                    elif state == "PAUSED":
                        state = "PLAYING"

                # While paused: ENTER resets game (both Enter keys)
                if state == "PAUSED" and event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    state = "RESTART"
                    break

                # While paused: clicking the button resumes
                if state == "PAUSED" and resume_btn.clicked(event):
                    state = "PLAYING"

            if state == "RESTART":
                break

            # ---------------- UPDATE (only if PLAYING) ----------------
            if state == "PLAYING":
                keys = pygame.key.get_pressed()
                dx = dy = 0.0
                if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                    dx = -PLAYER_SPEED * dt
                if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                    dx = PLAYER_SPEED * dt
                if keys[pygame.K_w] or keys[pygame.K_UP]:
                    dy = -PLAYER_SPEED * dt
                if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                    dy = PLAYER_SPEED * dt

                bunny.set_velocity((dx / dt if dx != 0 else 0, dy / dt if dy != 0 else 0))
                bunny.update(dt * 1000)

                move_with_collision(player, room["blocks"], dx, dy)
                bunny.set_pos(player.center)

                # portals
                for side, p_rect in room["portals"].items():
                    if player.colliderect(p_rect):
                        current_coords = portal_transition(side, current_coords, player)
                        room = generate_room(current_coords)
                        break

                # --- traps (red circles) ---
                # Only trigger if not invincible, and cooldown passed.
                if invuln_timer <= 0 and trap_cooldown <= 0:
                    for trap in room.get("traps", []):
                        if player.colliderect(trap):
                            # effects
                            hit_flash_timer = max(hit_flash_timer, HIT_FLASH_DURATION)
                            shake_timer = max(shake_timer, SHAKE_DURATION_TRAP)
                            shake_intensity = max(shake_intensity, SHAKE_INTENSITY_TRAP)

                            # NEW: invincibility
                            invuln_timer = INVINCIBILITY_DURATION

                            # NEW: knockback away from trap (no teleport)
                            _knockback(player, trap.center, room["blocks"], KNOCKBACK_PIXELS)

                            trap_cooldown = 0.6
                            break

                # fox AI
                for fox in room["foxes"]:
                    fdx = (FOX_SPEED * dt) if fox.x < player.x else (-FOX_SPEED * dt)
                    fdy = (FOX_SPEED * dt) if fox.y < player.y else (-FOX_SPEED * dt)
                    move_with_collision(fox, room["blocks"], fdx, fdy)

                    # Only take damage if NOT invincible
                    if invuln_timer <= 0 and fox.colliderect(player):
                        lives -= 1

                        # effects
                        hit_flash_timer = HIT_FLASH_DURATION
                        shake_timer = SHAKE_DURATION_FOX
                        shake_intensity = SHAKE_INTENSITY_FOX

                        # NEW: invincibility window
                        invuln_timer = INVINCIBILITY_DURATION

                        # NEW: knockback away from fox (no teleport)
                        _knockback(player, fox.center, room["blocks"], KNOCKBACK_PIXELS)

                        # spawn another fox (your logic stays)
                        room["foxes"].append(
                            pygame.Rect(
                                random.randint(100, 300),
                                random.randint(100, 300),
                                fox.width,
                                fox.height
                            )
                        )

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

            # ---------------- SHAKE OFFSET ----------------
            cx = cy = 0
            if shake_timer > 0 and shake_intensity > 0:
                cx = random.randint(-shake_intensity, shake_intensity)
                cy = random.randint(-shake_intensity, shake_intensity)

            # ---------------- DRAW ----------------
            WIN.fill(room["color"])

            # portal glow (shaken)
            pulse_val = (math.sin(pulse_timer) + 1) / 2
            glow_color = (0, 200 + int(55 * pulse_val), 200 + int(55 * pulse_val))
            for p_rect in room["portals"].values():
                glow_rect = p_rect.inflate(int(10 * pulse_val), int(10 * pulse_val)).move(cx, cy)
                pygame.draw.ellipse(WIN, WHITE, glow_rect)
                pygame.draw.ellipse(WIN, glow_color, p_rect.move(cx, cy))

            # environment blocks (shaken)
            for block in room["blocks"]:
                b = block.move(cx, cy)
                if block.width == WIDTH or block.height == HEIGHT:
                    pygame.draw.rect(WIN, (30, 30, 30), b)
                elif room["theme"] == "trees":
                    pygame.draw.rect(WIN, (80, 50, 20), (b.centerx - 10, b.centery, 20, 40))
                    pygame.draw.circle(WIN, (20, 100, 20), (b.centerx, b.centery), 40)
                elif room["theme"] == "rocks":
                    pygame.draw.rect(WIN, (100, 100, 100), b, border_radius=20)
                else:
                    pygame.draw.rect(WIN, (139, 69, 19), b)

            # image obstacles (shaken)
            for ob in room.get("obstacles", []):
                WIN.blit(ob["img"], ob["draw_rect"].move(cx, cy))

            # traps (shaken)
            for trap in room.get("traps", []):
                pygame.draw.circle(WIN, (150, 0, 0), (trap.centerx + cx, trap.centery + cy), 20, 5)

            # carrots (shaken)
            for carrot in room["carrots"]:
                pygame.draw.circle(WIN, (255, 165, 0), (carrot.centerx + cx, carrot.centery + cy), 12)

            # player + foxes (shaken)
            #pygame.draw.rect(WIN, WHITE, player.move(cx, cy))
            bunny_pos = bunny.get_pos()
            bunny.set_pos((bunny_pos[0] + cx, bunny_pos[1] + cy))
            bunny.draw(WIN)
            bunny.set_pos(bunny_pos)
            for fox in room["foxes"]:
                pygame.draw.rect(WIN, (255, 50, 50), fox.move(cx, cy))

            # red flash overlay (NOT shaken)
            if hit_flash_timer > 0:
                strength = hit_flash_timer / HIT_FLASH_DURATION
                alpha = int(HIT_FLASH_MAX_ALPHA * strength)
                flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                flash.fill((255, 0, 0, alpha))
                WIN.blit(flash, (0, 0))

            # UI (NOT shaken)
            ui = f"Lives: {lives} | Score: {score}/{TARGET_SCORE} | Location: {room['name']}"
            draw_text_outline(WIN, ui, FONT, WHITE, BLACK, pos=(30, 30), outline_thickness=2)

            # ---------------- PAUSE SCREEN ----------------
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

            # ---------------- WIN/LOSE SCREEN ----------------
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

                break  # restart fresh

            pygame.display.flip()
