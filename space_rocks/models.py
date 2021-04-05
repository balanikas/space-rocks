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
    def __init__(
            self,
            position: Vector2,
            sprite: Surface,
            velocity: Vector2):
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


class SpaceshipProperties:
    def __init__(self, maneuverability: float, acceleration: float, bullet_speed: float):
        self.maneuverability = maneuverability
        self.acceleration = acceleration
        self.bullet_speed = bullet_speed


class Spaceship(GameObject):
    UP = Vector2(0, -1)

    def __init__(
            self,
            properties: SpaceshipProperties,
            sprite_name: str,
            position: Vector2,
            create_bullet_callback: Callable[[Any], None]
    ):
        self._properties = properties
        self._create_bullet_callback = create_bullet_callback
        self._direction = Vector2(self.UP)
        super().__init__(position, SpriteLibrary.load(sprite_name), Vector2(0))

    def rotate(self, clockwise: bool = True):
        sign = 1 if clockwise else -1
        angle = self._properties.maneuverability * sign
        self._direction.rotate_ip(angle)

    def draw(self, surface: Surface):
        angle = self._direction.angle_to(self.UP)
        rotated_surface = rotozoom(self.sprite, angle, 1.0)
        rotated_surface_size = Vector2(rotated_surface.get_size())
        blit_position: Vector2 = self.geometry.position - rotated_surface_size * 0.5
        surface.blit(rotated_surface, blit_position)

    def accelerate(self):
        self.geometry = self.geometry.update_vel(
            self.geometry.velocity + (self._direction * self._properties.acceleration)
        )

    def shoot(self):
        bullet_velocity = self._direction * self._properties.bullet_speed + self.geometry.velocity
        bullet = Bullet("bullet", self.geometry.position, bullet_velocity)
        self._create_bullet_callback(bullet)
        SoundLibrary.play("laser")


class AsteroidProperties:
    def __init__(self, min_velocity: int, max_velocity: int):
        self.min_velocity = min_velocity
        self.max_velocity = max_velocity


class Asteroid(GameObject):
    def __init__(
            self,
            properties: AsteroidProperties,
            sprite_name: str,
            position: Vector2,
            create_asteroid_callback: Callable[[Any], None],
            size: int,
    ):
        self._properties = properties
        self._sprite_name = sprite_name
        self._create_asteroid_callback = create_asteroid_callback
        self._size: int = size
        size_to_scale = {
            4: 2,
            3: 1,
            2: 0.5,
            1: 0.25,
        }
        scale = size_to_scale[size]
        sprite = rotozoom(SpriteLibrary.load(self._sprite_name), 0, scale)

        super().__init__(position, sprite,
                         get_random_velocity(self._properties.min_velocity, self._properties.max_velocity))

    def split(self):
        SoundLibrary.play("hit_big")
        if self._size > 1:
            for _ in range(2):
                asteroid = Asteroid(
                    self._properties,
                    self._sprite_name,
                    self.geometry.position,
                    self._create_asteroid_callback,
                    self._size - 1)
                self._create_asteroid_callback(asteroid)


class Bullet(GameObject):
    def __init__(
            self,
            sprite_name: str,
            position: Vector2,
            velocity: Vector2):
        super().__init__(position, SpriteLibrary.load(sprite_name), velocity)

    def move(self, surface: Surface):
        self.geometry = self.geometry.update_pos(
            self.geometry.position + self.geometry.velocity
        )


class Stats(GameObject):
    def __init__(
            self,
            clock: pygame.time.Clock):
        self._clock = clock
        self._font = pygame.font.Font(None, 30)
        super().__init__(Vector2(0, 0), None, Vector2(0, 0))

    def draw(self, surface: Surface):
        fps = self._clock.get_fps()

        text_surface = self._font.render(
            str(round(fps, 0)) + " fps", False, (255, 255, 0)
        )
        surface.blit(text_surface, (0, 0))

    def move(self, surface: Surface):
        pass


class UI:
    def __init__(self):
        self._font = pygame.font.Font(None, 64)
        self._message = ""

    def _print_text(self, surface: Surface, text: str, font: Font, color: Color = Color("white")):
        text_surface: Surface = font.render(text, True, color)

        rect = text_surface.get_rect()
        rect.center = Vector2(surface.get_size()) / 2
        surface.blit(text_surface, rect)

    def draw(self, surface: Surface, state: GameState):
        if state == GameState.WON:
            self._message = "You won! Press RETURN to replay"
        if state == GameState.LOST:
            self._message = "You lost! Press RETURN to replay"
        if state == GameState.RUNNING:
            self._message = ""
        if state == GameState.NOT_RUNNING:
            self._message = "Press RETURN to start"

        self._print_text(surface, self._message, self._font)


class Background:
    def __init__(self, sprite_name: str):
        self._background = SpriteLibrary.load(sprite_name, False)

    def draw(self, surface: Surface):
        surface.blit(self._background, (0, 0))

    def move(self, surface: Surface):
        pass
