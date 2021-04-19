import logging
from typing import List, Optional

import pygame
from pygame import surface
from pygame.locals import *

from audio import SoundLibrary, init_sounds
from graphics import init_sprites
from menu import Menu
from models import GameState, UI
from debug import Debug
from space_rocks.animation import init_animations, Animation
from space_rocks.editing import LevelObserver
from space_rocks.levels import World, Level
from space_rocks.window import window
from utils import collides_with, print_pygame_info

# todo more accurate coll detection
# todo profiling: add flags to control stuff: enable_coldet, enable_rotation, enable_bla.. see perf graph and optimize.
# todo move game logic to per-level?
# todo edge bounce a bit buggy, fix
# todo even bounce asteroids? appearing/dissapearing looks not good, clipping, etc
# todo mouse over crashes game - The get_cursor method is unavailable in SDL2
# todo create a RAL (rendering abstraction layer) so i can switch from SDL to other
# todo game idea: 9 types of planets, each with own props like toughness, speed, how they split, rotation
# todo game idea: asutogenerated levels with increasing difficulty
# todo game idea: keep score, and perhaps highscore
# todo have a "record" option and record all game input and then replay it
# todo embed QT in the game window or vice versa, so game can be paused, .json file edited and restart game
# todo state machine for GameState ?
# todo https://realpython.com/pyinstaller-python/
# todo check if ship not rotated to avoid a rotozoom call
# todo https://realpython.com/python-logging-source-code/#what-does-getlogger-really-do
# todo find catastrophic errors, print error and raise SystemExit
# todo key to toggle fullscreen but pygame.display.toggle_fullscreen() is buggy
# todo organize imports
# todo fix 3 nice playable balanced levels, settle tha, experiment on level4
# todo correct the speed of bullets, should be constant across win sizes
# todo load assets in parallel for speedup


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
        print_pygame_info()

        self._clock = pygame.time.Clock()
        self._state = GameState.NOT_RUNNING
        self._debug = Debug(self._clock)
        self._ui = UI()
        self._screen: surface.Surface = pygame.display.set_mode(
            window.size, pygame.RESIZABLE, 16
        )
        self._screen.fill((0, 0, 0))

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

    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            elif event.type == VIDEORESIZE:
                window.resize()
                self._level.background.resize()
                self._level.spaceship.resize()
                for a in self._level.asteroids:
                    a.resize()
                self._menu = Menu(
                    self.set_level,
                    self.start_the_game,
                    self._world.get_all_levels(),
                )

            elif event.type == VIDEOEXPOSE:  # handles window minimising/maximising
                pass

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._menu.menu.enable()
                    self._menu.menu.mainloop(self._screen)
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
                    self._level.spaceship.switch_weapon()
                if event.key == pygame.K_RETURN:
                    if self._state == GameState.WON:
                        self._world.advance_level()
                        self._initialize_level()
                    if self._state == GameState.LOST:
                        self._world.set_current_level(0)
                        self._initialize_level()

        is_key_pressed = pygame.key.get_pressed()

        if self._state is GameState.RUNNING and self._level.spaceship:
            if is_key_pressed[pygame.K_RIGHT] or is_key_pressed[pygame.K_d]:
                self._level.spaceship.rotate(clockwise=True)
            elif is_key_pressed[pygame.K_LEFT] or is_key_pressed[pygame.K_a]:
                self._level.spaceship.rotate(clockwise=False)
            if is_key_pressed[pygame.K_UP] or is_key_pressed[pygame.K_w]:
                self._level.spaceship.accelerate()
            if is_key_pressed[pygame.K_SPACE]:
                self._level.spaceship.shoot()

    def _process_game_logic(self):
        for e in self._effects:
            e.move()

        if self._state is not GameState.RUNNING:
            return

        for game_object in self._level.get_game_objects():
            game_object.move(self._screen)

        ship = self._level.spaceship
        if ship:
            ship.rect.center = ship.geometry.position
            for a in self._level.asteroids:
                a.rect.center = a.geometry.position
                if pygame.sprite.spritecollide(
                    ship,
                    pygame.sprite.Group(a),
                    False,
                    pygame.sprite.collide_mask,
                ):
                    self._effects.append(ship.hit())
                    # self._level.remove_spaceship()
                    self._level.remove_asteroid(a)
                    self._state = GameState.LOST
                    break

        for b in list(self._level.bullets):
            for a in list(self._level.asteroids):
                if collides_with(a.geometry, b.geometry):
                    a.hit(b.geometry.velocity, b.props.damage)
                    if a.get_armor() <= 0:
                        anim = a.destroy()
                        self._effects.append(anim)
                        self._level.remove_asteroid(a)
                        a.split()
                    self._level.remove_bullet(b)
                    break

        for b in list(self._level.bullets):
            if not self._screen.get_rect().collidepoint(b.geometry.position):
                self._level.remove_bullet(b)

        if not self._level.asteroids and self._level.spaceship:
            self._state = GameState.WON

    def _draw(self):
        self._level.background.draw(
            self._screen, self._level.spaceship.geometry.position
        )

        for o in self._level.get_game_objects():
            o.draw(self._screen)

        for e in self._effects:
            e.draw(self._screen)

        self._debug.draw_visual(self._screen, self._level.get_game_objects())
        self._debug.draw_text(
            self._screen,
            self._level.spaceship.geometry.position,
            self._level.spaceship.geometry.velocity,
            self._level.spaceship.direction,
        )

        self._ui.draw(self._screen, self._state)

        pygame.display.flip()
        self._clock.tick(60)
