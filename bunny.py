import os, pygame

def diagonalize(src, max_shift, upward):
    w,h = src.get_size()
    dst = pygame.Surface((w, h), pygame.SRCALPHA)
    src.lock(); dst.lock()
    for y in range(h):
        t = (1 - y/(h-1)) if upward else (y/(h-1))
        shift = int(t * max_shift)
        for x in range(w):
            col = src.get_at((x, y))
            if col.a:
                nx = x + shift
                if 0 <= nx < w:
                    dst.set_at((nx, y), col)
    src.unlock(); dst.unlock()
    return dst

class Bunny:
    def __init__(self, pos, white_square_size=(32,32)):
        self.pos = pygame.math.Vector2(pos)
        files = ["idle.png","run1.png","run2.png"]
        base = []
        for name in files:
            path = os.path.join("images","bunny", name)
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, white_square_size)
            base.append(img)
        self.frames_right = base
        self.frames_left = [pygame.transform.flip(i, True, False) for i in base]
        max_shift = max(1, white_square_size[0]//6)
        self.diag_ur = [diagonalize(f, max_shift, upward=True) for f in base]
        self.diag_dr = [diagonalize(f, max_shift, upward=False) for f in base]
        self.direction = "right"; self.frame=0; self.timer=0; self.delay=120
        self.velocity = pygame.math.Vector2(0,0)

    def get_pos(self): return tuple(self.pos)
    def set_pos(self, p): self.pos = pygame.math.Vector2(p)
    def get_velocity(self): return tuple(self.velocity)
    def set_velocity(self, v): self.velocity = pygame.math.Vector2(v)

    def update(self, dt):
        moving = self.velocity.length_squared() > 0.1
        if moving:
            vx, vy = self.velocity.x, self.velocity.y
            if abs(vx) > 0 and abs(vy) > 0:
                self.direction = "ur" if vx>0 and vy<0 else ("dr" if vx>0 else ("ul" if vx<0 and vy<0 else "dl"))
            else:
                self.direction = "right" if vx>=0 else "left"
            self.timer += dt
            if self.timer >= self.delay:
                self.timer = 0
                self.frame = 1 + ((self.frame - 1 + 1) % 2)
        else:
            self.frame = 0; self.timer = 0
        self.pos += self.velocity * (dt/1000.0)

    def draw(self, surf):
        if self.direction in ("right","left"):
            frames = self.frames_right if self.direction=="right" else self.frames_left
        elif self.direction == "ur":
            frames = self.diag_ur
        elif self.direction == "dr":
            frames = self.diag_dr
        elif self.direction == "ul":
            frames = [pygame.transform.flip(f, True, False) for f in self.diag_ur]
        else: # dl
            frames = [pygame.transform.flip(f, True, False) for f in self.diag_dr]
        img = frames[self.frame]
        rect = img.get_rect(center=(int(self.pos.x), int(self.pos.y)))
        surf.blit(img, rect)