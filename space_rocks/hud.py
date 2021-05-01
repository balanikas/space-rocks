import pygame
import pygame.freetype
from pygame import Surface, Rect, Color

from player import ActiveWeapon
from window import window


class UIComponent:
    def __init__(self, rect: Rect, color: Color):
        self._surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        self._rect = rect
        self._color = color
        self._font = pygame.freetype.Font(f"../assets/OpenSansEmoji.ttf", 40)

    def draw_text(self, surface: Surface, text, color: Color = None):
        color = color if color else self._color
        text_surface, _ = self._font.render(text, color, None)
        surface.blit(text_surface, self._rect)


class UIComponentRect:
    def __init__(self, rect: Rect, color: Color):
        self._surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        self._surface.fill((255, 255, 255, 50))
        self._rect = rect
        self._color = color

    def draw(self, surface: Surface, color: Color = None):
        color = color if color else self._color
        surface.blit(self._surface, (self._rect.x, self._rect.y))
        # pygame.draw.rect(surface, Color(1,100,0,120), self._rect)
        # self._surface.blit(surface, self._rect)


class HUD:
    def __init__(self):
        self._green = Color(0, 255, 0, 255)
        self._background_color = Color(100, 100, 100, 128)
        self._red = Color(255, 0, 0, 255)
        y = window.height * 0.95
        h = window.height * 0.1

        self._armor = UIComponent(Rect(20, y + 10, 200, h), self._green)
        self._damage = UIComponent(Rect(180, y + 10, 50, h), self._green)
        self._weapon = UIComponent(Rect(window.width - 50, y + 10, 200, h), self._green)
        self._level = UIComponent(
            Rect(window.center[0] - 50, y + 10, 200, h), self._green
        )
        self._background = UIComponentRect(
            Rect(0, y, window.width, h), self._background_color
        )

    def draw(
        self,
        screen: Surface,
        armor: float,
        damage: float,
        weapon: ActiveWeapon,
        level_name: str,
    ):
        armor_color = self._red if armor < 10 else None
        self._armor.draw_text(screen, f"⛨{armor}", armor_color)
        self._damage.draw_text(screen, f"👊{damage}")
        self._weapon.draw_text(screen, f"⛋" if weapon == ActiveWeapon.PRIMARY else f"🚀")
        self._level.draw_text(screen, f"{level_name}")
        self._background.draw(screen)

    def resize(self):
        pass
