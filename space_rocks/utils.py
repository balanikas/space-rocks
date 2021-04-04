import random

from pygame.math import Vector2
from pygame.surface import Surface

from geometry import Geometry


def wrap_position(position: Vector2, surface: Surface):
    w, h = surface.get_size()
    return Vector2(position.x % w, position.y % h)


def get_random_position(surface: Surface):
    return Vector2(random.randrange(surface.get_width()), random.randrange(surface.get_height()))


def get_random_velocity(min_speed: int, max_speed: int):
    speed = random.randint(min_speed, max_speed)
    angle = random.randrange(0, 360)
    return Vector2(speed, 0).rotate(angle)


def collides_with(obj: Geometry, other_obj: Geometry) -> bool:
    distance = obj.position.distance_to(other_obj.position)
    return distance < obj.radius + other_obj.radius
