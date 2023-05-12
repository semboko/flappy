import pygame
from pymunk import Space, Vec2d, Body, Circle
from utils import convert
from math import ceil
from random import randint
from typing import List, Tuple
from pygame import Rect, Vector2 as V2

pygame.init()
DISPLAY_WIDTH = 480
DISPLAY_HEIGHT = 640
display = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT), display=1)
clock = pygame.time.Clock()
font = pygame.font.Font("./assets/VT323-Regular.ttf", 48)
fps = 60

space = Space()
space.gravity = 0, -1000


class GameBackground:
    def __init__(self) -> None:
        self.bg_image = pygame.image.load("./assets/Background.png")
        self.terrain_image = pygame.image.load("./assets/Terrain.png")
        self.tw = self.terrain_image.get_width()
        
    def render(self, scroll_x: int) -> None:
        display.blit(self.bg_image, (0, 0))
        scroll_x = scroll_x % self.tw - self.tw
        for i in range(2):
            display.blit(self.terrain_image, (i * self.tw + scroll_x, 565))


class Bird:
    def __init__(self, pos: Vec2d) -> None:
        self.body = Body()
        self.body.position = pos
        self.r = 25
        self.shape = Circle(self.body, self.r)
        self.shape.density = 1
        space.add(self.body, self.shape)
        
        raw_image = pygame.image.load("assets/emblem_256.png")
        self.image = pygame.transform.scale(raw_image, (2.5*self.r, 2.5*self.r))
        self.rect = self.image.get_rect(center=convert(self.body.position, display.get_height()))

    def jump(self):
        self.body.velocity = Vec2d(0, 0)
        self.body.apply_force_at_local_point((0, 40000000), (0, -self.r))
        
    def render(self):
        pos = convert(self.body.position, display.get_height())
        velocity_y = self.body.velocity.y
        if velocity_y > 0:
            angle = 20
        else:
            angle = 0
        rotated_img = pygame.transform.rotate(self.image, angle)
        rect = rotated_img.get_rect(center=pos)
        self.rect = display.blit(rotated_img, rect)
        # pygame.draw.circle(display, (0, 0, 0), pos, self.r, 1)
        # pygame.draw.rect(display, (255, 0, 0), self.rect, 1)


class Pipe:
    gap_size = 170
    width = 40
    
    @classmethod
    def spawn(cls):
        return cls(480, randint(200, 400))
    
    def __init__(self, init_x: int, gap_y: int) -> None:
        self.x = init_x
        self.gap_y = gap_y
        self.debug_color = (255, 0, 0)
        
        self.top_image = pygame.image.load("./assets/Pipe.png")
        bottom_draft = pygame.transform.rotate(self.top_image, 180)
        self.bottom_image = pygame.transform.flip(bottom_draft, True, False)
        
    def get_rects(self) -> Tuple[Rect, Rect]:
        left = self.x - self.width/2
        top_rect = Rect(V2(left, 0), V2(self.width, self.gap_y - self.gap_size/2))
        bottom_rect = Rect(V2(left, self.gap_y + self.gap_size/2), V2(self.width, 600))
        return top_rect, bottom_rect

    def render(self) -> None:
        top_area, bottom_area = self.get_rects()
        # pygame.draw.rect(display, self.debug_color, top)
        # pygame.draw.rect(display, self.debug_color, bottom)
        image_height = self.top_image.get_height()
        x = self.x - self.width/2
        top_y = self.gap_y - self.gap_size/2 - image_height
        bottom_y = self.gap_y + self.gap_size/2
        display.blit(self.top_image, (x, top_y))
        display.blit(self.bottom_image, (x, bottom_y))
        

class Game:
    score: int
    is_running: bool
    is_over: bool
    scroll_x: int
    bird: Bird
    background: GameBackground
    pipes: List[Pipe]
    
    def __init__(self) -> None:
        self.bird = Bird(Vec2d(200, 250))
        self.background = GameBackground()
        self.restart()

    def restart(self):
        self.over()
        self.is_over = False
        self.score = 0
        self.scroll_x = 0
        self.speed = 5
        self.pipes = []
    
    def run(self):
        self.is_running = True
        self.bird.body.body_type = Body.DYNAMIC
        
    def handle_space(self):
        if self.is_over:
            game.restart()
            return
        if not self.is_running:
            game.run()
        game.bird.jump()
    
    def over(self):
        self.is_over = True
        self.is_running = False
        self.bird.body.body_type = Body.STATIC
        
    def step(self):
        self.scroll_x -= self.speed
        for pipe in self.pipes:
            pipe.x -= self.speed
            if pipe.x < 0:
                self.pipes.remove(pipe)
                self.score += 1
        if self.scroll_x < -1000 and self.scroll_x % 400 == 0:
            self.pipes.append(Pipe.spawn())
    
    def bird_collides_with_pipes(self):
        bb = self.bird.shape.bb
        size = self.bird.shape.radius * 2
        bird_rect = Rect(convert(V2(bb.left, bb.top), DISPLAY_HEIGHT), V2(size, size))
        # pygame.draw.rect(display, (255, 255, 0), bird_rect, 2)
        for pipe in game.pipes:
            if bird_rect.collidelist(pipe.get_rects()) != -1:
                return True
    
    def render(self):
        self.background.render(self.scroll_x)
        self.bird.render()
        for pipe in self.pipes:
            pipe.render()
    
        # Draw Score
        score_info = font.render(f"Score: {self.score}", True, (255, 255, 255))
        dest = score_info.get_rect(center=(DISPLAY_WIDTH/2, 100))
        display.blit(score_info, dest)
        


game = Game()

while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            exit()
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_SPACE:
                game.handle_space()
    
    display.fill((255, 255, 255))
    game.render()
    if game.bird_collides_with_pipes():
        game.over()
    
    
    pygame.display.update()
    space.step(1/fps)
    clock.tick(fps)
    if game.is_running:
        game.step()