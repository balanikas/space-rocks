from typing import List, Sequence

from pygame import Vector2
from pygame.surface import Surface

import constants
from space_rocks.models import Background, Asteroid, Spaceship, Bullet, AsteroidProperties, SpaceshipProperties
from space_rocks.utils import get_random_position


class Level:
    MIN_ASTEROID_DISTANCE = 250

    def __init__(self):
        self._background: Background = Background("level0")
        self._bullets: List[Bullet] = []
        self._spaceship: Spaceship
        self._asteroids: List[Asteroid] = []

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


class Level1(Level):
    def __init__(self, screen: Surface):
        self._background = Background("level1")
        self._bullets: List[Bullet] = []
        props = SpaceshipProperties(5, 0.15, 5, "laser")
        self._spaceship = Spaceship(props, "spaceship",
                                    Vector2(constants.SCREEN_WIDTH / 2, constants.SCREEN_HEIGHT / 2),
                                    self._bullets.append)
        self._asteroids: List[Asteroid] = []
        for _ in range(3):
            while True:
                position = get_random_position(screen)
                if (
                        position.distance_to(self.spaceship.geometry.position)
                        > self.MIN_ASTEROID_DISTANCE
                ):
                    break
            properties = AsteroidProperties(1, 2, "hit_big", {
                4: 2,
                3: 1,
                2: 0.5,
                1: 0.25,
            })
            self._asteroids.append(Asteroid(properties, "asteroid", position, self._asteroids.append, 3))


class Level2(Level):
    def __init__(self, screen: Surface):
        self._background = Background("level2")
        self._bullets: List[Bullet] = []
        props = SpaceshipProperties(3, 0.05, 3, "laser")
        self._spaceship = Spaceship(props, "spaceship",
                                    Vector2(constants.SCREEN_WIDTH / 2, constants.SCREEN_HEIGHT / 2),
                                    self._bullets.append)
        self._asteroids: List[Asteroid] = []
        for _ in range(6):
            while True:
                position = get_random_position(screen)
                if (
                        position.distance_to(self.spaceship.geometry.position)
                        > self.MIN_ASTEROID_DISTANCE
                ):
                    break
            properties = AsteroidProperties(1, 3, "hit_big",
                                            {
                                                4: 2,
                                                3: 1,
                                                2: 0.5,
                                                1: 0.25,
                                            })
            self._asteroids.append(Asteroid(properties, "asteroid", position, self._asteroids.append, 4))


class Level3(Level):
    def __init__(self, screen: Surface):
        self._background = Background("level3")
        self._bullets: List[Bullet] = []
        props = SpaceshipProperties(3, 0.05, 3, "laser")
        self._spaceship = Spaceship(props, "spaceship",
                                    Vector2(constants.SCREEN_WIDTH / 2, constants.SCREEN_HEIGHT / 2),
                                    self._bullets.append)
        self._asteroids: List[Asteroid] = []
        for _ in range(20):
            while True:
                position = get_random_position(screen)
                if (
                        position.distance_to(self.spaceship.geometry.position)
                        > self.MIN_ASTEROID_DISTANCE
                ):
                    break
            properties = AsteroidProperties(2, 4, "hit_big", {
                4: 2,
                3: 1,
                2: 0.5,
                1: 0.25,
            })
            self._asteroids.append(Asteroid(properties, "asteroid", position, self._asteroids.append, 2))


class World:
    def __init__(self, screen: Surface):

        self._levels = {
            0: lambda: Level1(screen),
            1: lambda: Level2(screen),
            2: lambda: Level3(screen),
        }
        self._current_level_id = -1

    def get_current_level(self):
        if self._current_level_id == -1:
            self._current_level_id = 0
        return self._levels[self._current_level_id]()

    def get_next_level(self):
        if self._current_level_id >= len(self._levels) - 1:
            self._current_level_id = 0
        elif self._current_level_id == -1:
            self._current_level_id = 0
        else:
            self._current_level_id += 1

        return self._levels[self._current_level_id]()

    def get_level(self, level_id: int):
        return self._levels[level_id]()
