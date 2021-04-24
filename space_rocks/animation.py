import json
import logging
import os
from typing import Dict, Tuple

import pygame
from pygame.image import load
from pygame.math import Vector2
from pygame.surface import Surface

import constants

logger = logging.getLogger(__name__)


class Animation:
    def __init__(
        self,
        frames: list[Surface],
        position: Vector2,
        speed: float,
    ):
        self._frames = frames
        self._time = 0.0
        self._frame_index = 0
        self._position = position
        self._speed = speed

    @property
    def complete(self):
        return self._frame_index >= len(self._frames) - 1

    def move(self):
        self._time += self._speed
        if self._time > 1:
            self._frame_index += 1
            self._time = 0

    def draw(self, surface: Surface):
        if self.complete:
            return
        img = self._frames[self._frame_index]
        blit_position = self._position - (Vector2(img.get_size()) * 0.5)
        surface.blit(img, blit_position)


_bank: Dict[str, list[Surface]] = {}


class AnimationLibrary:
    @classmethod
    def __init__(cls, level_name: str) -> None:

        cls._bank = {}

        def create_frames(img: Surface, rows, columns) -> list[Surface]:
            h = int(img.get_height() / rows)
            w = int(img.get_width() / columns)
            size = w, h
            images = []
            orig_alpha = img.get_alpha()
            orig_ckey = img.get_colorkey()
            img.set_colorkey(None)
            img.set_alpha(None)

            for y in range(0, img.get_height(), h):
                for x in range(0, img.get_width(), w):
                    i = pygame.Surface(size)
                    i.blit(img, (0, 0), ((x, y), size))
                    if orig_alpha:
                        i.set_colorkey((0, 0, 0))
                    elif orig_ckey:
                        i.set_colorkey(orig_ckey)

                    images.append(i.convert_alpha())

            img.set_alpha(orig_alpha)
            img.set_colorkey(orig_ckey)
            return images

        def load_from(path: str):

            if not os.path.isfile(os.path.join(path, ".json")):
                return

            with open(os.path.join(path, ".json")) as json_file:
                if not json_file:
                    return
                data = json.load(json_file)

            for d in data["animations"]:
                img_name = d["image"].lower()
                img_path = f"{os.path.join(path, img_name + '.png')}"

                img = load(img_path)
                g = create_frames(img, d["rows"], d["columns"])

                _bank[img_name] = g

        # load default assets
        load_from(f"{constants.LEVELS_ROOT}{level_name.lower()}/anim/")

        # load default assets
        load_from(constants.ANIM_ASSETS_ROOT)

    @classmethod
    def load(
        cls, name: str, position: Vector2, speed: float, resize: Tuple[int, int] = None
    ) -> Animation:
        name = name.lower()
        anims = _bank[name]
        if resize:
            anims = [pygame.transform.scale(img, resize) for img in anims]

        return Animation(anims, position, speed)

    @classmethod
    def log_state(cls):
        logger.info("animations loaded")
        logger.info(_bank.keys())


def init_animations(level_name: str):
    AnimationLibrary(level_name)
    AnimationLibrary.log_state()
