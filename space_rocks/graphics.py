import io
import logging
import os
from typing import Dict, Tuple, Any

import pygame
from PIL import Image, ImageDraw, ImageFont
from pygame.image import load
from pygame.surface import Surface

from space_rocks import constants

logger = logging.getLogger(__name__)


class SpriteLibrary:
    _bank: Dict[str, Surface] = {}

    @classmethod
    def load_from_text(cls, text: str) -> Any:

        text = text.strip("text:")
        img: Image = Image.new("RGBA", (200, 200))

        d = ImageDraw.Draw(img)
        font = ImageFont.truetype("../assets/font.ttf", 20)
        d.text((0, 100), text, fill=(255, 0, 255), font=font)
        s = io.BytesIO()
        img.save(s, "png")
        bytes = img.tobytes()

        return pygame.image.fromstring(bytes, img.size, img.mode)

    @classmethod
    def __init__(cls, level_name: str) -> None:
        cls._bank = {}
        level_name = level_name.lower()

        for f in os.listdir(f"../levels/{level_name}/sprites/"):
            f = f.lower()
            if f.endswith(".png") or f.endswith(".jpg") or f.endswith(".jpeg"):
                try:
                    g = load(f"../levels/{level_name}/sprites/{f}")
                except:
                    g = load(f"{constants.GFX_ASSETS_ROOT}not_found.png")
                cls._bank[f.split(".")[0]] = g

        for f in os.listdir(f"{constants.GFX_ASSETS_ROOT}"):
            f = f.lower()
            if f.endswith(".png") or f.endswith(".jpg") or f.endswith(".jpeg"):
                try:
                    g = load(f"{constants.GFX_ASSETS_ROOT}{f}")
                except:
                    g = load(f"{constants.GFX_ASSETS_ROOT}not_found.png")
                cls._bank[f.split(".")[0]] = g

    @classmethod
    def load(cls, name: str, with_alpha: bool = True, resize: Tuple[int, int] = None):
        name = name.lower()
        if name not in cls._bank:
            print(f"sprite {name} not found")
            if name.startswith("text:"):
                cls._bank[name] = cls.load_from_text(name)
            else:
                name = "not_found"

        loaded_sprite = cls._bank[name]
        if resize:
            loaded_sprite = pygame.transform.scale(loaded_sprite, resize)
        return loaded_sprite.convert_alpha() if with_alpha else loaded_sprite.convert()

    @classmethod
    def print_state(cls):
        logger.info("gfx loaded")
        logger.info(cls._bank.keys())


def init_sprites(level_name: str):
    SpriteLibrary(level_name)
    SpriteLibrary.print_state()
