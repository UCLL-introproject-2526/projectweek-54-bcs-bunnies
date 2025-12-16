
import pygame
from settings import WIDTH, HEIGHT

def scale_to_width(image: pygame.Surface, target_width: int, *, smooth: bool = False) -> pygame.Surface:
    w, h = image.get_size()
    if w == 0:
        return image
    scale = target_width / w
    new_size = (max(1, int(w * scale)), max(1, int(h * scale)))
    return pygame.transform.smoothscale(image, new_size) if smooth else pygame.transform.scale(image, new_size)

def safe_load_bg(path: str, fallback_color=(40, 80, 40)) -> pygame.Surface:
    try:
        img = pygame.image.load(path).convert()
        return pygame.transform.scale(img, (WIDTH, HEIGHT))
    except Exception as e:
        print(f"[UI] Failed to load background {path}: {e}")
        surf = pygame.Surface((WIDTH, HEIGHT))
        surf.fill(fallback_color)
        return surf

def safe_load_png(path: str) -> pygame.Surface:
    try:
        return pygame.image.load(path).convert_alpha()
    except Exception as e:
        print(f"[UI] Failed to load png {path}: {e}")
        # Transparent placeholder
        surf = pygame.Surface((300, 80), pygame.SRCALPHA)
        pygame.draw.rect(surf, (60, 60, 60), surf.get_rect(), border_radius=12)
        return surf

def draw_text_outline(surface: pygame.Surface, text: str, font: pygame.font.Font,
                      text_color, outline_color, *, center=None, pos=None, outline_thickness: int = 2):
    base = font.render(text, True, text_color)
    outline = font.render(text, True, outline_color)

    if center is not None:
        rect = base.get_rect(center=center)
        x, y = rect.topleft
    else:
        if pos is None:
            raise ValueError("Provide either center=(x,y) or pos=(x,y)")
        x, y = pos

    for dx in range(-outline_thickness, outline_thickness + 1):
        for dy in range(-outline_thickness, outline_thickness + 1):
            if dx != 0 or dy != 0:
                surface.blit(outline, (x + dx, y + dy))
    surface.blit(base, (x, y))

class ImageButton:
    def __init__(self, image: pygame.Surface, center):
        self.image = image
        self.rect = self.image.get_rect(center=center)

    def draw(self, surface: pygame.Surface):
        surface.blit(self.image, self.rect)

    def clicked(self, event: pygame.event.Event) -> bool:
        return (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(event.pos))