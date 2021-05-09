from enum import Enum
from typing import NamedTuple, Callable, Any

import pygame
from pygame import Vector2
from pygame.surface import Surface

import space_rocks.animation as anim
import space_rocks.audio as  sounds
import space_rocks.graphics as gfx
from space_rocks.geometry import Geometry
from space_rocks.models import Bullet, BulletProperties, GameObject
from space_rocks.utils import bounce_other, get_blit_position, scale_and_rotate, bounce_edge, get_resize_factor
from space_rocks.window import window


class ActiveWeapon(Enum):
    PRIMARY = 1
    SECONDARY = 2


class PlayerProperties(NamedTuple):
    damage: float
    armor: float
    maneuverability: float
    acceleration: float
    sound_on_impact: str
    image_name: str
    anim_on_destroy: str
    primary_weapon: BulletProperties
    secondary_weapon: BulletProperties

    def validate(self):
        assert self.damage > 0
        assert self.armor > 0
        assert self.maneuverability > 0
        assert self.acceleration > 0


class Player(GameObject):
    UP = Vector2(0, -1)

    def __init__(
            self,
            properties: PlayerProperties,
            position: Vector2,
            create_bullet_callback: Callable[[Any], None],
    ):
        self._p = properties
        self._create_bullet_callback = create_bullet_callback
        self._direction = Vector2(self.UP)
        self._active_weapon = ActiveWeapon.PRIMARY
        self._last_shot = 0
        self._armor = self._p.armor
        self._angle = 0

        super().__init__(
            position,
            gfx.get(self._p.image_name, resize=get_resize_factor(0.1)),
            Vector2(0),
        )

        self._rotated_image = self.image

    @property
    def damage(self):
        return self._p.damage

    @property
    def armor(self):
        return self._armor

    @property
    def direction(self):
        return self._direction

    def resize(self):
        self.image = gfx.get(self._p.image_name, resize=get_resize_factor(0.1))
        self.reposition()

    def rotate(self, clockwise: bool = True):
        sign = 1 if clockwise else -1
        angle = self._p.maneuverability * sign
        self._direction = self._direction.rotate(angle)

    def move(self, surface: Surface):
        self.geometry = bounce_edge(surface, 50, 0.6, self.geometry)
        self.rect.center = (int(self.geometry.position.x), int(self.geometry.position.y))

    def draw(self, surface: Surface):
        if self.armor <= 0:
            return

        angle = self._direction.angle_to(self.UP)
        if angle != self._angle:
            rotated_surface = scale_and_rotate(self.image, angle, 1)
            self._rotated_image = rotated_surface
            self._angle = angle
        else:
            rotated_surface = self._rotated_image

        blit_position = get_blit_position(rotated_surface, self.geometry.position)

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
        sounds.play("change_weapon")

    def shoot(self):
        w = (
            self._p.primary_weapon
            if self._active_weapon == ActiveWeapon.PRIMARY
            else self._p.secondary_weapon
        )

        if pygame.time.get_ticks() - self._last_shot < w.reload:
            return

        self._last_shot = pygame.time.get_ticks()
        weapon_velocity = self._direction * w.speed
        weapon_velocity = Vector2(
            weapon_velocity.x * window.factor.x, weapon_velocity.y * window.factor.y
        )
        w = Bullet(w, self.geometry.position, weapon_velocity)
        self._create_bullet_callback(w)

    def hit(self, other: Geometry, damage: float):
        self._armor -= damage
        if self._armor > 0:
            sounds.play(self._p.sound_on_impact)
            self.geometry = bounce_other(self.geometry, other)
        else:
            sounds.play(self._p.sound_on_impact)

    def get_impact_animation(self):
        return anim.get(
            self._p.anim_on_destroy, self.geometry.position, resize=(200, 200)
        )

    @property
    def active_weapon(self) -> ActiveWeapon:
        return self._active_weapon
