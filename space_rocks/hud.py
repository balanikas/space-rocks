from typing import Optional

import pygame.freetype
from pygame import Rect, Color
from pygame.surface import Surface

from space_rocks.decorators import timer
from space_rocks.player import ActiveWeapon
from space_rocks.utils import create_surface_alpha
from space_rocks.window import window


class UIText:
    def __init__(self, rect: Rect, color: Color, font: pygame.freetype.Font):
        self._rect = rect
        self._color = color
        self._font = font

    def draw(self, surface: Surface, text: str, color: Optional[Color] = None):
        color = color if color else self._color
        text_surface, _ = self._font.render(text, color, None)
        surface.blit(text_surface, self._rect)


class UIRect:
    def __init__(self, rect: Rect, color: Color):
        self._surface = create_surface_alpha((rect.width, rect.height))
        self._surface.fill(color)
        self._rect = rect

    def draw(self, surface: Surface):
        surface.blit(self._surface, (self._rect.x, self._rect.y))


class HUD:
    def __init__(self):
        self._white = Color(255, 255, 255, 255)
        self._background_color = Color(0, 0, 0, 180)
        self._red = Color(255, 0, 0, 255)
        self._font = pygame.freetype.Font("assets/OpenSansEmoji.ttf", 40)

        y = window.height * 0.95
        w = window.width
        h = window.height * 0.05

        self._background = UIRect(Rect(0, y, w, h), self._background_color)

        self._armor = UIText(Rect(20, y + 10, 150, h), self._white, self._font)
        self._damage = UIText(Rect(170, y + 10, 150, h), self._white, self._font)
        self._weapon = UIText(Rect(320, y + 10, 150, h), self._white, self._font)
        self._level = UIText(Rect(w - 300, y + 10, 300, h), self._white, self._font)

    @timer
    def draw(
        self,
        screen: Surface,
        armor: float,
        damage: float,
        weapon: ActiveWeapon,
        level_name: str,
    ):
        self._background.draw(screen)

        armor_color = self._red if armor < 10 else self._white
        self._armor.draw(screen, f"⛨{armor}", armor_color)
        self._damage.draw(screen, f"👊{damage}")
        self._weapon.draw(screen, "🔫" if weapon == ActiveWeapon.PRIMARY else "🚀")
        self._level.draw(screen, f"{level_name}")

    def resize(self):
        pass
