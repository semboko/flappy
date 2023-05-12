import pygame
from pymunk import Vec2d


def convert(pos: Vec2d, h: int) -> pygame.Vector2:
    return pygame.Vector2(pos.x, h - pos.y)