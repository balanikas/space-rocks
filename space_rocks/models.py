from enum import Enum
from typing import Any, Callable, Dict
from typing import NamedTuple

import pygame
from pygame.math import Vector2
from pygame.surface import Surface
from pygame.transform import rotozoom

import audio as sounds
import graphics as gfx
import animation as anim
from geometry import Geometry
from utils import (
    get_random_velocity,
    get_random_rotation,
    get_resize_factor,
    bounce_edge,
    bounce_other,
    get_blit_position,
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

    def move(self, surface: Surface):
        pass

    def draw(self, surface: Surface):
        pass

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

    def validate(self):
        assert self.damage > 0
        assert self.speed > 0
        assert self.reload > 0


class Bullet(GameObject):  # rename class to weapon
    def __init__(self, props: BulletProperties, position: Vector2, velocity: Vector2):
        super().__init__(
            position,
            gfx.get(props.image, resize=get_resize_factor(0.05)),
            velocity,
        )
        self._p = props
        sounds.play(self._p.sound)

    @property
    def damage(self):
        return self._p.damage

    def move(self, surface: Surface):
        self.geometry = self.geometry.update_pos(
            self.geometry.position + self.geometry.velocity
        )

    def draw(self, surface: Surface):
        blit_position = get_blit_position(self.image, self.geometry)
        surface.blit(self.image, blit_position)

    def resize(self):
        self.image = gfx.get(self._p.image, resize=get_resize_factor(0.03))
        self.reposition()


class EnemyProperties(NamedTuple):
    damage: float
    armor: float
    max_velocity: float
    min_velocity: float
    max_rotation: float
    scale: float
    children: int
    sound_on_destroy: str
    sound_on_impact: str
    image: str
    anim_on_destroy: str

    def validate(self):
        assert self.damage > 0
        assert self.armor > 0
        assert self.max_velocity >= 0
        assert self.min_velocity >= 0
        assert self.scale > 0


class Enemy(GameObject):
    def __init__(
        self,
        properties: Dict[int, EnemyProperties],
        position: Vector2,
        create_enemy_callback: Callable[[Any], None],
        tier: int,
    ):
        self._properties = properties
        self._create_enemy_callback = create_enemy_callback
        self._tier = tier
        self._angle = 0
        self._p = self._properties[self._tier]
        self._scale = self._p.scale
        self._armor = self._p.armor
        self._rotation = get_random_rotation(0, self._p.max_rotation)
        image = rotozoom(
            gfx.get(self._p.image, resize=get_resize_factor(0.1)),
            0,
            self._scale,
        )

        super().__init__(
            position,
            image,
            get_random_velocity(self._p.min_velocity, self._p.max_velocity),
        )

    def resize(self):
        self.image = gfx.get(self._p.image, resize=get_resize_factor(0.1))
        self._scale *= max(window.factor)
        self.reposition()

    def draw(self, surface: Surface):
        if self._rotation > 0:
            self._angle += self._rotation
            rotated_surface = rotozoom(self.image, self._angle, 1)
        else:
            rotated_surface = self.image

        blit_position = get_blit_position(rotated_surface, self.geometry)
        surface.blit(rotated_surface, blit_position)

    def move(self, surface: Surface):
        self.geometry = bounce_edge(surface, 20, 1, self.geometry)
        self.rect.center = self.geometry.position

    def split(self):
        sounds.play(self._p.sound_on_destroy)
        if self._tier > 1:
            for _ in range(self._p.children):
                enemy = Enemy(
                    self._properties,
                    self.geometry.position,
                    self._create_enemy_callback,
                    self._tier - 1,
                )
                self._create_enemy_callback(enemy)

    def hit(self, other: Geometry, damage: float):
        self._armor -= damage
        if self._armor > 0:
            sounds.play(self._p.sound_on_impact)
            self.geometry = bounce_other(self.geometry, other)
        else:
            sounds.play(self._p.sound_on_destroy)
            self.split()

    def get_impact_animation(self):
        return anim.get(
            self._p.anim_on_destroy, self.geometry.position, resize=(200, 200)
        )

    @property
    def damage(self) -> float:
        return self._p.damage

    @property
    def armor(self) -> float:
        return self._armor
