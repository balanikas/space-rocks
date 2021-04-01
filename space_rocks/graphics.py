import os
from typing import Dict

from pygame.image import load
from pygame.surface import Surface


class SpriteLibrary:

    @classmethod
    def __init__(cls) -> None:

        cls._bank: Dict[str, Surface] = {}
        for f in os.listdir(f"../assets/sprites/"):
            if f.endswith(".png"):
                cls._bank[f.split(".")[0]] = load(f"../assets/sprites/{f}")

    @classmethod
    def load(cls, name: str, with_alpha: bool = True):
        loaded_sprite = cls._bank[name]
        return loaded_sprite.convert_alpha() if with_alpha else loaded_sprite.convert()


def init_sprites():
    SpriteLibrary()
