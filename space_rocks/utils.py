import math
import random
from typing import Tuple

import pygame
from pygame.math import Vector2
from pygame.sprite import Sprite
from pygame.surface import Surface

from geometry import Geometry
from window import window


def wrap_position(surface: Surface, geometry: Geometry) -> Geometry:
    position = Vector2(geometry.position + geometry.velocity)
    w, h = surface.get_size()
    if position.x % (w + 100) < position.x:
        position.x = -100
    if position.y % (h + 100) < position.y:
        position.y = -100
    return geometry.update_vel(position)


def get_random_position(surface: Surface) -> Vector2:
    return Vector2(
        random.randrange(50, surface.get_width() - 50),
        random.randrange(50, surface.get_height() - 50),
    )


def get_random_velocity(min_speed: float, max_speed: float) -> Vector2:
    speed = random.uniform(min_speed, max_speed) * random.uniform(0.5, 1.5)
    angle = random.randrange(0, 360)
    return Vector2(speed, 0).rotate(angle)


def get_random_rotation(min_rotation: float, max_rotation: float) -> float:
    r = random.uniform(min_rotation, max_rotation) * random.choice([1, -1])
    return r


def collides_with(obj: Geometry, other_obj: Geometry) -> bool:
    distance = obj.position.distance_to(other_obj.position)
    return distance < obj.radius + other_obj.radius


def is_in_screen(screen: Surface, geometry: Geometry):
    return screen.get_rect().collidepoint(geometry.position)


def sprite_collide(a: Sprite, b: Sprite):
    return pygame.sprite.spritecollide(
        a,
        pygame.sprite.Group(b),
        False,
        pygame.sprite.collide_mask,
    )


def get_safe_asteroid_distance(screen, ship_position: Vector2) -> Vector2:
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


def bounce_edge(
    surface: Surface, edge_offset: int, velocity_decrease: float, geometry: Geometry
) -> Geometry:
    assert edge_offset > 0
    assert 0 < velocity_decrease <= 1

    position = geometry.position + geometry.velocity
    w, h = surface.get_size()
    e = edge_offset
    velocity = Vector2(geometry.velocity)
    vel_decrease_threshold = 1

    if position.x >= w - e or position.x <= e:
        if abs(velocity.x) < vel_decrease_threshold:
            velocity.x = velocity.x * -1
        else:
            velocity.x = (velocity.x * velocity_decrease) * -1
    if position.y >= h - e or position.y <= e:
        if abs(velocity.y) < vel_decrease_threshold:
            velocity.y = velocity.y * -1
        else:
            velocity.y = (velocity.y * velocity_decrease) * -1

    geometry = geometry.update_vel(velocity)
    return geometry.update_pos(position)


def bounce_other(obj: Geometry, other: Geometry) -> Geometry:
    other_x, other_y = other.position
    vel = Vector2(obj.velocity)

    if other_x > 0:
        vel.x = (abs(vel.x) * -1) if other_x > obj.position.x else abs(vel.x)
    else:
        vel.x = abs(vel.x) if other_x < obj.position.x else (abs(vel.x) * -1)

    if other_y > 0:
        vel.y = (abs(vel.y) * -1) if other_y > obj.position.y else abs(vel.y)
    else:
        vel.y = abs(vel.y) if other_y < obj.position.y else (abs(vel.y) * -1)

    return obj.update_vel(vel)
