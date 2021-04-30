from enum import Enum
from typing import NamedTuple, Callable, Any, Optional

import pygame
from pygame import Vector2, Surface
from pygame.transform import rotozoom

from animation import Animation, AnimationLibrary
from audio import SoundLibrary
from geometry import Geometry
from graphics import SpriteLibrary
from models import GameObject, BulletProperties, Bullet
from utils import get_resize_factor, bounce_edge, bounce_other
from window import window


class ActiveWeapon(Enum):
    PRIMARY = 1
    SECONDARY = 2


class ShipProperties(NamedTuple):
    damage: float
    armor: float
    maneuverability: float
    acceleration: float
    sound_hit: str
    image_name: str
    on_impact: str
    primary_weapon: BulletProperties
    secondary_weapon: BulletProperties

    def validate(self):
        assert self.damage > 0
        assert self.armor > 0
        assert self.maneuverability > 0
        assert self.acceleration > 0


class Ship(GameObject):
    UP = Vector2(0, -1)

    def __init__(
        self,
        properties: ShipProperties,
        position: Vector2,
        create_bullet_callback: Callable[[Any], None],
    ):
        self._p = properties
        self._create_bullet_callback = create_bullet_callback
        self._direction = Vector2(self.UP)
        self._active_weapon = ActiveWeapon.PRIMARY
        self._last_shot = 0
        self._dead = False
        self._armor = self._p.armor
        self._angle = 0

        super().__init__(
            position,
            SpriteLibrary.load(self._p.image_name, resize=get_resize_factor(0.1)),
            Vector2(0),
        )

    @property
    def damage(self):
        return self._p.damage

    @property
    def armor(self):
        return self._armor

    @property
    def direction(self):
        return self._direction

    @property
    def dead(self):
        return self._dead

    def resize(self):
        self.image = SpriteLibrary.load(
            self._p.image_name, resize=get_resize_factor(0.1)
        )
        self.reposition()

    def rotate(self, clockwise: bool = True):
        sign = 1 if clockwise else -1
        angle = self._p.maneuverability * sign
        self._direction.rotate_ip(angle)

    def move(self, surface: Surface):
        self.geometry = bounce_edge(surface, 50, 0.6, self.geometry)
        self.rect.center = self.geometry.position

    def draw(self, surface: Surface):
        if self._dead:
            return

        angle = self._direction.angle_to(self.UP)
        rotated_surface = rotozoom(self.image, angle, 1)
        rotated_surface_size = Vector2(rotated_surface.get_size())
        blit_position = self.geometry.position - rotated_surface_size * 0.5
        surface.blit(rotated_surface, blit_position)

    def accelerate(self):
        self.geometry = self.geometry.update_vel(
            self.geometry.velocity + (self._direction * self._p.acceleration)
        )

    def switch_weapon(self):
        if self._active_weapon == ActiveWeapon.PRIMARY:
            self._active_weapon = ActiveWeapon.SECONDARY
        else:
            self._active_weapon = ActiveWeapon.PRIMARY
        SoundLibrary.play("change_weapon")

    def shoot(self):
        bullet = (
            self._p.primary_weapon
            if self._active_weapon == ActiveWeapon.PRIMARY
            else self._p.secondary_weapon
        )

        if pygame.time.get_ticks() - self._last_shot < bullet.reload:
            return

        self._last_shot = pygame.time.get_ticks()
        bullet_velocity = self._direction * bullet.speed
        bullet_velocity = Vector2(
            bullet_velocity.x * window.factor.x, bullet_velocity.y * window.factor.y
        )
        bullet = Bullet(bullet, self.geometry.position, bullet_velocity)
        self._create_bullet_callback(bullet)

    def hit(self, other: Geometry, damage: float) -> Optional[Animation]:
        self._armor -= damage
        if self._armor > 0:
            SoundLibrary.play(self._p.sound_hit)
            self.geometry = bounce_other(self.geometry, other)
            return None
        else:
            self._dead = True
            SoundLibrary.play(self._p.sound_hit)
            return AnimationLibrary.load(
                self._p.on_impact, self.geometry.position, resize=(200, 200)
            )

    @property
    def active_weapon(self) -> ActiveWeapon:
        return self._active_weapon
