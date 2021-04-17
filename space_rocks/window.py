from typing import Tuple

import pygame
from pygame import Vector2

from space_rocks import constants


class Window:
    def __init__(self):
        self._size = (constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)
        self._resize_factor: Vector2 = Vector2(1, 1)

    @property
    def size(self) -> Tuple[int, int]:
        return self._size

    @property
    def width(self) -> int:
        return self._size[0]

    @property
    def height(self) -> int:
        return self._size[1]

    @property
    def factor(self) -> Vector2:
        return self._resize_factor

    @property
    def center(self) -> Tuple[int, int]:
        return self._size[0] / 2, self._size[1] / 2

    def resize(self):
        info = pygame.display.Info()
        self._resize_factor = Vector2(
            info.current_w / self._size[0], info.current_h / self._size[1]
        )
        self._size = (info.current_w, info.current_h)


window = Window()
