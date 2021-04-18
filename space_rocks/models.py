from enum import Enum
from typing import Any, Callable, Dict

import pygame
from pygame import Color
from pygame.font import Font
from pygame.math import Vector2
from pygame.surface import Surface
from pygame.transform import rotozoom

from audio import SoundLibrary
from geometry import Geometry
from graphics import SpriteLibrary
from space_rocks.window import window
from utils import (
    wrap_position,
    get_random_velocity,
    get_random_rotation,
    get_resize_factor,
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
        if image:
            self.image: Surface = image
            self.geometry: Geometry = Geometry(
                position, image.get_width() / 2, velocity
            )

        if hasattr(self, "image"):
            self.rect: pygame.rect.Rect = self.image.get_rect(center=position)

    def draw(self, surface: Surface):
        blit_position = self.geometry.position - Vector2(self.geometry.radius)
        surface.blit(self.image, blit_position)

    def move(self, surface: Surface):
        self.geometry = self.geometry.update_pos(
            wrap_position(self.geometry.position + self.geometry.velocity, surface)
        )

    def reposition(self):
        new_pos = Vector2(
            window.factor.x * self.geometry.position.x,
            window.factor.y * self.geometry.position.y,
        )
        self.geometry = self.geometry.update_pos(new_pos)


class SpaceshipProperties:
    def __init__(
        self,
        maneuverability: float,
        acceleration: float,
        bullet_speed: float,
        sound_shoot: str,
        image_name: str,
    ):
        self.maneuverability = maneuverability
        self.acceleration = acceleration
        self.bullet_speed = bullet_speed
        self.sound_shoot = sound_shoot
        self.image_name = image_name


class Spaceship(GameObject):
    UP = Vector2(0, -1)

    def __init__(
        self,
        properties: SpaceshipProperties,
        position: Vector2,
        create_bullet_callback: Callable[[Any], None],
    ):
        self._properties = properties
        self._create_bullet_callback = create_bullet_callback
        self._direction = Vector2(self.UP)
        self._edge_distance = 50

        super().__init__(
            position,
            SpriteLibrary.load(
                self._properties.image_name, resize=get_resize_factor(0.1)
            ),
            Vector2(0),
        )

    def resize(self):
        self.image = SpriteLibrary.load(
            self._properties.image_name, resize=get_resize_factor(0.1)
        )
        self.reposition()

    def rotate(self, clockwise: bool = True):
        sign = 1 if clockwise else -1
        angle = self._properties.maneuverability * sign
        self._direction.rotate_ip(angle)

    def move(self, surface: Surface):

        position = self.geometry.position + self.geometry.velocity
        w, h = surface.get_size()
        e = self._edge_distance
        if position.x >= w - e or position.x <= e:
            vel = self.geometry.velocity
            vel.x = (vel.x * 0.6) * -1
        if position.y >= h - e or position.y <= e:
            vel = self.geometry.velocity
            vel.y = (vel.y * 0.6) * -1

        self.geometry = self.geometry.update_pos(position)

    def draw(self, surface: Surface):
        angle = self._direction.angle_to(self.UP)
        rotated_surface = rotozoom(self.image, angle, 1)
        rotated_surface_size = Vector2(rotated_surface.get_size())
        blit_position: Vector2 = self.geometry.position - rotated_surface_size * 0.5
        surface.blit(rotated_surface, blit_position)

    def accelerate(self):
        self.geometry = self.geometry.update_vel(
            self.geometry.velocity + (self._direction * self._properties.acceleration)
        )

    def shoot(self):
        bullet_velocity = (
            self._direction * self._properties.bullet_speed + self.geometry.velocity
        )
        bullet = Bullet("bullet", self.geometry.position, bullet_velocity)
        self._create_bullet_callback(bullet)
        SoundLibrary.play(self._properties.sound_shoot)


class AsteroidProperties:
    def __init__(
        self,
        min_velocity: int,
        max_velocity: int,
        max_rotation: float,
        scale: float,
        children: int,
        sound_hit: str,
        sprite_name: str,
    ):
        self.min_velocity = min_velocity
        self.max_velocity = max_velocity
        self.max_rotation = max_rotation
        self.scale = scale
        self.children = children
        self.sound_hit = sound_hit
        self.sprite_name = sprite_name


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
        self._direction = Vector2(0, -1)
        self._angle = 0

        self._props: AsteroidProperties = self._properties[self._tier]
        self._rotation = get_random_rotation(0, self._props.max_rotation)

        sprite = rotozoom(
            SpriteLibrary.load(self._props.sprite_name, resize=get_resize_factor(0.1)),
            0,
            self._props.scale,
        )

        super().__init__(
            position,
            sprite,
            get_random_velocity(self._props.min_velocity, self._props.max_velocity),
        )

    def resize(self):
        self.image = SpriteLibrary.load(
            self._props.sprite_name, resize=get_resize_factor(0.1)
        )
        self._props.scale *= max(window.factor)
        self.reposition()

    def draw(self, surface: Surface):
        self._angle += self._rotation
        self._direction.rotate_ip(self._angle)

        rotated_surface = rotozoom(self.image, self._angle, 1)
        rotated_surface_size = Vector2(rotated_surface.get_size())
        blit_position: Vector2 = self.geometry.position - rotated_surface_size * 0.5
        surface.blit(rotated_surface, blit_position)

    def split(self):
        SoundLibrary.play(self._props.sound_hit)
        if self._tier > 1:
            for _ in range(self._props.children):
                asteroid = Asteroid(
                    self._properties,
                    self.geometry.position,
                    self._create_asteroid_callback,
                    self._tier - 1,
                )
                self._create_asteroid_callback(asteroid)


class Bullet(GameObject):
    def __init__(self, sprite_name: str, position: Vector2, velocity: Vector2):
        super().__init__(
            position,
            SpriteLibrary.load(sprite_name, resize=get_resize_factor(0.03)),
            velocity,
        )
        self._sprite_name = sprite_name

    def move(self, surface: Surface):
        self.geometry = self.geometry.update_pos(
            self.geometry.position + self.geometry.velocity
        )

    def resize(self):
        self.image = SpriteLibrary.load(
            self._sprite_name, resize=get_resize_factor(0.03)
        )
        self.reposition()


class Stats:
    def __init__(self, clock: pygame.time.Clock):
        self._clock = clock
        self._font = pygame.font.Font(None, 30)

    def draw(self, surface: Surface, pos: Vector2, vel: Vector2, dir: Vector2):
        fps = self._clock.get_fps()

        text_surface = self._font.render(
            f"{round(fps, 0)} fps | x:{round(pos.x, 1)} y:{round(pos.y, 1)} | vel: {vel} | dir: {dir} | "
            f"win:{window.size} | "
            f"display: {(pygame.display.Info().current_w, pygame.display.Info().current_h)}",
            False,
            (255, 255, 0),
        )
        surface.blit(text_surface, (0, 0))

    def move(self, surface: Surface):
        pass


class UI:
    def __init__(self):
        self._font = pygame.font.Font(None, 64)
        self._message = ""
        self._sound_played = False

    def _print_text(
        self, surface: Surface, text: str, font: Font, color: Color = Color("white")
    ):
        text_surface: Surface = font.render(text, True, color)

        rect = text_surface.get_rect()
        rect.center = Vector2(surface.get_size()) / 2
        surface.blit(text_surface, rect)

    def draw(self, surface: Surface, state: GameState):
        if state == GameState.WON:
            self._message = "You won! Press RETURN to continue"
            if not self._sound_played:
                SoundLibrary.play("win_level")
                self._sound_played = not self._sound_played
        elif state == GameState.LOST:
            self._message = "You lost! Press RETURN to restart"
            if not self._sound_played:
                SoundLibrary.play("game_over")
                self._sound_played = not self._sound_played
        elif state == GameState.RUNNING:
            self._sound_played = False
            self._message = ""
        elif state == GameState.NOT_RUNNING:
            self._message = "Press RETURN to start"

        self._print_text(surface, self._message, self._font)


class Background:
    def _initialize(self):
        self._background = SpriteLibrary.load(
            self._sprite_name, False, resize=get_resize_factor(1.2)
        )

        (s_x, s_y) = self._background.get_size()
        x = ((s_x - window.width) / 2) * -1
        y = ((s_y - window.height) / 2) * -1
        self._offset = (x, y)
        self._position = Vector2(0, 0)

    def __init__(self, sprite_name: str):
        self._sprite_name = sprite_name
        self._initialize()

        SoundLibrary.play(
            "background", True
        )  # better to create new method playForever ?

    def draw(self, surface: Surface, pos: Vector2):
        self._position = (
            pos - Vector2(window.center)
        ) * -0.2  # ensures background moves slower than ship
        self._position += self._offset

        surface.blit(self._background, self._position)

    def resize(self):
        self._initialize()


class Animation:
    def animstrip(self, img, width=0):
        if not width:
            width = img.get_height()
        size = width, img.get_height()
        images = []
        orig_alpha = img.get_alpha()
        orig_ckey = img.get_colorkey()
        img.set_colorkey(None)
        img.set_alpha(None)
        for x in range(0, img.get_width(), width):
            i = pygame.Surface(size)
            i.blit(img, (0, 0), ((x, 0), size))
            if orig_alpha:
                i.set_colorkey((0, 0, 0))
            elif orig_ckey:
                i.set_colorkey(orig_ckey)

            i = pygame.transform.scale(i, get_resize_factor(0.07))
            images.append(i.convert())
        img.set_alpha(orig_alpha)
        img.set_colorkey(orig_ckey)
        return images

    def __init__(self, image_name: str, position: Vector2):

        img = SpriteLibrary.load(image_name, False)
        self._images = self.animstrip(img)
        self._time = 0.0
        self._img_index = 0
        self._position = position

    @property
    def done(self):
        return self._img_index >= len(self._images) - 1

    def move(self):
        self._time += 1
        if self._time > 1:
            self._img_index += 1
            self._time = 0

    def draw(self, surface: Surface):
        if self.done:
            return

        img = self._images[self._img_index]
        blit_position: Vector2 = self._position - Vector2(img.get_size()) * 0.5
        surface.blit(img, blit_position)
