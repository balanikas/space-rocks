from pygame import Vector2, Surface

import audio as sounds
import graphics as gfx
from space_rocks.utils import scale_surface
from window import window


class Background:
    def _initialize(self):

        self._image = gfx.get(self._image_name, False)
        target_size = Vector2(window.width * 1.2, window.height * 1.2)
        source_size = Vector2(self._image.get_size())
        delta_x, delta_y = source_size - target_size
        if delta_x < 0 or delta_y < 0:
            self._image = scale_surface(
                self._image, (int(target_size.x), int(target_size.y))
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
