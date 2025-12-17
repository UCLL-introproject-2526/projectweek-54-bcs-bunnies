import pygame
import time
import random
import math

from settings import (
    WIDTH, HEIGHT, FPS,
    PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_SPEED,
    FOX_SPEED, LIVES_START, TARGET_SCORE,
    WHITE, BLACK,
    HIT_FLASH_DURATION, HIT_FLASH_MAX_ALPHA
)
from ui import draw_text_outline, ImageButton, safe_load_png, scale_to_width
from world import generate_room, move_with_collision, portal_transition, reset_world


def run_game(WIN: pygame.Surface, FONT: pygame.font.Font, END_FONT: pygame.font.Font) -> str:
    """
    ENTER on win/lose -> restart from beginning.
    ESC key -> PAUSE toggle.
    While PAUSED:
      - Click button under "PAUSED" to RESUME
      - Press ESC to RESUME
      - Press ENTER to RESET (restart game fresh)
    Red hit flash when fox touches you.
    """
    clock = pygame.time.Clock()

    # Button shown ONLY on pause screen (under the paused text)
    RESUME_IMG = scale_to_width(safe_load_png("images/back_button.png"), 260, smooth=False)
    resume_btn = ImageButton(RESUME_IMG, (WIDTH // 2, HEIGHT // 2 + 140))

    while True:  # restart loop (ENTER on win/lose, ENTER on pause reset)
        reset_world()

        player = pygame.Rect(WIDTH // 2, HEIGHT // 2, PLAYER_WIDTH, PLAYER_HEIGHT)
        current_coords = (0, 0)
        score = 0
        lives = LIVES_START
        state = "PLAYING"   # PLAYING / PAUSED / WON / LOST
        pulse_timer = 0.0

        hit_flash_timer = 0.0

        while True:
            dt = clock.tick(FPS) / 1000.0

            if state == "PLAYING":
                pulse_timer += dt * 5.0

            room = generate_room(current_coords)

            # fade red flash even while paused
            if hit_flash_timer > 0:
                hit_flash_timer = max(0.0, hit_flash_timer - dt)

            # ---------------- EVENTS ----------------
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"

                # ESC toggles pause/resume (only play/pause)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if state == "PLAYING":
                        state = "PAUSED"
                    elif state == "PAUSED":
                        state = "PLAYING"

                # While paused: ENTER resets game
                if state == "PAUSED" and event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    # restart fresh: break inner loop -> outer while True restarts
                    state = "RESTART"
                    break

                # While paused: clicking the button resumes
                if state == "PAUSED" and resume_btn.clicked(event):
                    state = "PLAYING"

            # if we set restart flag from pause
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

                move_with_collision(player, room["blocks"], dx, dy)

                # portals
                for side, p_rect in room["portals"].items():
                    if player.colliderect(p_rect):
                        current_coords = portal_transition(side, current_coords, player)
                        room = generate_room(current_coords)
                        break

                # fox AI (unchanged + red flash)
                for fox in room["foxes"]:
                    fdx = (FOX_SPEED * dt) if fox.x < player.x else (-FOX_SPEED * dt)
                    fdy = (FOX_SPEED * dt) if fox.y < player.y else (-FOX_SPEED * dt)
                    move_with_collision(fox, room["blocks"], fdx, fdy)

                    if fox.colliderect(player):
                        lives -= 1
                        hit_flash_timer = HIT_FLASH_DURATION

                        room["foxes"].append(
                            pygame.Rect(
                                random.randint(100, 300),
                                random.randint(100, 300),
                                fox.width,
                                fox.height
                            )
                        )

                        player.center = (WIDTH // 2, HEIGHT // 2)
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

            # ---------------- DRAW ----------------
            WIN.fill(room["color"])

            # portal glow
            pulse_val = (math.sin(pulse_timer) + 1) / 2
            glow_color = (0, 200 + int(55 * pulse_val), 200 + int(55 * pulse_val))
            for p_rect in room["portals"].values():
                glow_rect = p_rect.inflate(int(10 * pulse_val), int(10 * pulse_val))
                pygame.draw.ellipse(WIN, WHITE, glow_rect)
                pygame.draw.ellipse(WIN, glow_color, p_rect)

            # environment blocks
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

            # image obstacles
            for ob in room.get("obstacles", []):
                WIN.blit(ob["img"], ob["draw_rect"])

            # carrots
            for carrot in room["carrots"]:
                pygame.draw.circle(WIN, (255, 165, 0), carrot.center, 12)

            # player + foxes
            pygame.draw.rect(WIN, WHITE, player)
            for fox in room["foxes"]:
                pygame.draw.rect(WIN, (255, 50, 50), fox)

            # red flash overlay
            if hit_flash_timer > 0:
                strength = hit_flash_timer / HIT_FLASH_DURATION
                alpha = int(HIT_FLASH_MAX_ALPHA * strength)
                flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                flash.fill((255, 0, 0, alpha))
                WIN.blit(flash, (0, 0))

            # UI
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

                # button under the text (resumes)
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
