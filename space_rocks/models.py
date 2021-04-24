import random
from enum import Enum
from typing import Any, Callable, Dict
from typing import NamedTuple
import pygame
from pygame.math import Vector2
from pygame.surface import Surface
from pygame.transform import rotozoom

from audio import SoundLibrary
from geometry import Geometry
from graphics import SpriteLibrary
from animation import AnimationLibrary, Animation
from window import window
from utils import (
    wrap_position,
    get_random_velocity,
    get_random_rotation,
    get_resize_factor,
    bounce_edge,
)


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
    def props(self):
        return self._p

    def move(self, surface: Surface):
        self.geometry = self.geometry.update_pos(
            self.geometry.position + self.geometry.velocity
        )

    def resize(self):
        self.image = SpriteLibrary.load(
            self.props.image, resize=get_resize_factor(0.03)
        )
        self.reposition()


class SpaceshipProperties(NamedTuple):
    maneuverability: float
    acceleration: float
    sound_hit: str
    image_name: str
    on_impact: str
    primary_weapon: BulletProperties
    secondary_weapon: BulletProperties


class ActiveWeapon(Enum):
    PRIMARY = 1
    SECONDARY = 2


class Spaceship(GameObject):
    UP = Vector2(0, -1)

    def __init__(
        self,
        properties: SpaceshipProperties,
        position: Vector2,
        create_bullet_callback: Callable[[Any], None],
    ):
        self._p = properties
        self._create_bullet_callback = create_bullet_callback
        self._direction = Vector2(self.UP)
        self._active_weapon = ActiveWeapon.PRIMARY
        self._last_shot = 0
        self._dead = False

        super().__init__(
            position,
            SpriteLibrary.load(self._p.image_name, resize=get_resize_factor(0.1)),
            Vector2(0),
        )

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

    def draw(self, surface: Surface):
        if self._dead:
            return

        angle = self._direction.angle_to(self.UP)
        rotated_surface = rotozoom(self.image, angle, 1)
        rotated_surface_size = Vector2(rotated_surface.get_size())
        blit_position: Vector2 = self.geometry.position - rotated_surface_size * 0.5
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

    def shoot(self):
        bullet = (
            self._p.primary_weapon
            if self._active_weapon == ActiveWeapon.PRIMARY
            else self._p.secondary_weapon
        )

        if pygame.time.get_ticks() - self._last_shot < bullet.reload:
            return

        self._last_shot = pygame.time.get_ticks()
        bullet_velocity = self._direction * bullet.speed + self.geometry.velocity
        bullet_velocity = Vector2(
            bullet_velocity.x * window.factor.x, bullet_velocity.y * window.factor.y
        )
        bullet = Bullet(bullet, self.geometry.position, bullet_velocity)
        self._create_bullet_callback(bullet)

    def hit(self) -> Animation:
        SoundLibrary.play(self._p.sound_hit)
        self._dead = True

        return AnimationLibrary.load(
            self._p.on_impact, self.geometry.position, 1, resize=(200, 200)
        )


class AsteroidProperties(NamedTuple):
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
        self._armor = self._p.armor
        self._rotation = get_random_rotation(0, self._p.max_rotation)
        image = rotozoom(
            SpriteLibrary.load(self._p.sprite_name, resize=get_resize_factor(0.1)),
            0,
            self._p.scale,
        )

        super().__init__(
            position,
            image,
            get_random_velocity(self._p.min_velocity, self._p.max_velocity),
        )

    @property
    def props(self):
        return self._p

    def resize(self):
        self.image = SpriteLibrary.load(
            self._p.sprite_name, resize=get_resize_factor(0.1)
        )
        self._p.scale *= max(window.factor)
        self.reposition()

    def draw(self, surface: Surface):
        self._angle += self._rotation
        rotated_surface = rotozoom(self.image, self._angle, 1)
        rotated_surface_size = Vector2(rotated_surface.get_size())
        blit_position: Vector2 = self.geometry.position - rotated_surface_size * 0.5
        surface.blit(rotated_surface, blit_position)

    def move(self, surface: Surface):
        self.geometry = bounce_edge(surface, 20, 1, self.geometry)

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

    def hit(self, bullet_vel: Vector2, damage: float):
        SoundLibrary.play(self._p.sound_hit)
        self._armor -= damage
        # todo make vel change dep on scale so small asteroids knock back hardder?
        self.geometry = self.geometry.update_vel(
            self.geometry.velocity + (bullet_vel * random.uniform(0.2, 0.4))
        )

    def destroy(self) -> Animation:
        SoundLibrary.play(self._p.sound_destroy)
        return AnimationLibrary.load(
            self._p.on_impact, self.geometry.position, 1, resize=(200, 200)
        )

    def get_armor(self):
        return self._armor
