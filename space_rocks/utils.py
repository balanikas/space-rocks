import math
import random
from typing import Tuple

import pygame
from pygame.math import Vector2
from pygame.surface import Surface

from geometry import Geometry
from space_rocks.window import window


def wrap_position(position: Vector2, surface: Surface):
    w, h = surface.get_size()

    if position.x % (w + 100) < position.x:
        position.x = -100
    if position.y % (h + 100) < position.y:
        position.y = -100
    return Vector2(position.x, position.y)


def get_random_position(surface: Surface):
    return Vector2(
        random.randrange(surface.get_width()), random.randrange(surface.get_height())
    )


def get_random_velocity(min_speed: int, max_speed: int):
    speed = random.randint(min_speed, max_speed) * random.random()
    angle = random.randrange(0, 360)
    return Vector2(speed, 0).rotate(angle)


def get_random_rotation(min_rotation: int, max_rotation):
    r = (
        random.randint(min_rotation, max_rotation)
        * random.random()
        * random.choice([1, -1])
    )
    return r


def collides_with(obj: Geometry, other_obj: Geometry) -> bool:
    distance = obj.position.distance_to(other_obj.position)
    return distance < obj.radius + other_obj.radius


def get_safe_asteroid_distance(screen, ship_position: Vector2):
    min_asteroid_distance = 250
    while True:
        position = get_random_position(screen)
        if position.distance_to(ship_position) > min_asteroid_distance:
            break
    return position


def print_pygame_info():
    lines = []
    info = pygame.display.Info()
    lines.append(f"Current Video Driver: {pygame.display.get_driver()}")
    lines.append(f"Video Mode is Accelerated: {('No', 'Yes')[info.hw]}")
    lines.append(f"Display Depth (Bits Per Pixel): {info.bitsize:d}")

    info = pygame.mixer.get_init()
    lines.append(f"Sound Frequency: {info[0]:d}")
    lines.append(f"Sound Quality: {abs(info[1]):d} bits")
    lines.append(f"Sound Channels: {('Mono', 'Stereo')[info[2] - 1]}")

    print(lines)


def get_resize_factor(factor: float) -> Tuple[int, int]:
    max_ratio = max(window.size)
    return math.floor(max_ratio * factor), math.floor(max_ratio * factor)
