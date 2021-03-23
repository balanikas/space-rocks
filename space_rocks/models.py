from typing import Any, Callable
from pygame.surface import Surface
from pygame.math import Vector2
from utils import load_sprite, wrap_position, get_random_velocity, load_sound
from pygame.transform import rotozoom

UP = Vector2(0, -1)


class GameObject:
    def __init__(self, position: Vector2, sprite: Surface, velocity: Vector2):
        self.position: Vector2 = Vector2(position)
        self.sprite: Surface = sprite
        self.radius: float = sprite.get_width() / 2
        self.velocity: Vector2 = Vector2(velocity)

    def draw(self, surface: Surface):
        blit_position = self.position - Vector2(self.radius)
        surface.blit(self.sprite, blit_position)

    def move(self, surface: Surface):
        self.position = wrap_position(self.position + self.velocity, surface)

    def collides_with(self, other_obj: Any) -> bool:
        distance = self.position.distance_to(other_obj.position)
        return distance < self.radius + other_obj.radius


class Spaceship(GameObject):
    MANEUVERABILITY = 3
    ACCELERATION = 0.05
    BULLET_SPEED = 3

    def __init__(self, position: Vector2, create_bullet_callback: Callable[[Any], None]):
        self.create_bullet_callback = create_bullet_callback
        self.direction = Vector2(UP)
        self.laser_sound = load_sound("laser")
        super().__init__(position, load_sprite("spaceship"), Vector2(0))

    def rotate(self, clockwise: bool = True):
        sign = 1 if clockwise else -1
        angle = self.MANEUVERABILITY * sign
        self.direction.rotate_ip(angle)

    def draw(self, surface: Surface):
        angle = self.direction.angle_to(UP)
        rotated_surface = rotozoom(self.sprite, angle, 1.0)
        rotated_surface_size = Vector2(rotated_surface.get_size())
        blit_position: Vector2 = self.position - rotated_surface_size * 0.5
        surface.blit(rotated_surface, blit_position)

    def accelerate(self):
        self.velocity += self.direction * self.ACCELERATION

    def shoot(self):
        bullet_velocity = self.direction * self.BULLET_SPEED + self.velocity
        bullet = Bullet(self.position, bullet_velocity)
        self.create_bullet_callback(bullet)
        self.laser_sound.play()


class Asteroid(GameObject):
    def __init__(
        self,
        position: Vector2,
        create_asteroid_callback: Callable[[Any], None],
        size: int = 3,
    ):
        self.create_asteroid_callback = create_asteroid_callback
        self.size: int = size
        self.hit_big_sound = load_sound("hit_big")
        self.hit_sound = load_sound("hit")

        size_to_scale = {
            3: 1,
            2: 0.5,
            1: 0.25,
        }
        scale = size_to_scale[size]
        sprite = rotozoom(load_sprite("asteroid"), 0, scale)

        super().__init__(position, sprite, get_random_velocity(1, 2))

    def split(self):
        self.hit_big_sound.play()
        if self.size > 1:
            for _ in range(2):
                asteroid = Asteroid(self.position, self.create_asteroid_callback, self.size - 1)
                self.create_asteroid_callback(asteroid)


class Bullet(GameObject):
    def __init__(self, position: Vector2, velocity: Vector2):
        super().__init__(position, load_sprite("bullet"), velocity)

    def move(self, surface: Surface):
        self.position = self.position + self.velocity