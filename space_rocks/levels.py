from typing import List, Sequence, Tuple, Optional

from pygame import Vector2
from pygame.surface import Surface

import constants
from space_rocks.models import Background, Asteroid, Spaceship, Bullet, AsteroidProperties, SpaceshipProperties, \
    GameObject
from space_rocks.utils import get_safe_asteroid_distance


class Level:


    def __init__(self, name: str):
        self._background: Background = Background("background")
        self._bullets: List[Bullet] = []
        self._spaceship: Optional[Spaceship] = None
        self._asteroids: List[Asteroid] = []
        self._name = name

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

    @property
    def name(self) -> str:
        return self._name

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


class Level1(Level):
    def __init__(self, screen: Surface, name: str):
        super().__init__(name)
        self._bullets: List[Bullet] = []
        props = SpaceshipProperties(5, 0.15, 5, "laser")
        self._spaceship = Spaceship(props, "spaceship",
                                    constants.SCREEN_CENTER,
                                    self._bullets.append)
        self._asteroids: List[Asteroid] = []
        for a in ["planet-1", "planet-2", "planet-3"]:
            position = get_safe_asteroid_distance(screen, self.spaceship.geometry.position)
            properties = {
                3: AsteroidProperties(1, 2, 3, 1, 2, "explosion5", a),
                2: AsteroidProperties(2, 4, 20, 0.5, 8, "explosion4", a),
                1: AsteroidProperties(1, 3, 3, 0.3, 4, "hit_big", a),
            }
            self._asteroids.append(Asteroid(properties, position, self._asteroids.append, 3))

'''
{
    name: "level1",
    ship: {
        manuverability: 1,
        ...
        
    },
    asteroids: [
        {
            3: {
                max_vel: 2,
                min_vel: 3,
                ...
                "sound_hit": "expl1",
                ...
            }
            2 : {
                max_vel: 2,
                min_vel: 3,
                ...
                "sound_hit": "expl1",
                ...
            },
            ...
        },
        
        
    ]
}

'''


class Level2(Level):
    def __init__(self, screen: Surface, name: str):
        super().__init__(name)
        self._bullets: List[Bullet] = []
        props = SpaceshipProperties(5, 0.15, 5, "laser")
        self._spaceship = Spaceship(props, "spaceship",
                                    Vector2(constants.SCREEN_WIDTH / 2, constants.SCREEN_HEIGHT / 2),
                                    self._bullets.append)
        self._asteroids: List[Asteroid] = []
        for _ in range(6):
            position = get_safe_asteroid_distance(screen, self.spaceship.geometry.position)

            properties = {
                4: AsteroidProperties(1, 2, 3, 1, 4, "hit_big", "asteroid"),
                3: AsteroidProperties(1, 3, 3, 0.5, 4, "hit_big", "asteroid"),
                2: AsteroidProperties(1, 3, 3, 0.2, 8, "hit_big", "asteroid"),
                1: AsteroidProperties(1, 3, 3, 0.1, 4, "hit_big", "asteroid"),
            }
            self._asteroids.append(Asteroid(properties, position, self._asteroids.append, 4))


class Level3(Level):
    def __init__(self, screen: Surface, name: str):
        super().__init__(name)
        self._bullets: List[Bullet] = []
        props = SpaceshipProperties(5, 0.15, 5, "laser")
        self._spaceship = Spaceship(props, "spaceship",
                                    constants.SCREEN_CENTER,
                                    self._bullets.append)
        self._asteroids: List[Asteroid] = []
        for _ in range(16):
            position = get_safe_asteroid_distance(screen, self.spaceship.geometry.position)

            properties = {
                2: AsteroidProperties(2, 3, 7, 0.4, 2, "hit_big", "asteroid"),
                1: AsteroidProperties(1, 3, 3, 0.1, 4, "hit_big", "asteroid"),
            }
            self._asteroids.append(Asteroid(properties, position, self._asteroids.append, 2))



class World:
    def __init__(self, screen: Surface):

        # todo get level names by folder structure, use only class 'Level', pass the json (from definition.json), instantiate 'Level' props from json data.
        self._levels = {
            0: ("level1", lambda: Level1(screen, "level1")),
            1: ("level2", lambda: Level2(screen, "level2")),
            2: ("level3", lambda: Level3(screen, "level3")),
        }
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
