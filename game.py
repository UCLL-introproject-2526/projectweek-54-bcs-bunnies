import pygame
import time
import random
import math

from settings import (
    WIDTH, HEIGHT, FPS,
    PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_SPEED,
    FOX_SPEED, LIVES_START, TARGET_SCORE,
    WHITE, BLACK
)
from ui import draw_text_outline
from world import generate_room, move_with_collision, portal_transition, reset_world


def run_game(WIN: pygame.Surface, FONT: pygame.font.Font, END_FONT: pygame.font.Font) -> str:
    """
    Runs the game.
    ENTER on win/lose -> restart from the real beginning (fresh rooms, full lives, score 0).
    ESC -> menu.
    """

    clock = pygame.time.Clock()

    while True:  # restart loop
        reset_world()

        player = pygame.Rect(WIDTH//2, HEIGHT//2, PLAYER_WIDTH, PLAYER_HEIGHT)
        current_coords = (0, 0)
        score = 0
        lives = LIVES_START
        state = "PLAYING"
        pulse_timer = 0.0

        while True:
            dt = clock.tick(FPS) / 1000.0
            pulse_timer += dt * 5.0
            room = generate_room(current_coords)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return "menu"

            if state == "PLAYING":
                keys = pygame.key.get_pressed()
                dx = dy = 0.0
                if keys[pygame.K_a] or keys[pygame.K_LEFT]:  dx = -PLAYER_SPEED * dt
                if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx =  PLAYER_SPEED * dt
                if keys[pygame.K_w] or keys[pygame.K_UP]:    dy = -PLAYER_SPEED * dt
                if keys[pygame.K_s] or keys[pygame.K_DOWN]:  dy =  PLAYER_SPEED * dt

                move_with_collision(player, room["blocks"], dx, dy)

                # portals
                for side, p_rect in room["portals"].items():
                    if player.colliderect(p_rect):
                        current_coords = portal_transition(side, current_coords, player)
                        room = generate_room(current_coords)
                        break

                # fox AI (UNCHANGED)
                for fox in room["foxes"]:
                    fdx = (FOX_SPEED * dt) if fox.x < player.x else (-FOX_SPEED * dt)
                    fdy = (FOX_SPEED * dt) if fox.y < player.y else (-FOX_SPEED * dt)
                    move_with_collision(fox, room["blocks"], fdx, fdy)

                    if fox.colliderect(player):
                        lives -= 1
                        # spawn another fox in this room (UNCHANGED)
                        room["foxes"].append(
                            pygame.Rect(
                                random.randint(100, 300),
                                random.randint(100, 300),
                                fox.width,
                                fox.height
                            )
                        )
                        player.center = (WIDTH//2, HEIGHT//2)
                        if lives <= 0:
                            state = "LOST"
                            break

                # carrots/score (UNCHANGED)
                for carrot in room["carrots"][:]:
                    if player.colliderect(carrot):
                        room["carrots"].remove(carrot)
                        score += 1
                        if score >= TARGET_SCORE:
                            state = "WON"

            # --- DRAW ---
            WIN.fill(room["color"])

            # portal glow
            pulse_val = (math.sin(pulse_timer) + 1) / 2
            glow_color = (0, 200 + int(55 * pulse_val), 200 + int(55 * pulse_val))
            for p_rect in room["portals"].values():
                glow_rect = p_rect.inflate(int(10 * pulse_val), int(10 * pulse_val))
                pygame.draw.ellipse(WIN, WHITE, glow_rect)
                pygame.draw.ellipse(WIN, glow_color, p_rect)

            # environment blocks (your existing drawing)
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

            # NEW: draw your image obstacles (trees/bushes)
            for ob in room.get("obstacles", []):
                WIN.blit(ob["img"], ob["draw_rect"])

            # carrots
            for carrot in room["carrots"]:
                pygame.draw.circle(WIN, (255, 165, 0), carrot.center, 12)

            # player + fox rects
            pygame.draw.rect(WIN, WHITE, player)
            for fox in room["foxes"]:
                pygame.draw.rect(WIN, (255, 50, 50), fox)

            # UI text with outline
            ui = f"Lives: {lives} | Score: {score}/{TARGET_SCORE} | Location: {room['name']}"
            draw_text_outline(WIN, ui, FONT, WHITE, BLACK, pos=(30, 30), outline_thickness=2)

            # win/lose screen + restart
            if state != "PLAYING":
                overlay = pygame.Surface((WIDTH, HEIGHT))
                overlay.set_alpha(200)
                overlay.fill((0, 0, 0))
                WIN.blit(overlay, (0, 0))

                msg = "YOU LOST LIL BRO" if state == "LOST" else "YOU WON CHAMP"
                draw_text_outline(WIN, msg, END_FONT, WHITE, BLACK, center=(WIDTH//2, HEIGHT//2), outline_thickness=4)
                draw_text_outline(WIN, "Press ENTER to restart | ESC for menu", FONT, WHITE, BLACK,
                                  center=(WIDTH//2, HEIGHT//2 + 90), outline_thickness=2)

                pygame.display.flip()

                while True:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            return "quit"
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_RETURN:
                                break
                            if event.key == pygame.K_ESCAPE:
                                return "menu"
                    else:
                        clock.tick(30)
                        continue
                    break

                break  # restart fresh (outer loop)

            pygame.display.flip()
