import pygame as pg
import pymunk
from typing import List

pg.init()
display = pg.display.set_mode((1000, 500))
clock = pg.time.Clock()
space = pymunk.Space()
space.gravity = (0, -1000)

def convert(pos: pymunk.Vec2d) -> pg.Vector2:
    return pg.Vector2(pos.x, display.get_height() - pos.y)

class Bird:
    def __init__(self, pos: pymunk.Vec2d, r: int) -> None:
        self.body = pymunk.Body()
        self.body.position = pos
        self.shape = pymunk.Circle(self.body, r)
        self.r = r
        self.shape.density = 1
        space.add(self.body, self.shape)
        
        raw_icon = pg.image.load("./assets/emblem_256.png")
        self.icon = pg.transform.scale(raw_icon, pg.Vector2(self.r * 2, self.r * 2))
    
    def jump(self):
        self.body.apply_force_at_local_point((0, 40000000), (0, -self.r))
    
    def render(self, screen: pg.Surface):
        # pg.draw.circle(screen, (255, 0, 0), convert(self.body.position), self.r, 1)
        icon_pos = self.body.position + pymunk.Vec2d(-self.r, self.r)
        screen.blit(self.icon, convert(icon_pos))
        

def mainloop():
    bird = Bird(pymunk.Vec2d(250, 250), 25)
    while True:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                return
            if e.type == pg.KEYDOWN:
                if e.key == pg.K_SPACE:
                    bird.jump()
        
        display.fill((255, 255, 255))
        
        bird.render(display)
        
        pg.display.update()
        clock.tick(60)
        space.step(1/60)


mainloop()