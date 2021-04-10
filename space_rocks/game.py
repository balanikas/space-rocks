from typing import List

import pygame
from pygame import surface

import constants
from audio import SoundLibrary, init_sounds
from graphics import init_sprites
from menu import Menu
from models import GameObject, Stats, UI, GameState
from space_rocks.levels import World
from utils import collides_with


# todo more accurate coll detection
# todo more sound effects
# todo more ..stuff: lifes, bonus, weapon types, etc
# todo: more asteroid sprites
# todo soundtrack
# todo profiling
# todo move game logic to per-level?
# todo: find subclasses of Level and autocreate _levels
#  todo same badass sound for every menu change
# todo extract asteroid split into props
# todo paralax effect on background
# todo make internet fetched level

class SpaceRocks:

    def set_level(self, value, level):
        self._world.set_current_level(level)

    def start_the_game(self):
        self._initialize()

    def __init__(self):
        self._init_pygame()

        self._debug = False
        self._clock = pygame.time.Clock()
        self._ellapsed_frames = 0
        self._state = GameState.NOT_RUNNING
        self._stats = Stats(self._clock)
        self._ui = UI()
        screen_size = (constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)
        self._screen: surface.Surface = pygame.display.set_mode(screen_size,
                                                                pygame.HWSURFACE)
        self._screen.fill((0, 0, 0))

        self._world = World(self._screen)

        self._menu = Menu(
            constants.SCREEN_WIDTH,
            constants.SCREEN_HEIGHT,
            self.set_level,
            self.start_the_game,
            self._screen,
            self._world.get_all_levels())

    def _initialize(self):
        SoundLibrary.stop_all()

        current_level = self._world.get_current_level()
        init_sounds(current_level[1])
        init_sprites(current_level[1])
        self._level = self._world.start_level(current_level[0])
        self._state = GameState.RUNNING

    def main_loop(self):
        while True:
            self._handle_input()
            self._process_game_logic()
            self._draw()

    def _init_pygame(self):
        pygame.init()
        pygame.display.set_caption("Softwaroids")
        pygame.font.init()

    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

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
                    self._initialize()
                if event.key == pygame.K_2:
                    self._state = GameState.RUNNING
                    self._level = self._world.set_current_level(1)
                    self._initialize()
                if event.key == pygame.K_3:
                    self._state = GameState.RUNNING
                    self._level = self._world.set_current_level(2)
                    self._initialize()

                if event.key == pygame.K_RETURN and self._state is not GameState.RUNNING:
                    if self._state == GameState.WON:
                        self._level = self._world.advance_level()
                    if self._state == GameState.LOST:
                        self._level = self._world.set_current_level(0)
                    self._initialize()

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

        if self._level.spaceship:

            self._level.spaceship.rect.center = self._level.spaceship.geometry.position
            for asteroid in self._level.asteroids:
                asteroid.rect.center = asteroid.geometry.position

                if pygame.sprite.spritecollide(self._level.spaceship, pygame.sprite.Group(asteroid), False,
                                               pygame.sprite.collide_mask):
                    # self._level.remove_spaceship()
                    self._state = GameState.LOST
                    break

        for bullet in self._level.bullets[:]:
            for asteroid in self._level.asteroids[:]:
                if collides_with(asteroid.geometry, bullet.geometry):
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

        if self._state is GameState.NOT_RUNNING:
            return

        for o in self._get_game_objects():
            o.draw(self._screen)

        if self._debug:
            for o in self._get_game_objects():
                if hasattr(o, "image"):
                    pygame.draw.polygon(o.image, (0, 255, 0), pygame.mask.from_surface(o.image).outline(), 1)
                    rect = o.rect
                    pygame.draw.rect(
                        self._screen,
                        (0, 0, 255),
                        (
                            o.geometry.position.x - (rect.width / 2), o.geometry.position.y - (rect.height / 2),
                            rect.width,
                            rect.height),
                        1
                    )

            self._stats.draw(self._screen)

        self._ui.draw(self._screen, self._state)

        pygame.display.flip()
        self._clock.tick(60)

    def _get_game_objects(self) -> List[GameObject]:
        game_objects: List[GameObject] = self._level.get_game_objects()

        return game_objects
