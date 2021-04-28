import io
import logging
import os
from typing import Dict, Tuple, Any

import pygame
from PIL import Image, ImageDraw, ImageFont
from pygame.image import load
from pygame.surface import Surface

import constants
from utils import get_random_choice

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

        def load_from(path: str):
            for root, _, files in os.walk(path):
                for f in files:
                    f = f.lower()
                    if f.endswith(".png") or f.endswith(".jpg") or f.endswith(".jpeg"):
                        try:
                            g = load(f"{os.path.join(root, f)}")
                        except:
                            g = load(f"{constants.GFX_ASSETS_ROOT}not_found.png")
                        key = os.path.join(root.replace(path, ""), f)
                        cls._bank[key.split(".")[0]] = g

        # load default assets
        load_from(f"{constants.LEVELS_ROOT}{level_name.lower()}/sprites/")

        # load default assets
        load_from(constants.GFX_ASSETS_ROOT)

    @classmethod
    def load(cls, name: str, with_alpha: bool = True, resize: Tuple[int, int] = None):
        name = get_random_choice(name)

        if name not in cls._bank:
            logger.warning(f"sprite {name} not found")
            if name.startswith("text:"):
                cls._bank[name] = cls.load_from_text(name)
            else:
                name = "not_found"

        loaded_sprite = cls._bank[name]
        if resize:
            loaded_sprite = pygame.transform.scale(loaded_sprite, resize)
        return loaded_sprite.convert_alpha() if with_alpha else loaded_sprite.convert()

    @classmethod
    def log_state(cls):
        logger.info(f"{len(cls._bank)} images loaded")
        logger.info(cls._bank.keys())


def init_sprites(level_name: str):
    SpriteLibrary(level_name)
    SpriteLibrary.log_state()
