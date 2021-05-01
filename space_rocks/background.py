from pygame import Vector2, Surface

import audio as sounds
from graphics import SpriteLibrary
from utils import get_resize_factor
from window import window


class Background:
    def _initialize(self):
        self._image = SpriteLibrary.load(
            self._image_name, False, resize=get_resize_factor(1.2)
        )

        (s_x, s_y) = self._image.get_size()
        x = ((s_x - window.width) / 2) * -1
        y = ((s_y - window.height) / 2) * -1
        self._offset = (x, y)

    def __init__(self, image_name: str, soundtrack: str):
        self._image_name = image_name
        self._initialize()
        sounds.play(soundtrack, True)

    def draw(self, surface: Surface, pos: Vector2):
        position = (
            pos - Vector2(window.center)
        ) * -0.2  # ensures background moves slower than player
        position += self._offset
        surface.blit(self._image, position)

    def resize(self):
        self._initialize()
