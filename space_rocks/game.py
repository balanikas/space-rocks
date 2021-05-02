import logging
from typing import Optional

import pygame
from pygame import surface, Vector2
from pygame.locals import *

import audio as sounds
import constants
from animation import init_animations, AnimationLibrary
from debug import Debug
from decorators import timer
from editing import LevelObserver
from effects import Sun, GradientEffect
import graphics as gfx
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
# todo check if player not rotated to avoid a rotozoom call
# todo key to toggle fullscreen but pygame.display.toggle_fullscreen() is buggy
# todo fix 3 nice playable balanced levels, settle tha, experiment on level4
# todo load default assets once and then level assets per level change. for performance
# todo asserts
# todo resizable window as constant flag
# todo detect monitors update rate Hz and set framerate dynamically to that. make sure game objects speed is correct
# todo autogenerate armor slowly
# todo show armor as bar
# todo less explosive sounds
# todo bounce related to sizes, small size bounce more
# todo better wallpaper
# todo better soundtrack
# todo more anims, and comment on why they suck on vsync
# todo black hole randomly appears
# todo electcity anim on player!
# todo refactor libs to non classes
# todo bouncing not accurate, shooting from behind has no impact
#


class Game:
    def set_level(self, level):
        self._world.set_current_level(level)

    def start_the_game(self):
        self._initialize_level()

    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        LevelObserver(
            self._initialize_level
        )  # file watcher that reloads a level on level change

        # very small buffer but sound lag still exists(est 0.2 - 0.4 secs).
        # Tried many hthings, perhaps just a pygame limitation
        pygame.mixer.pre_init(44100, -16, 2, 128)
        pygame.init()
        pygame.display.set_caption("experimental video game by balanikas@github")
        pygame.font.init()

        self._clock = pygame.time.Clock()
        self._state = GameState.NOT_RUNNING

        # having SCALED as flags enables vsync but fucks up most animations.
        flags = pygame.SCALED | pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF
        self._screen: surface.Surface = pygame.display.set_mode(
            (pygame.display.Info().current_w, pygame.display.Info().current_h),
            flags,
            32,
            vsync=1,
        )
        window.resize()

        self._debug = Debug(self._clock)
        self._ui = UI()
        self._hud = HUD()

        print_pygame_info()

        self._world = World(self._screen)
        self._level: Optional[Level]
        self._menu = Menu(
            self.set_level,
            self.start_the_game,
            self._world.get_all_levels(),
        )
        self._menu.menu.mainloop(self._screen)

        # self.set_level(0)
        # self.start_the_game()

    def _initialize_level(self):
        self._state = GameState.LOADING_LEVEL
        sounds.stop_all()
        level_id, level_name = self._world.get_current_level()
        sounds.init(level_name)
        sounds.play("change_level")

        gfx.init(level_name)
        init_animations(level_name)
        self._level = self._world.start_level(level_id)
        self._effects = []
        self._state = GameState.RUNNING

    def main_loop(self):
        while True:
            if self._state is GameState.LOADING_LEVEL:
                continue
            self._handle_input()
            self._process_game_logic()
            self._draw()
            self._cleanup()
            self._clock.tick_busy_loop(constants.FRAME_RATE)

    def _resize(self):
        window.resize()
        self._level.background.resize()
        self._level.player.resize()
        for a in self._level.enemies:
            a.resize()
        self._menu = Menu(
            self.set_level,
            self.start_the_game,
            self._world.get_all_levels(),
        )

    @timer
    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            elif event.type == VIDEORESIZE:
                pass
                # self._resize()
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
                if event.key == pygame.K_7:
                    self._state = GameState.RUNNING
                    self._world.set_previous_level()
                    self._initialize_level()
                if event.key == pygame.K_8:
                    self._state = GameState.RUNNING
                    self._initialize_level()
                if event.key == pygame.K_9:
                    self._state = GameState.RUNNING
                    self._world.advance_level()
                    self._initialize_level()

                if event.key == pygame.K_5:
                    self._effects = []
                    x = 0
                    y = 250
                    c = 0
                    for k, _ in AnimationLibrary._bank.items():
                        x += 250
                        c += 1
                        if c > 8:
                            y += 250
                            c = 0
                            x = 0
                        self._effects.append(
                            AnimationLibrary.load(k, Vector2(x, y), resize=(200, 200))
                        )

                if event.key == pygame.K_0:
                    for x in list(self._effects):
                        if type(x) is Sun or type(x) is GradientEffect:
                            self._effects.remove(x)

                    self._effects.append(Sun(Vector2(300, 300)))
                    self._effects.append(
                        GradientEffect(self._level.player.geometry.position)
                    )

                if event.key == pygame.K_1:
                    self._level.player.switch_weapon()
                if event.key == pygame.K_RETURN:
                    if self._state == GameState.WON:
                        self._world.advance_level()
                        self._initialize_level()
                    if self._state == GameState.LOST:
                        self._world.set_current_level(0)
                        self._initialize_level()

        is_key_pressed = pygame.key.get_pressed()

        if self._state is GameState.RUNNING and self._level.player:
            if is_key_pressed[pygame.K_RIGHT] or is_key_pressed[pygame.K_d]:
                self._level.player.rotate(clockwise=True)
            elif is_key_pressed[pygame.K_LEFT] or is_key_pressed[pygame.K_a]:
                self._level.player.rotate(clockwise=False)
            if is_key_pressed[pygame.K_UP] or is_key_pressed[pygame.K_w]:
                self._level.player.accelerate()
            if is_key_pressed[pygame.K_SPACE]:
                self._level.player.shoot()

    @timer
    def _process_game_logic(self):
        for e in self._effects:
            e.move()

        for game_object in self._level.game_objects:
            game_object.move(self._screen)

        player = self._level.player
        if player and not player.armor <= 0:
            for a in list(self._level.enemies):
                if collides_with(player.geometry, a.geometry):
                    if sprite_collide(player, a):
                        player_geo = player.geometry
                        player.hit(a.geometry, a.damage)
                        if player.armor <= 0:
                            self._effects.append(player.get_impact_animation())
                            self._state = GameState.LOST
                        a.hit(player_geo, player.damage)
                        if a.armor <= 0:
                            self._effects.append(a.get_impact_animation())
                            self._level.remove_enemy(a)
                        break

        for b in list(self._level.bullets):
            for a in list(self._level.enemies):
                if collides_with(a.geometry, b.geometry):
                    a.hit(b.geometry, b.damage)
                    if a.armor <= 0:
                        self._effects.append(a.get_impact_animation())
                        self._level.remove_enemy(a)
                    self._level.remove_bullet(b)
                    break

        if not self._level.enemies and self._level.player:
            self._state = GameState.WON

    @timer
    def _draw(self):
        self._level.background.draw(self._screen, self._level.player.geometry.position)

        for o in self._level.game_objects:
            o.draw(self._screen)

        for e in self._effects:
            e.draw(self._screen)

        # self._debug.draw_visual(self._screen, self._level.game_objects)
        self._debug.draw_text(
            self._screen,
            self._level.player.geometry.position,
            self._level.player.geometry.velocity,
            self._level.player.direction,
        )

        _, level_name = self._world.get_current_level()
        self._hud.draw(
            self._screen,
            self._level.player.armor,
            self._level.player.damage,
            self._level.player.active_weapon,
            level_name,
        )

        self._ui.draw(self._screen, self._state)

        pygame.display.flip()

    def _cleanup(self):
        for b in list(self._level.bullets):
            if not is_in_screen(self._screen, b.geometry):
                self._level.remove_bullet(b)

        for e in list(self._effects):
            if e.complete:
                self._effects.remove(e)
