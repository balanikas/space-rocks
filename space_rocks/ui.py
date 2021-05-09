from pygame.color import Color
from pygame.font import Font
from pygame.surface import Surface

import space_rocks.audio as sounds
from space_rocks.models import GameState
from space_rocks.utils import create_default_font


class UI:
    def __init__(self):
        self._font = create_default_font(64)
        self._message = ""
        self._sound_played = False

    def _print_text(
            self, surface: Surface, text: str, font: Font, color: Color = Color(0, 255, 0)
    ):
        text_surface = font.render(text, True, color)
        if not text_surface:
            raise SystemExit
        rect = text_surface.get_rect()
        rect.center = int(surface.get_size()[0] / 2), int(surface.get_size()[1] / 2)
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
