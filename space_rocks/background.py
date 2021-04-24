from pygame import Vector2, Surface

from graphics import SpriteLibrary
from utils import get_resize_factor
from audio import SoundLibrary
from window import window


class Background:
    def _initialize(self):
        self._background = SpriteLibrary.load(
            self._sprite_name, False, resize=get_resize_factor(1.2)
        )

        (s_x, s_y) = self._background.get_size()
        x = ((s_x - window.width) / 2) * -1
        y = ((s_y - window.height) / 2) * -1
        self._offset = (x, y)

    def __init__(self, sprite_name: str):
        self._sprite_name = sprite_name
        self._initialize()

        SoundLibrary.play("background", True)

    def draw(self, surface: Surface, pos: Vector2):
        position = (
            pos - Vector2(window.center)
        ) * -0.2  # ensures background moves slower than ship
        position += self._offset
        surface.blit(self._background, position)

    def resize(self):
        self._initialize()
