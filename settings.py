
import pygame

# Window
WIDTH, HEIGHT = 1280, 720
FPS = 60

# Player / enemies
PLAYER_WIDTH, PLAYER_HEIGHT = 40, 50
PLAYER_SPEED = 650

FOX_WIDTH, FOX_HEIGHT = 50, 50
FOX_SPEED = 300

# Gameplay
LIVES_START = 3
TARGET_SCORE = 15

# World
BLOCK_SIZE = 80
PORTAL_SIZE = 70

# UI / Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Hit / damage flash effect
HIT_FLASH_DURATION = 0.25   # seconds (0.2–0.35 feels good)
HIT_FLASH_MAX_ALPHA = 120   # 0–255 (higher = stronger red)
