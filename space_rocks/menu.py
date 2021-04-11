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
        engine = sound.Sound()
        engine.set_sound(sound.SOUND_TYPE_EVENT, "../assets/sounds/menu/confirmation_001.ogg")

        theme = pygame_menu.themes.THEME_DARK.copy()
        theme.set_background_color_opacity(0)
        theme.title_bar_style = pygame_menu.widgets.MENUBAR_STYLE_NONE
        theme.widget_font_size = 60
        self.menu = pygame_menu.Menu(
            "menu",
            width * 0.8,
            height * 0.8,
            theme=theme,
            onclose=pygame_menu.events.CLOSE)

        self.menu.get_menubar().hide()

        # self.menu.set_onmouseover(None)

        def on_select_level(x, level):
            self.menu.get_sound().play_event()
            on_change_level(level)

        self.menu.add.selector('Select level :', all_levels, onchange=on_select_level)
        self.menu.add.button('Play', lambda: (self.menu.disable(), on_start_game()))
        self.menu.add.button('Quit', pygame_menu.events.EXIT)

        self.menu.set_sound(engine, recursive=True)
        for w in self.menu.get_widgets():
            w.set_onselect(self.menu.get_sound().play_event)

        def main_background() -> None:
            background_image = pygame_menu.BaseImage(
                image_path=pygame_menu.baseimage.IMAGE_EXAMPLE_METAL)
            background_image.draw(screen)

        self.menu.mainloop(screen)
