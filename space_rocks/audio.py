import logging
import os
from typing import Dict

import constants
from utils import get_random_choice
from pygame.mixer import Sound

logger = logging.getLogger(__name__)


class SoundLibrary:

    _bank: Dict[str, Sound] = {}

    @classmethod
    def __init__(cls, level_name: str) -> None:

        cls._bank = {}

        def _load_from(path: str):
            for root, _, files in os.walk(path):
                for f in files:
                    f = f.lower()
                    if f.endswith(".wav") or f.endswith(".ogg"):
                        try:
                            s = Sound(f"{os.path.join(root, f)}")
                        except:
                            s = Sound(f"{constants.SOUND_ASSETS_ROOT}not_found.wav")
                        key = os.path.join(root.replace(path, ""), f)
                        cls._bank[key.split(".")[0]] = s

        # load level assets
        _load_from(f"{constants.LEVELS_ROOT}{level_name.lower()}/sounds/")

        # load default assets
        _load_from(constants.SOUND_ASSETS_ROOT)

    @classmethod
    def play(cls, name: str, repeat: bool = False):
        name = get_random_choice(name)
        if name not in cls._bank:
            logger.warning(f"sound {name} not found")
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
    def log_state(cls):
        logger.info(f"{len(cls._bank)} sounds loaded")
        logger.info(cls._bank.keys())


def init_sounds(level_name: str):
    SoundLibrary(level_name)
    SoundLibrary.log_state()
