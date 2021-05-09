import math
import random
from typing import Tuple

import pygame
from pygame.math import Vector2
from pygame.sprite import Sprite
from pygame.surface import Surface
from pygame.transform import rotozoom
from pygame.rect import Rect

from space_rocks.geometry import Geometry
from space_rocks.window import window


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
    return screen.get_rect().collidepoint(geometry.position.x, geometry.position.y)


def sprite_collide(a: Sprite, b: Sprite):
    return pygame.sprite.spritecollide(
        a,
        pygame.sprite.Group(b),
        False,
        pygame.sprite.collide_mask,
    )


def get_safe_enemy_distance(screen: Surface, player_position: Vector2) -> Vector2:
    min_enemy_distance = 350
    while True:
        position = get_random_position(screen)
        if position.distance_to(player_position) > min_enemy_distance:
            break
    return position


def get_resize_factor(factor: float) -> Tuple[int, int]:
    assert factor > 0
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
    vel = Vector2(obj.velocity)

    def update_velocity(velocity: float, pos: float, other_pos: float):
        velocity = abs(velocity)
        if other_pos > 0:
            return velocity * -1 if other_pos > pos else velocity
        else:
            return velocity if other_pos < pos else velocity * -1

    vel.x = update_velocity(vel.x, obj.position.x, other.position.x)
    vel.y = update_velocity(vel.y, obj.position.y, other.position.y)

    return obj.update_vel(vel)


def get_random_choice(text: str) -> str:
    text = text.lower()
    return random.choice(
        [x.strip(" ") for x in text.split(",")]
    )  # randomize what to play if many


def get_blit_position(surface: Surface, position: Vector2):
    surface_size = Vector2(surface.get_size())
    blit_position = position - surface_size * 0.5
    return (int(blit_position.x), int(blit_position.y))


def scale_surface(surface: Surface, size: Tuple[int, int]) -> Surface:
    return pygame.transform.scale(surface, size)


def create_surface_alpha(size: Tuple[int, int]) -> Surface:
    return Surface(size, pygame.SRCALPHA)


def create_surface_from_image(image_file_path: str):
    return pygame.image.load(image_file_path)


def create_default_font(size: int) -> pygame.font.Font:
    return pygame.font.Font(None, size)


def scale_and_rotate(surface: Surface, angle: float, scale: float) -> Surface:
    return rotozoom(surface, angle, scale)


def init_display() -> Surface:
    pygame.display.set_caption("experimental video game by balanikas@github")
    # having SCALED as flags enables vsync but fucks up most animations.
    flags = pygame.SCALED | pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF
    screen = pygame.display.set_mode(
        (pygame.display.Info().current_w, pygame.display.Info().current_h),
        flags,
        32,
        vsync=1,
    )

    lines = []
    info = pygame.display.Info()
    lines.append(f"Current Video Driver: {pygame.display.get_driver()}")
    lines.append(f"Video Mode is Accelerated: {('No', 'Yes')[info.hw]}")
    lines.append(f"Display Depth (Bits Per Pixel): {info.bitsize:d}")
    print(lines)

    return screen


def init_fonts():
    pygame.font.init()
