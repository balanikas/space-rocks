import os
from typing import Dict

from pygame.image import load
from pygame.surface import Surface


class SpriteLibrary:
    _bank: Dict[str, Surface] = {}

    @classmethod
    def __init__(cls) -> None:

        for f in os.listdir(f"../assets/sprites/"):
            if f.endswith(".png") or f.endswith(".jpg") or f.endswith(".jpeg"):
                try:
                    g = load(f"../assets/sprites/{f}")
                except:
                    g = load(f"../assets/sprites/not_found.png")
                cls._bank[f.split(".")[0]] = g

    @classmethod
    def load(cls, name: str, with_alpha: bool = True):
        if name not in cls._bank:
            name = "not_found"

        loaded_sprite = cls._bank[name]
        return loaded_sprite.convert_alpha() if with_alpha else loaded_sprite.convert()


def init_sprites():
    SpriteLibrary()
    print("sprites loaded")
