from typing import List, Sequence

from pygame import Vector2
from pygame.surface import Surface

from space_rocks.models import Background, Asteroid, Spaceship, Bullet, GameObject
from space_rocks.utils import get_random_position


class Level():
    MIN_ASTEROID_DISTANCE = 250

    def __init__(self, screen: Surface):
        self._background = Background("space")
        self._bullets: List[Bullet] = []
        self._spaceship = Spaceship("spaceship", Vector2(500, 400), self._bullets.append)
        self._asteroids: List[Asteroid] = []
        for _ in range(1):
            while True:
                position = get_random_position(screen)
                if (
                        position.distance_to(self.spaceship.geometry.position)
                        > self.MIN_ASTEROID_DISTANCE
                ):
                    break

            self._asteroids.append(Asteroid("asteroid", position, self._asteroids.append))

    @property
    def background(self):
        return self._background

    @property
    def bullets(self) -> Sequence[Bullet]:
        return self._bullets

    @property
    def spaceship(self):
        return self._spaceship

    @property
    def asteroids(self) -> Sequence[Asteroid]:
        return self._asteroids

    def remove_spaceship(self):
        self._spaceship = None

    def remove_bullet(self, bullet: Bullet):
        self._bullets.remove(bullet)

    def remove_asteroid(self, a: Asteroid):
        self._asteroids.remove(a)

    def get_game_objects(self):
        game_objects = [self._background, *self._asteroids, *self._bullets]

        if self._spaceship:
            game_objects.append(self._spaceship)

        return game_objects


class Level2(Level):
    def __init__(self, screen: Surface):
        self._background = Background("space2")
        self._bullets: List[Bullet] = []
        self._spaceship = Spaceship("spaceship", Vector2(500, 400), self._bullets.append)
        self._asteroids: List[Asteroid] = []
        for _ in range(12):
            while True:
                position = get_random_position(screen)
                if (
                        position.distance_to(self.spaceship.geometry.position)
                        > self.MIN_ASTEROID_DISTANCE
                ):
                    break

            self._asteroids.append(Asteroid("asteroid", position, self._asteroids.append))
