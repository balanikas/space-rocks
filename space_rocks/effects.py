import pygame
from pygame import Vector2
from pygame.color import Color
from pygame.surface import Surface

import space_rocks.audio as sounds
import space_rocks.graphics as gfx
from space_rocks.utils import scale_surface, create_surface_alpha
from space_rocks.window import window


class GradientEffect:
    def __init__(self, focus_point: Vector2):
        self._focus_point = focus_point

    def _gradient_rect(
        self,
        surface: Surface,
        left_colour: Color,
        right_colour: Color,
        target_rect: pygame.Rect,
    ):
        """ Draw a horizontal-gradient filled rectangle covering <target_rect> """
        colour_rect = create_surface_alpha((2, 2))
        pygame.draw.line(colour_rect, left_colour, (0, 0), (0, 1))  # left colour line
        pygame.draw.line(colour_rect, right_colour, (1, 0), (1, 1))  # right colour line

        colour_rect = pygame.transform.smoothscale(
            colour_rect, (target_rect.width, target_rect.height)
        )  # stretch!
        surface.blit(colour_rect, target_rect)  # paint it

    def move(self):
        pass

    @property
    def complete(self):
        return False

    def draw(self, surface: Surface):
        self._gradient_rect(
            surface,
            Color(0, 0, 200, 100),
            Color(0, 0, 200, 0),
            pygame.Rect(0, 0, self._focus_point.x, window.height),
        )

        self._gradient_rect(
            surface,
            Color(200, 0, 0, 0),
            Color(200, 0, 0, 100),
            pygame.Rect(self._focus_point.x, 0, window.width, window.height),
        )


class Sun:
    def __init__(self, pos: Vector2):
        self._flip_time_ms = 5000
        self._start_ticks = pygame.time.get_ticks()
        self._darkness = 0
        self._scale = 0.1
        self._growth = True
        self._pos = pos
        sounds.play("gradient_start")

    def move(self):
        if pygame.time.get_ticks() - self._start_ticks > self._flip_time_ms:
            self._growth = not self._growth
            sounds.play("gradient_stop")
            self._start_ticks = pygame.time.get_ticks()

        if self._growth:
            if self._darkness < 200:
                self._darkness += 10
            if self._scale <= 1:
                self._scale += 0.1
        else:

            if self._darkness > 0:
                self._darkness -= 10
            if self._scale > 0:
                self._scale -= 0.02

    @property
    def complete(self):
        return self._scale <= 0 and not self._growth

    def draw(self, surface: Surface):
        w, h = (int(window.width * self._scale), int(window.height * self._scale))
        light = gfx.get("blue_gradient")
        light = scale_surface(light, (w, h))
        filter_surface = pygame.surface.Surface(
            (window.width, window.height), pygame.SRCALPHA
        )

        filter_surface.fill(pygame.Color(0, 0, 0, self._darkness))
        filter_surface.blit(light, (self._pos.x - (w / 2), self._pos.y - (h / 2)))
        surface.blit(filter_surface, (0, 0))
