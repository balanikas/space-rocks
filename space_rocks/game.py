import logging
from typing import List, Optional

import pygame
from pygame import surface
from pygame.locals import *

import constants
from animation import init_animations, Animation
from audio import SoundLibrary, init_sounds
from debug import Debug
from editing import LevelObserver
from graphics import init_sprites
from hud import HUD
from levels import World, Level
from menu import Menu
from models import GameState
from ui import UI
from utils import collides_with, print_pygame_info, sprite_collide, is_in_screen
from window import window


# todo mouse over crashes game - The get_cursor method is unavailable in SDL2
# todo have a "record" option and record all game input and then replay it
# todo embed QT in the game window or vice versa, so game can be paused, .json file edited and restart game
# todo state machine for GameState ?
# todo https://realpython.com/pyinstaller-python/
# todo check if ship not rotated to avoid a rotozoom call
# todo key to toggle fullscreen but pygame.display.toggle_fullscreen() is buggy
# todo fix 3 nice playable balanced levels, settle tha, experiment on level4
# todo load default assets once and then level assets per level change. for performance


class SpaceRocks:
    def set_level(self, level):
        self._world.set_current_level(level)

    def start_the_game(self):
        self._initialize_level()

    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        LevelObserver(
            self._initialize_level
        )  # file watcher that reloads a level on level change
        pygame.mixer.pre_init(44100, -16, 2, 4096)
        pygame.init()
        pygame.display.set_caption("video game by Balanikas")
        pygame.font.init()

        self._clock = pygame.time.Clock()
        self._state = GameState.NOT_RUNNING
        self._debug = Debug(self._clock)
        self._ui = UI()
        self._hud = HUD()

        self._screen: surface.Surface = pygame.display.set_mode(
            window.size, pygame.RESIZABLE, 16
        )

        print_pygame_info()

        self._world = World(self._screen)
        self._level: Optional[Level]
        self._menu = Menu(
            self.set_level,
            self.start_the_game,
            self._world.get_all_levels(),
        )
        # self._menu.menu.mainloop(self._screen)

        self.set_level(0)
        self.start_the_game()

    def _initialize_level(self):
        self._state = GameState.LOADING_LEVEL
        SoundLibrary.stop_all()
        level_id, level_name = self._world.get_current_level()
        init_sounds(level_name)
        SoundLibrary.play("change_level")

        init_sprites(level_name)
        init_animations(level_name)
        self._level = self._world.start_level(level_id)
        self._effects: List[Animation] = []
        self._state = GameState.RUNNING

    def main_loop(self):
        while True:
            if self._state is GameState.LOADING_LEVEL:
                continue
            self._handle_input()
            self._process_game_logic()
            self._draw()
            self._cleanup()

    def _resize(self):
        window.resize()
        self._level.background.resize()
        self._level.ship.resize()
        for a in self._level.asteroids:
            a.resize()
        self._menu = Menu(
            self.set_level,
            self.start_the_game,
            self._world.get_all_levels(),
        )

    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            elif event.type == VIDEORESIZE:
                self._resize()
            elif event.type == VIDEOEXPOSE:  # handles window minimising/maximising
                pass

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._menu.menu.enable()
                    self._menu.menu.mainloop(self._screen)

                # for debugging
                if event.key == pygame.K_q:
                    self._debug.enabled = not self._debug.enabled
                if event.key == pygame.K_z:
                    self._state = GameState.WON
                if event.key == pygame.K_5:
                    self._state = GameState.RUNNING
                    self._world.set_current_level(0)
                    self._initialize_level()
                if event.key == pygame.K_6:
                    self._state = GameState.RUNNING
                    self._world.set_current_level(1)
                    self._initialize_level()
                if event.key == pygame.K_7:
                    self._state = GameState.RUNNING
                    self._world.set_current_level(2)
                    self._initialize_level()

                if event.key == pygame.K_1:
                    self._level.ship.switch_weapon()
                if event.key == pygame.K_RETURN:
                    if self._state == GameState.WON:
                        self._world.advance_level()
                        self._initialize_level()
                    if self._state == GameState.LOST:
                        self._world.set_current_level(0)
                        self._initialize_level()

        is_key_pressed = pygame.key.get_pressed()

        if self._state is GameState.RUNNING and self._level.ship:
            if is_key_pressed[pygame.K_RIGHT] or is_key_pressed[pygame.K_d]:
                self._level.ship.rotate(clockwise=True)
            elif is_key_pressed[pygame.K_LEFT] or is_key_pressed[pygame.K_a]:
                self._level.ship.rotate(clockwise=False)
            if is_key_pressed[pygame.K_UP] or is_key_pressed[pygame.K_w]:
                self._level.ship.accelerate()
            if is_key_pressed[pygame.K_SPACE]:
                self._level.ship.shoot()

    def _process_game_logic(self):
        for e in self._effects:
            e.move()

        for game_object in self._level.game_objects:
            game_object.move(self._screen)

        ship = self._level.ship
        if ship and not ship.dead:

            for a in list(self._level.asteroids):

                if collides_with(ship.geometry, a.geometry):
                    if sprite_collide(ship, a):
                        ship_geo = ship.geometry
                        ship_anim = ship.hit(a.geometry, a.damage)
                        if ship_anim:
                            self._effects.append(ship_anim)
                            self._state = GameState.LOST

                        a_anim = a.hit(ship_geo, ship.damage)
                        if a_anim:
                            self._effects.append(a_anim)
                            self._level.remove_asteroid(a)

                        break

        for b in list(self._level.bullets):
            for a in list(self._level.asteroids):
                if collides_with(a.geometry, b.geometry):
                    a_anim = a.hit(b.geometry, b.damage)
                    if a_anim:
                        self._effects.append(a_anim)
                        self._level.remove_asteroid(a)
                    self._level.remove_bullet(b)
                    break

        for b in list(self._level.bullets):
            if not is_in_screen(self._screen, b.geometry):
                self._level.remove_bullet(b)

        if not self._level.asteroids and self._level.ship:
            self._state = GameState.WON

    def _draw(self):
        self._level.background.draw(self._screen, self._level.ship.geometry.position)

        for o in self._level.game_objects:
            o.draw(self._screen)

        for e in self._effects:
            e.draw(self._screen)

        # self._debug.draw_visual(self._screen, self._level.game_objects)
        self._debug.draw_text(
            self._screen,
            self._level.ship.geometry.position,
            self._level.ship.geometry.velocity,
            self._level.ship.direction,
        )

        _, level_name = self._world.get_current_level()
        self._hud.draw(
            self._screen,
            self._level.ship.armor,
            self._level.ship.damage,
            self._level.ship._active_weapon,
            level_name,
        )

        self._ui.draw(self._screen, self._state)

        pygame.display.flip()
        self._clock.tick(constants.FRAME_RATE)

    def _cleanup(self):
        for e in list(self._effects):
            if e.complete:
                self._effects.remove(e)
