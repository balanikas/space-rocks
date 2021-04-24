from enum import Enum
from typing import Any, Callable, Dict, Optional
from typing import NamedTuple

import pygame
from pygame.math import Vector2
from pygame.surface import Surface
from pygame.transform import rotozoom

from animation import AnimationLibrary, Animation
from audio import SoundLibrary
from geometry import Geometry
from graphics import SpriteLibrary
from utils import (
    wrap_position,
    get_random_velocity,
    get_random_rotation,
    get_resize_factor,
    bounce_edge,
    bounce_other,
)
from window import window


class GameState(Enum):
    RUNNING = 1
    NOT_RUNNING = 2
    LOST = 3
    WON = 4
    LOADING_LEVEL = 5


class GameObject(pygame.sprite.Sprite):
    def __init__(self, position: Vector2, image: Surface, velocity: Vector2):
        super(GameObject, self).__init__()
        self.image: Surface = image
        self.geometry: Geometry = Geometry(position, image.get_width() / 2, velocity)
        self.rect: pygame.rect.Rect = self.image.get_rect(center=position)

    def draw(self, surface: Surface):
        blit_position = self.geometry.position - Vector2(self.geometry.radius)
        surface.blit(self.image, blit_position)

    def move(self, surface: Surface):
        self.geometry = wrap_position(surface, self.geometry)

    def reposition(self):
        new_pos = Vector2(
            window.factor.x * self.geometry.position.x,
            window.factor.y * self.geometry.position.y,
        )
        self.geometry = self.geometry.update_pos(new_pos)


class BulletProperties(NamedTuple):
    damage: float
    speed: float
    sound: str
    reload: int
    image: str


class Bullet(GameObject):  # rename class to weapon
    def __init__(self, props: BulletProperties, position: Vector2, velocity: Vector2):
        super().__init__(
            position,
            SpriteLibrary.load(props.image, resize=get_resize_factor(0.03)),
            velocity,
        )
        self._p = props
        SoundLibrary.play(self._p.sound)

    @property
    def damage(self):
        return self._p.damage

    def move(self, surface: Surface):
        self.geometry = self.geometry.update_pos(
            self.geometry.position + self.geometry.velocity
        )

    def resize(self):
        self.image = SpriteLibrary.load(self._p.image, resize=get_resize_factor(0.03))
        self.reposition()


class AsteroidProperties(NamedTuple):
    damage: float
    armor: float
    max_velocity: float
    min_velocity: float
    max_rotation: float
    scale: float
    children: int
    sound_destroy: str
    sound_hit: str
    sprite_name: str
    on_impact: str


class Asteroid(GameObject):
    def __init__(
        self,
        properties: Dict[int, AsteroidProperties],
        position: Vector2,
        create_asteroid_callback: Callable[[Any], None],
        tier: int,
    ):
        self._properties = properties
        self._create_asteroid_callback = create_asteroid_callback
        self._tier: int = tier
        self._angle = 0
        self._p = self._properties[self._tier]
        self._scale = self._p.scale

        self._armor = self._p.armor
        self._rotation = get_random_rotation(0, self._p.max_rotation)
        image = rotozoom(
            SpriteLibrary.load(self._p.sprite_name, resize=get_resize_factor(0.1)),
            0,
            self._scale,
        )

        super().__init__(
            position,
            image,
            get_random_velocity(self._p.min_velocity, self._p.max_velocity),
        )

    def resize(self):
        self.image = SpriteLibrary.load(
            self._p.sprite_name, resize=get_resize_factor(0.1)
        )
        self._scale *= max(window.factor)
        self.reposition()

    def draw(self, surface: Surface):

        if self._rotation > 0:
            self._angle += self._rotation
            rotated_surface = rotozoom(self.image, self._angle, 1)
        else:
            rotated_surface = self.image

        rotated_surface_size = Vector2(rotated_surface.get_size())
        blit_position: Vector2 = self.geometry.position - rotated_surface_size * 0.5
        surface.blit(rotated_surface, blit_position)

    def move(self, surface: Surface):
        self.geometry = bounce_edge(surface, 20, 1, self.geometry)
        self.rect.center = self.geometry.position

    def split(self):
        SoundLibrary.play(self._p.sound_destroy)
        if self._tier > 1:
            for _ in range(self._p.children):
                asteroid = Asteroid(
                    self._properties,
                    self.geometry.position,
                    self._create_asteroid_callback,
                    self._tier - 1,
                )
                self._create_asteroid_callback(asteroid)

    def hit(self, other: Geometry, damage: float) -> Optional[Animation]:
        self._armor -= damage
        if self._armor > 0:
            SoundLibrary.play(self._p.sound_hit)
            self.geometry = bounce_other(self.geometry, other)
            return None
        else:
            SoundLibrary.play(self._p.sound_destroy)
            self.split()
            return AnimationLibrary.load(
                self._p.on_impact, self.geometry.position, resize=(200, 200)
            )

    @property
    def damage(self):
        return self._p.damage

    @property
    def armor(self):
        return self._armor
