import logging
import os
from typing import Dict

from space_rocks import constants

logger = logging.getLogger(__name__)


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
                    s = Sound(f"{constants.SOUND_ASSETS_ROOT}not_found.wav")

                cls._bank[f.split(".")[0]] = s

        for f in os.listdir(f"{constants.SOUND_ASSETS_ROOT}"):
            f = f.lower()
            if f.endswith(".wav"):
                try:
                    s = Sound(f"{constants.SOUND_ASSETS_ROOT}{f}")
                except:
                    s = Sound(f"{constants.SOUND_ASSETS_ROOT}not_found.wav")

                cls._bank[f.split(".")[0]] = s

    @classmethod
    def play(cls, name: str, repeat: bool = False):
        name = name.lower()
        if name not in cls._bank:
            print(f"sound {name} not found")
            name = "not_found"

        if constants.ENABLE_AUDIO:
            cls._bank[name].play(1000 if repeat else 0)

    @classmethod
    def stop(cls, name: str):
        name = name.lower()
        if name not in cls._bank:
            name = "not_found"

        cls._bank[name].stop()

    @classmethod
    def stop_all(cls):
        for k, v in cls._bank.items():
            v.stop()

    @classmethod
    def print_state(cls):
        logger.info("sounds loaded")
        logger.info(cls._bank.keys())


def init_sounds(level_name: str):
    SoundLibrary(level_name)
    SoundLibrary.print_state()
