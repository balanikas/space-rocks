import os
from typing import Dict


class SoundLibrary:

    @classmethod
    def __init__(cls) -> None:
        from pygame.mixer import Sound

        cls._bank: Dict[str, Sound] = {}
        for f in os.listdir(f"../assets/sounds/"):
            if f.endswith(".wav"):
                cls._bank[f.split(".")[0]] = Sound(f"../assets/sounds/{f}")

    @classmethod
    def play(cls, name: str):
        cls._bank[name].play()

    @classmethod
    def stop(cls, name: str):
        cls._bank[name].stop()

    @classmethod
    def stop_all(cls):
        for k, v in cls._bank.items():
            v.stop()


def init_sounds():
    SoundLibrary()
    print("sounds loaded")
