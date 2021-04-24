import json
import logging
import os
from typing import List, Sequence, Tuple

import jsonschema
from jsonschema import validate
from pygame.surface import Surface

import constants
from models import (
    Background,
    Asteroid,
    Spaceship,
    Bullet,
    AsteroidProperties,
    SpaceshipProperties,
    GameObject,
    BulletProperties,
)

from utils import get_safe_asteroid_distance
from window import window

logger = logging.getLogger(__name__)


def _load_schema() -> str:
    with open(f"{constants.LEVELS_ROOT}level_schema.json", "r") as read_file:
        return json.load(read_file)


class Level:
    _schema = _load_schema()

    def _load_level(self, json_path: str):
        with open(json_path, "r") as read_file:
            data = json.load(read_file)

            try:
                validate(instance=data, schema=self._schema)
            except jsonschema.exceptions.ValidationError as err:
                logger.error(f"invalid json at: {json_path}: " + err.message)
                raise SystemExit

            logger.info(f"{json_path} loaded and appears valid")
            return data

    def __init__(self, screen: Surface, json_path: str):
        self._bullets: List[Bullet] = []
        data = self._load_level(json_path)
        ship = data["ship"]
        prim = ship["primary_weapon"]
        primary_weapon = BulletProperties(
            prim["damage"],
            prim["speed"],
            prim["sound"],
            prim["reload"],
            prim["image"],
        )

        sec = ship["secondary_weapon"]
        secondary_weapon = BulletProperties(
            sec["damage"],
            sec["speed"],
            sec["sound"],
            sec["reload"],
            sec["image"],
        )

        props = SpaceshipProperties(
            ship["maneuverability"],
            ship["acceleration"],
            ship["sound_hit"],
            "spaceship",
            ship["on_impact"],
            primary_weapon,
            secondary_weapon,
        )

        self._spaceship = Spaceship(props, window.center, self._bullets.append)
        self._asteroids: List[Asteroid] = []

        for a in data["asteroids"]:
            props = {}
            c = len(a["tiers"])
            for t in a["tiers"]:
                props[c] = AsteroidProperties(
                    t["armor"],
                    t["max_velocity"],
                    t["min_velocity"],
                    t["max_rotation"],
                    t["scale"],
                    t["children"],
                    t["sound_destroy"],
                    t["sound_hit"],
                    t["sprite_name"],
                    t["on_impact"],
                )
                c = c - 1

            position = get_safe_asteroid_distance(
                screen, self.spaceship.geometry.position
            )

            self._asteroids.append(
                Asteroid(props, position, self._asteroids.append, len(a["tiers"]))
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
    def load_level(self, screen: Surface, directory: str):
        return lambda: Level(
            screen, os.path.join(constants.LEVELS_ROOT, directory, ".json")
        )

    def __init__(self, screen: Surface):
        self._levels = {}
        for d in os.listdir(constants.LEVELS_ROOT):
            if not d.startswith(".") and os.path.isdir(
                os.path.join(constants.LEVELS_ROOT, d)
            ):
                (k, v) = d.split("_")
                self._levels[int(k)] = (d, self.load_level(screen, d))

        self._current_level_id = -1

    def start_current_level(self):
        if self._current_level_id == -1:
            self._current_level_id = 0
        self._levels[self._current_level_id][1]()

    def start_next_level(self):
        self.advance_level()
        self._levels[self._current_level_id][1]()

    def start_level(self, level_id: int) -> Level:
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
