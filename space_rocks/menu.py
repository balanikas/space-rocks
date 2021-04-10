from typing import Callable, List, Tuple

import pygame_menu
from pygame.surface import Surface
from pygame_menu import sound


class Menu:
    def __init__(
            self,
            width: int,
            height: int,
            on_change_level: Callable,
            on_start_game: Callable,
            screen: Surface,
            all_levels: List[Tuple[str, int]]
    ):
        widget_colors_theme = pygame_menu.themes.THEME_BLUE.copy()
        widget_colors_theme.set_background_color_opacity(0.5)

        engine = sound.Sound()
        engine.set_sound(sound.SOUND_TYPE_EVENT, "../assets/sounds/menu/confirmation_001.ogg")

        self.menu = pygame_menu.Menu(
            "menu",
            width - 400,
            height - 400,
            theme=widget_colors_theme,
            onclose=pygame_menu.events.CLOSE)

        self.menu.add.selector('Select level :', all_levels, onchange=on_change_level)
        self.menu.add.button('Play', lambda: (self.menu.disable(), on_start_game()))
        self.menu.add.button('Quit', pygame_menu.events.CLOSE)

        self.menu.set_sound(engine, recursive=True)
        for w in self.menu.get_widgets():
            w.set_onselect(self.menu.get_sound().play_event)
        self.menu.mainloop(screen)
