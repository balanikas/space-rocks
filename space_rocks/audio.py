import logging
import os
from typing import Dict

import constants

logger = logging.getLogger(__name__)


class SoundLibrary:
    from pygame.mixer import Sound

    _bank: Dict[str, Sound] = {}

    @classmethod
    def __init__(cls, level_name: str) -> None:
        from pygame.mixer import Sound

        cls._bank = {}

        def load_from(path: str):
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
        load_from(f"{constants.LEVELS_ROOT}{level_name.lower()}/sounds/")

        # load default assets
        load_from(constants.SOUND_ASSETS_ROOT)

    @classmethod
    def play(cls, name: str, repeat: bool = False):
        name = name.lower()
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
        logger.info("sounds loaded")
        logger.info(cls._bank.keys())


def init_sounds(level_name: str):
    SoundLibrary(level_name)
    SoundLibrary.log_state()
