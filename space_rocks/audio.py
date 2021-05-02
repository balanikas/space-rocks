import logging
import os
from typing import Dict

from pygame.mixer import Sound

import constants
from utils import get_random_choice

logger = logging.getLogger(__name__)


_bank: Dict[str, Sound] = {}


def _init(level_name):
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
                    _bank[key.split(".")[0]] = s

    global _bank
    _bank = {}

    # load level assets
    _load_from(f"{constants.LEVELS_ROOT}{level_name.lower()}/sounds/")

    # load default assets
    _load_from(constants.SOUND_ASSETS_ROOT)


def play(name: str, repeat: bool = False):
    name = get_random_choice(name)
    if name not in _bank:
        logger.warning(f"sound {name} not found")
        name = "not_found"
    if constants.ENABLE_AUDIO:
        _bank[name].play(1000 if repeat else 0)


def stop(name: str):
    name = name.lower()
    if name not in _bank:
        name = "not_found"
    _bank[name].stop()


def stop_all():
    for k, v in _bank.items():
        v.stop()


def count():
    return len(_bank)


def _log_state():
    logger.info(f"{len(_bank)} sounds loaded")
    logger.info(_bank.keys())


def init(level_name: str):
    _init(level_name)
    _log_state()
