import os
from typing import Dict

import pygame.mixer


class SoundLibrary:
    from pygame.mixer import Sound
    _bank: Dict[str, Sound] = {}

    @classmethod
    def __init__(cls, level_name: str) -> None:

        from pygame.mixer import Sound
        cls._bank = {}
        level_name = level_name.lower()
        for f in os.listdir(f"../levels/{level_name}/sounds/"):
            f = f.lower()
            if f.endswith(".wav"):
                try:
                    s = Sound(f"../levels/{level_name}/sounds/{f}")
                except:
                    s = Sound(f"../assets/sounds/not_found.wav")

                cls._bank[f.split(".")[0]] = s

        for f in os.listdir(f"../assets/sounds/"):
            f = f.lower()
            if f.endswith(".wav"):
                try:
                    s = Sound(f"../assets/sounds/{f}")
                except:
                    s = Sound(f"../assets/sounds/not_found.wav")

                cls._bank[f.split(".")[0]] = s

    @classmethod
    def play(cls, name: str, repeat: bool = False):
        if name not in cls._bank:
            print(f"sound {name} not found")
            name = "not_found"

        cls._bank[name].play(1000 if repeat else 0)
        pygame.mixer.pause()

    @classmethod
    def stop(cls, name: str):
        if name not in cls._bank:
            name = "not_found"

        cls._bank[name].stop()

    @classmethod
    def stop_all(cls):
        for k, v in cls._bank.items():
            v.stop()


def init_sounds(level_name: str):
    SoundLibrary(level_name)
    print(f"sounds loaded for level {level_name}")
