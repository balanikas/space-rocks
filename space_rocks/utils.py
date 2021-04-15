import random

import pygame

from pygame.math import Vector2
from pygame.surface import Surface

from geometry import Geometry


def wrap_position(position: Vector2, surface: Surface):
    w, h = surface.get_size()
    return Vector2(position.x % w, position.y % h)


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
    MIN_ASTEROID_DISTANCE = 250
    while True:
        position = get_random_position(screen)
        if position.distance_to(ship_position) > MIN_ASTEROID_DISTANCE:
            break
    return position

def print_info():
    lines = []
    info = pygame.display.Info()
    lines.append("Current Video Driver: %s" % pygame.display.get_driver())
    lines.append("Video Mode is Accelerated: %s" % ("No", "Yes")[info.hw])
    lines.append("Display Depth (Bits Per Pixel): %d" % info.bitsize)

    info = pygame.mixer.get_init()
    lines.append("Sound Frequency: %d" % info[0])
    lines.append("Sound Quality: %d bits" % abs(info[1]))
    lines.append("Sound Channels: %s" % ("Mono", "Stereo")[info[2] - 1])

    print(lines)