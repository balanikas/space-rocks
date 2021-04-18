import json
import logging
import os
from typing import List, Sequence, Tuple

import jsonschema
from jsonschema import validate
from pygame.surface import Surface

from space_rocks import constants
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
from space_rocks.window import window

logger = logging.getLogger(__name__)


def _load_schema() -> str:
    with open(f"{constants.LEVELS_ROOT}level_schema.json", "r") as read_file:
        return json.load(read_file)


class Level:
    schema = _load_schema()

    def _load_level(self, json_path: str):
        with open(json_path, "r") as read_file:
            data = json.load(read_file)

            try:
                validate(instance=data, schema=self.schema)
            except jsonschema.exceptions.ValidationError as err:
                print(f"invalid json at: {json_path}: " + err.message)
                raise SystemExit

            logger.info(f"{json_path} loaded and appears valid")
            return data

    def __init__(self, screen: Surface, json_path: str):

        self._bullets: List[Bullet] = []

        data = self._load_level(json_path)

        ship = data["ship"]
        props = SpaceshipProperties(
            ship["maneuverability"],
            ship["acceleration"],
            ship["bullet_speed"],
            ship["sound_shoot"],
            ship["sound_hit"],
            "spaceship",
        )
        self._spaceship = Spaceship(props, window.center, self._bullets.append)

        self._asteroids: List[Asteroid] = []
        for a in data["asteroids"]:
            props = {}
            c = len(a["tiers"])
            for t in a["tiers"]:
                props[c] = AsteroidProperties(
                    t["max_velocity"],
                    t["min_velocity"],
                    t["max_rotation"],
                    t["scale"],
                    t["children"],
                    t["sound_hit"],
                    t["sprite_name"],
                )
                c = c -1

            position = get_safe_asteroid_distance(
                screen, self.spaceship.geometry.position
            )

            self._asteroids.append(Asteroid(props, position, self._asteroids.append, len(a["tiers"])))

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
    def load_level(self, screen : Surface, path: str, item: str):
        return lambda: Level(screen, os.path.join(path, item, ".json"))

    def __init__(self, screen: Surface):
        self._levels = {}
        for item in os.listdir(constants.LEVELS_ROOT):
            if not item.startswith(".") and os.path.isdir(os.path.join(constants.LEVELS_ROOT, item)):
                (k, v) = item.split("_")
                self._levels[int(k)] = (item, self.load_level(screen, constants.LEVELS_ROOT, item))

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
