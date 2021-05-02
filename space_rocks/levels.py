import json
import logging
import os
from typing import List, Sequence, Tuple, Callable, Dict

import jsonschema
from jsonschema import validate
from pygame import Vector2
from pygame.surface import Surface

import constants
from background import Background
from models import (
    Enemy,
    Bullet,
    EnemyProperties,
    GameObject,
    BulletProperties,
)
from player import PlayerProperties, Player
from utils import get_safe_enemy_distance
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
        player = data["player"]
        prim = player["primary_weapon"]
        primary_weapon = BulletProperties(
            prim["damage"],
            prim["speed"],
            prim["sound"],
            prim["reload"],
            prim["image"],
        )
        primary_weapon.validate()

        sec = player["secondary_weapon"]
        secondary_weapon = BulletProperties(
            sec["damage"],
            sec["speed"],
            sec["sound"],
            sec["reload"],
            sec["image"],
        )
        secondary_weapon.validate()

        player_props = PlayerProperties(
            player["damage"],
            player["armor"],
            player["maneuverability"],
            player["acceleration"],
            player["sound_on_impact"],
            player["image"],
            player["anim_on_destroy"],
            primary_weapon,
            secondary_weapon,
        )

        player_props.validate()

        self._player = Player(
            player_props, Vector2(window.center), self._bullets.append
        )
        self._enemies: List[Enemy] = []

        for a in data["enemies"]:
            player_props = {}
            c = len(a["tiers"])
            for t in a["tiers"]:
                p = EnemyProperties(
                    t["damage"],
                    t["armor"],
                    t["max_velocity"],
                    t["min_velocity"],
                    t["max_rotation"],
                    t["scale"],
                    t["children"],
                    t["sound_on_destroy"],
                    t["sound_on_impact"],
                    t["image"],
                    t["anim_on_destroy"],
                )
                p.validate()
                player_props[c] = p
                c = c - 1

            position = get_safe_enemy_distance(screen, self.player.geometry.position)

            self._enemies.append(
                Enemy(player_props, position, self._enemies.append, len(a["tiers"]))
            )

        self._background: Background = Background(
            data["background"], data["soundtrack"]
        )

    @property
    def background(self) -> Background:
        return self._background

    @property
    def bullets(self) -> Sequence[Bullet]:
        return self._bullets

    @property
    def player(self) -> Player:
        return self._player

    @property
    def enemies(self) -> Sequence[Enemy]:
        return self._enemies

    @property
    def game_objects(self) -> Sequence[GameObject]:
        game_objects = [*self._enemies, *self._bullets]
        if self._player:
            game_objects.append(self._player)
        return game_objects

    def remove_player(self):
        self._player = None

    def remove_bullet(self, bullet: Bullet):
        self._bullets.remove(bullet)

    def remove_enemy(self, a: Enemy):
        self._enemies.remove(a)


class World:
    def _load_level(self, screen: Surface, directory: str) -> Callable:
        return lambda: Level(
            screen, os.path.join(constants.LEVELS_ROOT, directory, ".json")
        )

    def __init__(self, screen: Surface):
        self._levels: Dict[int, Tuple[str, Callable]] = {}
        for d in os.listdir(constants.LEVELS_ROOT):
            if not d.startswith(".") and os.path.isdir(
                os.path.join(constants.LEVELS_ROOT, d)
            ):
                (k, v) = d.split("_")
                self._levels[int(k)] = (d, self._load_level(screen, d))

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

    def set_previous_level(self):
        if self._current_level_id > 0:
            self._current_level_id -= 1
        else:
            self._current_level_id = len(self._levels) - 1

    def get_all_levels(self) -> List[Tuple[str, int]]:
        levels = []
        for k, v in self._levels.items():
            levels.append((v[0], k))

        return levels
