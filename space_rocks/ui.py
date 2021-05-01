import pygame
from pygame.color import Color
from pygame.font import Font
from pygame.math import Vector2
from pygame.surface import Surface

import audio as sounds
from models import GameState


class UI:
    def __init__(self):
        self._font = pygame.font.Font(None, 64)
        self._message = ""
        self._sound_played = False

    def _print_text(
        self, surface: Surface, text: str, font: Font, color: Color = Color(0, 255, 0)
    ):
        text_surface: Surface = font.render(text, True, color)
        rect = text_surface.get_rect()
        rect.center = Vector2(surface.get_size()) / 2
        surface.blit(text_surface, rect)

    def draw(self, surface: Surface, state: GameState):

        if state == GameState.WON:
            self._message = "You won! Press RETURN to continue"
            if not self._sound_played:
                sounds.play("win_level")
                self._sound_played = not self._sound_played
        elif state == GameState.LOST:
            self._message = "You lost! Press RETURN to restart"
            if not self._sound_played:
                sounds.play("game_over")
                self._sound_played = not self._sound_played
        elif state == GameState.RUNNING:
            self._sound_played = False
            self._message = ""
        elif state == GameState.NOT_RUNNING:
            self._message = "Press RETURN to start"

        self._print_text(surface, self._message, self._font)
