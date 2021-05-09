from typing import Callable, List, Tuple

import pygame_menu
from pygame import Color
from pygame_menu import sound

from space_rocks import constants
from space_rocks.window import window


class Menu:
    def __init__(
            self,
            on_change_level: Callable,
            on_start_game: Callable,
            all_levels: List[Tuple[str, int]],
    ):
        engine = sound.Sound()
        engine.set_sound(
            sound.SOUND_TYPE_EVENT, f"{constants.SOUND_ASSETS_ROOT}menu/default.wav"
        )

        theme = pygame_menu.themes.THEME_DARK.copy()
        theme.set_background_color_opacity(0.3)
        theme.title_bar_style = pygame_menu.widgets.MENUBAR_STYLE_NONE
        theme.widget_font_size = int(50 * min(window.factor.x, window.factor.y))
        theme.selection_color = Color(0, 255, 0)
        self.menu = pygame_menu.Menu(
            "menu",
            window.width * 0.8,
            window.height * 0.8,
            theme=theme,
            onclose=pygame_menu.events.CLOSE,
        )

        self.menu.get_menubar().hide()

        def on_select_level(_, level):
            self.menu.get_sound().play_event()
            on_change_level(level)

        self.menu.add.selector("Select level :", all_levels, onchange=on_select_level)
        self.menu.add.button("Play", lambda: (self.menu.disable(), on_start_game()))
        self.menu.add.button("Quit", pygame_menu.events.EXIT)

        self.menu.set_sound(engine, recursive=True)
        for w in self.menu.get_widgets():
            w.set_onselect(self.menu.get_sound().play_event)
