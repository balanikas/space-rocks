import json
import os
from typing import List, Sequence, Tuple

from pygame.surface import Surface

import constants
from space_rocks.models import (
    Background,
    Asteroid,
    Spaceship,
    Bullet,
    AsteroidProperties,
    SpaceshipProperties,
    GameObject,
)
from space_rocks.utils import get_safe_asteroid_distance


class Level:
    def __init__(self, screen: Surface, json_path: str):

        self._bullets: List[Bullet] = []

        with open(json_path, "r") as read_file:
            data = json.load(read_file)
            ship = data["ship"]
            props = SpaceshipProperties(
                ship["maneuverability"],
                ship["acceleration"],
                ship["bullet_speed"],
                ship["sound_shoot"],
            )
            self._spaceship = Spaceship(
                props, "spaceship", constants.SCREEN_CENTER, self._bullets.append
            )

            self._asteroids: List[Asteroid] = []
            for a in data["asteroids"]:
                props = {}
                for k, v in a.items():
                    props[int(k)] = AsteroidProperties(
                        v["max_velocity"],
                        v["min_velocity"],
                        v["max_rotation"],
                        v["scale"],
                        v["children"],
                        v["sound_hit"],
                        v["sprite_name"],
                    )

                position = get_safe_asteroid_distance(
                    screen, self.spaceship.geometry.position
                )

                self._asteroids.append(
                    Asteroid(props, position, self._asteroids.append, 3)
                )

        self._background: Background = Background("background")

    @property
    def background(self) -> Background:
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

    def get_game_objects(self) -> Sequence[GameObject]:
        game_objects = [*self._asteroids, *self._bullets]

        if self._spaceship:
            game_objects.append(self._spaceship)

        return game_objects


class World:
    def load_level(self, screen, path, item):
        return lambda: Level(screen, os.path.join(path, item, ".json"))

    def __init__(self, screen: Surface):
        path = "../levels/"
        self._levels = {}
        for item in os.listdir(path):
            if not item.startswith(".") and os.path.isdir(os.path.join(path, item)):
                (k, v) = item.split("_")
                self._levels[int(k)] = (item, self.load_level(screen, path, item))

        self._current_level_id = -1

    def start_current_level(self):
        if self._current_level_id == -1:
            self._current_level_id = 0
        return self._levels[self._current_level_id][1]()

    def start_next_level(self):
        self.advance_level()
        return self._levels[self._current_level_id][1]()

    def start_level(self, level_id: int):
        return self._levels[level_id][1]()

    def get_current_level(self) -> Tuple[int, str]:
        if self._current_level_id == -1:
            self._current_level_id = 0
        return self._current_level_id, self._levels[self._current_level_id][0]

    def set_current_level(self, level_id: int):
        self._current_level_id = level_id

    def advance_level(self):
        if self._current_level_id >= len(self._levels) - 1:
            self._current_level_id = 0
        elif self._current_level_id == -1:
            self._current_level_id = 0
        else:
            self._current_level_id += 1

    def get_all_levels(self) -> List[Tuple[str, int]]:
        levels = []
        for k, v in self._levels.items():
            levels.append((v[0], k))

        return levels
