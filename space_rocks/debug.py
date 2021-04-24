from typing import Sequence

import pygame
from pygame.math import Vector2

from models import GameObject
from window import window


class Debug:
    def __init__(self, clock: pygame.time.Clock):
        self._clock = clock
        self._font = pygame.font.Font(None, 30)
        self.enabled = False

    def draw_text(self, surface: pygame.Surface, pos: Vector2, vel: Vector2, dir: Vector2):
        if not self.enabled:
            return

        fps = self._clock.get_fps()

        text_surface = self._font.render(
            f"{round(fps, 0)} fps | "
            f"x:{round(pos.x, 1)} y:{round(pos.y, 1)} | "
            f"vel: {vel} | "
            f"dir: {dir} | "
            f"win:{window.size} | "
            f"display: {(pygame.display.Info().current_w, pygame.display.Info().current_h)}",
            False,
            (255, 255, 0),
        )
        surface.blit(text_surface, (0, 0))

    def draw_visual(self, screen: pygame.Surface, objs: Sequence[GameObject]):
        if not self.enabled:
            return

        for o in objs:
            pygame.draw.polygon(
                o.image,
                (0, 255, 0),
                pygame.mask.from_surface(o.image).outline(),
                1,
            )
            rect = o.rect
            pygame.draw.rect(
                screen,
                (0, 0, 255),
                (
                    o.geometry.position.x - (rect.width / 2),
                    o.geometry.position.y - (rect.height / 2),
                    rect.width,
                    rect.height,
                ),
                1,
            )