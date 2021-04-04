from enum import Enum
from typing import Any, Callable

import pygame
from pygame import Color
from pygame.font import Font
from pygame.math import Vector2
from pygame.surface import Surface
from pygame.transform import rotozoom

from audio import SoundLibrary
from geometry import Geometry
from graphics import SpriteLibrary
from utils import wrap_position, get_random_velocity


class GameState(Enum):
    RUNNING = 1
    NOT_RUNNING = 2
    LOST = 3
    WON = 4


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
    def __init__(self, clock: pygame.time.Clock):
        self.clock = clock
        self.font = pygame.font.Font(None, 30)
        super().__init__(Vector2(0, 0), None, Vector2(0, 0))

    def draw(self, surface: Surface):
        fps = self.clock.get_fps()

        text_surface = self.font.render(
            str(round(fps, 0)) + "%", False, (255, 255, 0)
        )
        surface.blit(text_surface, (0, 0))

    def move(self, surface: Surface):
        pass


class UI():
    def __init__(self):
        self.font = pygame.font.Font(None, 64)
        self.message = ""

    def _print_text(self, surface: Surface, text: str, font: Font, color: Color = Color("tomato")):
        text_surface: Surface = font.render(text, True, color)
        text_surface.set_colorkey((0, 100, 100))

        rect = text_surface.get_rect()
        rect.center = Vector2(surface.get_size()) / 2
        surface.blit(text_surface, rect)

    def draw(self, surface: Surface, state: GameState):
        if state == GameState.WON:
            self.message = "You won! Press RETURN to replay"
        if state == GameState.LOST:
            self.message = "You lost! Press RETURN to replay"
        if state == GameState.RUNNING:
            self.message = ""
        if state == GameState.NOT_RUNNING:
            self.message = "Press RETURN to start"

        self._print_text(surface, self.message, self.font)


class Background():
    def __init__(self):
        self.background = SpriteLibrary.load("space", False)
        SoundLibrary.play("background")

    def draw(self, surface: Surface):
        surface.blit(self.background, (0, 0))

    def move(self, surface: Surface):
        pass
