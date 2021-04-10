import os
from typing import Dict


class SoundLibrary:
    from pygame.mixer import Sound
    _bank: Dict[str, Sound] = {}

    @classmethod
    def __init__(cls, level_name: str) -> None:

        from pygame.mixer import Sound
        cls._bank = {}
        level_name = level_name.lower()
        for f in os.listdir(f"../{level_name}/sounds/"):
            f = f.lower()
            if f.endswith(".wav"):
                try:
                    s = Sound(f"../{level_name}/sounds/{f}")
                except:
                    s = Sound(f"../assets/sounds/not_found.wav")

                cls._bank[f.split(".")[0]] = s

    @classmethod
    def play(cls, name: str):
        if name not in cls._bank:
            name = "not_found"

        cls._bank[name].play()

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
