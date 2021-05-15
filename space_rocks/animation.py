import json
import logging
import os
from typing import Dict, Tuple, NamedTuple, List, Optional

from pygame.math import Vector2
from pygame.rect import Rect
from pygame.surface import Surface

from space_rocks import constants
from space_rocks.utils import (
    get_random_choice,
    scale_surface,
    create_surface_from_image,
    get_blit_position,
)

logger = logging.getLogger(__name__)


class Animation:
    def __init__(
        self,
        frames: list[Surface],
        position: Vector2,
        speed: float,
        repeat: bool = False,
    ):
        self._frames = frames
        self._time = 0.0
        self._frame_index = 0
        self._position = position
        self._speed = speed
        self._repeat = repeat

    @property
    def complete(self):
        if self._repeat:
            return False
        return self._frame_index >= len(self._frames) - 1

    def move(self):
        self._time += self._speed
        if self._time > 1:
            self._frame_index += 1
            self._time = 0

    def draw(self, surface: Surface):
        if self.complete:
            return
        if self._frame_index >= len(self._frames) - 1:
            self._frame_index = 0

        img = self._frames[self._frame_index]
        blit_position = get_blit_position(img, self._position)
        surface.blit(img, blit_position)


class AnimationData(NamedTuple):
    frames: list[Surface]
    speed: float


_bank: Dict[str, AnimationData] = {}


def _init(level_name: str) -> None:
    def create_frames(img: Surface, rows: int, columns: int) -> list[Surface]:
        h = int(img.get_height() / rows)
        w = int(img.get_width() / columns)
        size = w, h
        images: List[Surface] = []
        orig_alpha = img.get_alpha()
        orig_ckey = img.get_colorkey()
        img.set_colorkey(None)
        img.set_alpha(None)

        for y in range(0, img.get_height(), h):
            for x in range(0, img.get_width(), w):
                i = Surface(size)
                i.blit(img, (0, 0), Rect(x, y, w, h))
                if orig_alpha:
                    i.set_colorkey((0, 0, 0))
                elif orig_ckey:
                    i.set_colorkey(orig_ckey)

                images.append(i.convert_alpha())

        img.set_alpha(orig_alpha)
        img.set_colorkey(orig_ckey)
        return images

    def _load_from(path: str):

        if not os.path.isfile(os.path.join(path, ".json")):
            return

        with open(os.path.join(path, ".json")) as json_file:
            if not json_file:
                return
            data = json.load(json_file)

        for d in data["animations"]:
            img_name = d["image"].lower()
            img_path = f"{os.path.join(path, img_name + '.png')}"

            img = create_surface_from_image(img_path)
            frames = create_frames(img, d["rows"], d["columns"])

            _bank[img_name] = AnimationData(frames, d["speed"])

    # load default assets
    _load_from(f"{constants.LEVELS_ROOT}{level_name.lower()}/anim/")

    # load default assets
    _load_from(constants.ANIM_ASSETS_ROOT)


def get(
    name: str, position: Vector2, resize: Optional[Tuple[int, int]] = None
) -> Animation:
    name = get_random_choice(name)

    if name not in _bank:
        anim_data = AnimationData([], 1)
    else:
        anim_data = _bank[name]
        if resize:
            anim_data = AnimationData(
                [scale_surface(img, resize) for img in anim_data.frames],
                anim_data.speed,
            )

    return Animation(anim_data.frames, position, anim_data.speed)


def _log_state():
    logger.info(f"{len(_bank)} animations loaded:")
    logger.info(_bank.keys())


def count():
    return len(_bank)


def init(level_name: str):
    _init(level_name)
    _log_state()
