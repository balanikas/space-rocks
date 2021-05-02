import os
from typing import Sequence

import psutil
import pygame
from pygame import Surface
from pygame.color import Color
from pygame.math import Vector2

from decorators import func_timings
from models import GameObject
from window import window
import graphics as gfx
import audio as sounds
import animation as anim


class Debug:
    def __init__(self, clock: pygame.time.Clock):
        self._clock = clock
        self._font = pygame.font.Font(None, 24)
        self.enabled = False
        self._process = psutil.Process(os.getpid())
        self._surface = pygame.Surface((window.width, window.height), pygame.SRCALPHA)
        self._surface.fill(Color(0, 0, 0, 128))

    def _draw_lines(self, surface: Surface, lines: []):
        y = 0
        for l in lines:
            text_surface = self._font.render(
                l,
                False,
                (255, 255, 0),
            )
            surface.blit(text_surface, (0, y))
            y += 25

    def draw_text(
        self, surface: Surface, position: Vector2, velocity: Vector2, direction: Vector2
    ):
        if not self.enabled:
            return

        surface.blit(self._surface, (0, 0))

        lines = []
        lines.append(
            f"fps: {round(self._clock.get_fps(), 0)} | "
            f"win:{window.size} | "
            f"display: {(pygame.display.Info().current_w, pygame.display.Info().current_h)} | "
            f"vel: {(round(velocity.x), round(velocity.y))} | "
            f"dir: {(round(direction.x), round(direction.y))} | "
            f"pos: {(round(position.x), round(position.y))} | "
        )

        lines.append("-" * 5 + " function performance " + "-" * 5)
        for k, v in func_timings.items():
            lines.append(f"{k}:{v:.2f} ms")

        lines.append("-" * 5 + " process " + "-" * 5)
        mem_mb = round(self._process.memory_info().rss / 1024 ** 2)
        lines.append(f"{mem_mb} Mb")
        cpu = round(self._process.cpu_percent())
        lines.append(f"{cpu} % CPU")

        lines.append("-" * 5 + " assets " + "-" * 5)
        lines.append(f"images: {gfx.count()}")
        lines.append(f"sounds: {sounds.count()}")
        lines.append(f"animations: {anim.count()}")
        self._draw_lines(surface, lines)

    def draw_visual(self, screen: pygame.Surface, objs: Sequence[GameObject]):
        if not self.enabled:
            return

        for o in objs:
            points = pygame.mask.from_surface(o.image).outline()
            if len(points) < 2:
                continue

            pygame.draw.polygon(
                o.image,
                (0, 255, 0),
                points,
                1,
            )
            rect = o.rect
            pygame.draw.rect(
                screen,
                (0, 255, 0),
                (
                    o.geometry.position.x - (rect.width / 2),
                    o.geometry.position.y - (rect.height / 2),
                    rect.width,
                    rect.height,
                ),
                1,
            )
