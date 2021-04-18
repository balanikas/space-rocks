import logging
from typing import List, Optional

import pygame
from pygame import surface
from pygame.locals import *

from audio import SoundLibrary, init_sounds
from graphics import init_sprites
from menu import Menu
from models import GameObject, Stats, UI, GameState, Animation
from space_rocks.editing import FileHandler
from space_rocks.levels import World, Level
from space_rocks.window import window
from utils import collides_with, print_info

from watchdog.observers import Observer


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
# todo on ship collision animation freezes
# todo organize imports
# todo fix 3 nice playable balanced levels, settle tha, experiment on level4
# todo add ADSW key layout, place debug somehwere else
# todo pressing enter in middle of gaem shoudlnt be allowed
# todo add toughness param to asteroids
# todo variable size of explosion, maybe as json prop
# todo correct the speed of bullets, should be constant across win sizes


class SpaceRocks:
    def set_level(self, level):
        self._world.set_current_level(level)

    def start_the_game(self):
        self._initialize_level()

    def __init__(self):
        logging.basicConfig(level=logging.INFO)

        event_handler = FileHandler(self._initialize_level)
        observer = Observer()
        observer.schedule(event_handler, f"../levels/", recursive=True)
        observer.start()

        pygame.mixer.pre_init(44100, -16, 2, 4096)
        pygame.init()
        pygame.display.set_caption("video game by Balanikas")
        pygame.font.init()
        print_info()

        self._debug = False
        self._clock = pygame.time.Clock()
        self._ellapsed_frames = 0
        self._state = GameState.NOT_RUNNING
        self._stats = Stats(self._clock)
        self._ui = UI()
        flags = pygame.RESIZABLE
        self._screen: surface.Surface = pygame.display.set_mode(window.size, flags, 16)
        self._screen.fill((0, 0, 0))

        self._world = World(self._screen)
        self._level: Optional[Level]
        self._menu = Menu(
            self.set_level,
            self.start_the_game,
            self._world.get_all_levels(),
        )
        self._menu.menu.mainloop(self._screen)

    def _initialize_level(self):
        self._state = GameState.LOADING_LEVEL
        SoundLibrary.stop_all()

        current_level = self._world.get_current_level()
        init_sounds(current_level[1])
        init_sprites(current_level[1])
        self._level = self._world.start_level(current_level[0])
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
                if event.key == pygame.K_d:
                    self._debug = not self._debug
                if event.key == pygame.K_z:
                    self._state = GameState.WON
                if event.key == pygame.K_1:
                    self._state = GameState.RUNNING
                    self._level = self._world.set_current_level(0)
                    self._initialize_level()
                if event.key == pygame.K_2:
                    self._state = GameState.RUNNING
                    self._level = self._world.set_current_level(1)
                    self._initialize_level()
                if event.key == pygame.K_3:
                    self._state = GameState.RUNNING
                    self._level = self._world.set_current_level(2)
                    self._initialize_level()

                if event.key == pygame.K_RETURN:
                    if self._state == GameState.WON:
                        self._level = self._world.advance_level()
                    if self._state == GameState.LOST:
                        self._level = self._world.set_current_level(0)
                    self._initialize_level()

        is_key_pressed = pygame.key.get_pressed()

        if self._state is GameState.RUNNING and self._level.spaceship:
            if is_key_pressed[pygame.K_RIGHT]:
                self._level.spaceship.rotate(clockwise=True)
            elif is_key_pressed[pygame.K_LEFT]:
                self._level.spaceship.rotate(clockwise=False)
            if is_key_pressed[pygame.K_UP]:
                self._level.spaceship.accelerate()
            if is_key_pressed[pygame.K_SPACE]:
                if self._ellapsed_frames > 10:
                    self._level.spaceship.shoot()
                    self._ellapsed_frames = 0

        self._ellapsed_frames += 1

    def _process_game_logic(self):

        if self._state is not GameState.RUNNING:
            return

        for game_object in self._get_game_objects():
            game_object.move(self._screen)

        for e in self._effects:
            e.move()

        if self._level.spaceship:

            self._level.spaceship.rect.center = self._level.spaceship.geometry.position
            for asteroid in self._level.asteroids:
                asteroid.rect.center = asteroid.geometry.position

                if pygame.sprite.spritecollide(
                    self._level.spaceship,
                    pygame.sprite.Group(asteroid),
                    False,
                    pygame.sprite.collide_mask,
                ):
                    self._effects.append(
                        Animation("explosion", asteroid.geometry.position)
                    )
                    # self._level.remove_spaceship()
                    #self._state = GameState.LOST
                    break

        for bullet in self._level.bullets[:]:
            for asteroid in self._level.asteroids[:]:
                if collides_with(asteroid.geometry, bullet.geometry):
                    self._effects.append(
                        Animation("explosion", asteroid.geometry.position)
                    )
                    self._level.remove_asteroid(asteroid)
                    self._level.remove_bullet(bullet)
                    asteroid.split()
                    break

        for bullet in self._level.bullets[:]:
            if not self._screen.get_rect().collidepoint(bullet.geometry.position):
                self._level.remove_bullet(bullet)

        if not self._level.asteroids and self._level.spaceship:
            self._state = GameState.WON

    def _draw(self):

        self._level.background.draw(
            self._screen, self._level.spaceship.geometry.position
        )

        for o in self._get_game_objects():
            o.draw(self._screen)

        for e in self._effects:
            e.draw(self._screen)

        if self._debug:
            for o in self._get_game_objects():
                if hasattr(o, "image"):
                    pygame.draw.polygon(
                        o.image,
                        (0, 255, 0),
                        pygame.mask.from_surface(o.image).outline(),
                        1,
                    )
                    rect = o.rect
                    pygame.draw.rect(
                        self._screen,
                        (0, 0, 255),
                        (
                            o.geometry.position.x - (rect.width / 2),
                            o.geometry.position.y - (rect.height / 2),
                            rect.width,
                            rect.height,
                        ),
                        1,
                    )

            self._stats.draw(
                self._screen,
                self._level.spaceship.geometry.position,
                self._level.spaceship.geometry.velocity,
                self._level.spaceship._direction,
            )

        self._ui.draw(self._screen, self._state)

        pygame.display.flip()
        self._clock.tick(60)

    def _get_game_objects(self) -> List[GameObject]:
        return self._level.get_game_objects()


