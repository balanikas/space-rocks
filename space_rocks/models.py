import time
from typing import Any, Callable

import pygame
from pygame.math import Vector2
from pygame.surface import Surface
from pygame.transform import rotozoom

from audio import SoundLibrary
from geometry import Geometry
from graphics import SpriteLibrary
from utils import wrap_position, get_random_velocity


class GameObject:
    def __init__(self, position: Vector2, sprite: Surface, velocity: Vector2):
        if sprite:
            self.sprite: Surface = sprite
            self.geometry: Geometry = Geometry(
                position, sprite.get_width() / 2, velocity
            )

    def draw(self, surface: Surface):
        blit_position = self.geometry.position - Vector2(self.geometry.radius)
        surface.blit(self.sprite, blit_position)

    def move(self, surface: Surface):
        self.geometry = self.geometry.update_pos(
            wrap_position(self.geometry.position + self.geometry.velocity, surface)
        )


class Spaceship(GameObject):
    MANEUVERABILITY = 3
    ACCELERATION = 0.05
    BULLET_SPEED = 3
    UP = Vector2(0, -1)

    def __init__(
            self, position: Vector2, create_bullet_callback: Callable[[Any], None]
    ):
        self.create_bullet_callback = create_bullet_callback
        self.direction = Vector2(self.UP)
        super().__init__(position, SpriteLibrary.load("spaceship"), Vector2(0))

    def rotate(self, clockwise: bool = True):
        sign = 1 if clockwise else -1
        angle = self.MANEUVERABILITY * sign
        self.direction.rotate_ip(angle)

    def draw(self, surface: Surface):
        angle = self.direction.angle_to(self.UP)
        rotated_surface = rotozoom(self.sprite, angle, 1.0)
        rotated_surface_size = Vector2(rotated_surface.get_size())
        blit_position: Vector2 = self.geometry.position - rotated_surface_size * 0.5
        surface.blit(rotated_surface, blit_position)

    def accelerate(self):
        self.geometry = self.geometry.update_vel(
            self.geometry.velocity + (self.direction * self.ACCELERATION)
        )

    def shoot(self):
        bullet_velocity = self.direction * self.BULLET_SPEED + self.geometry.velocity
        bullet = Bullet(self.geometry.position, bullet_velocity)
        self.create_bullet_callback(bullet)
        SoundLibrary.play("laser")


class Asteroid(GameObject):
    def __init__(
            self,
            position: Vector2,
            create_asteroid_callback: Callable[[Any], None],
            size: int = 3,
    ):
        self.create_asteroid_callback = create_asteroid_callback
        self.size: int = size
        size_to_scale = {
            3: 1,
            2: 0.5,
            1: 0.25,
        }
        scale = size_to_scale[size]
        sprite = rotozoom(SpriteLibrary.load("asteroid"), 0, scale)

        super().__init__(position, sprite, get_random_velocity(1, 2))

    def split(self):
        SoundLibrary.play("hit_big")
        if self.size > 1:
            for _ in range(2):
                asteroid = Asteroid(
                    self.geometry.position, self.create_asteroid_callback, self.size - 1
                )
                self.create_asteroid_callback(asteroid)


class Bullet(GameObject):
    def __init__(self, position: Vector2, velocity: Vector2):
        super().__init__(position, SpriteLibrary.load("bullet"), velocity)

    def move(self, surface: Surface):
        self.geometry = self.geometry.update_pos(
            self.geometry.position + self.geometry.velocity
        )


class Stats(GameObject):
    def __init__(self):
        self.start_time = time.perf_counter()
        self.font = pygame.font.SysFont(None, 20)
        super().__init__(Vector2(0, 0), None, Vector2(0, 0))

    def draw(self, surface: Surface):
        end_time = time.perf_counter()
        ms_per_frame = 1000 / 60
        ms_since_start = (end_time - self.start_time) * 1000
        ms_wait_time_percent = (ms_since_start / ms_per_frame) * 100

        text_surface = self.font.render(
            str(round(ms_wait_time_percent, 0)) + "%", False, (255, 255, 0)
        )
        surface.blit(text_surface, (0, 0))
        self.start_time = time.perf_counter()

    def move(self, surface: Surface):
        pass
