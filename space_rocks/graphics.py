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


_bank: Dict[str, Surface] = {}


def load_from_text(text: str) -> Any:
    text = text.strip("text:")
    img: Image = Image.new("RGBA", (200, 200))
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype("../assets/OpenSansEmoji.ttf", 20)
    d.text((0, 100), text, fill=(255, 0, 255), font=font)
    s = io.BytesIO()
    img.save(s, "png")
    img_bytes = img.tobytes()

    return pygame.image.fromstring(img_bytes, img.size, img.mode)


def _init(level_name: str) -> None:
    def _load_from(path: str):
        for root, _, files in os.walk(path):
            for f in files:
                f = f.lower()
                if f.endswith(".png") or f.endswith(".jpg") or f.endswith(".jpeg"):
                    try:
                        g = load(f"{os.path.join(root, f)}")
                    except:
                        g = load(f"{constants.GFX_ASSETS_ROOT}not_found.png")
                    key = os.path.join(root.replace(path, ""), f)
                    _bank[key.split(".")[0]] = g

    global _bank
    _bank = {}
    # load default assets
    _load_from(f"{constants.LEVELS_ROOT}{level_name.lower()}/sprites/")
    # load default assets
    _load_from(constants.GFX_ASSETS_ROOT)


def get(name: str, with_alpha: bool = True, resize: Tuple[int, int] = None) -> Surface:
    name = get_random_choice(name)
    if name not in _bank:
        logger.warning(f"sprite {name} not found")
        if name.startswith("text:"):
            _bank[name] = load_from_text(name)
        else:
            name = "not_found"
    loaded_sprite = _bank[name]
    if resize:
        loaded_sprite = pygame.transform.scale(loaded_sprite, resize)
    return loaded_sprite.convert_alpha() if with_alpha else loaded_sprite.convert()


def count():
    return len(_bank)


def _log_state():
    logger.info(f"{len(_bank)} images loaded")
    logger.info(_bank.keys())


def init(level_name: str):
    _init(level_name)
    _log_state()
