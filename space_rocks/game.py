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


# todo
# todo more accurate coll detection
# todo more sound effects
# todo more ..stuff: lifes, bonus, weapon types, etc
# todo: more asteroid sprites
# todo soundtrack
# todo profiling
# todo better bullet sprite
# todo move game logic to per-level?
# todo: find subclasses of Level and autocreate _levels
#  todo same badass sound for every menu change

class SpaceRocks:

    def set_level(self, value, level):
        self.level = self.world.get_level(level)

    def start_the_game(self):
        self._initialize()

    def __init__(self):
        self._init_pygame()

        self.clock = pygame.time.Clock()
        self.ellapsed_frames = 0
        self.state = GameState.NOT_RUNNING
        self.stats = Stats(self.clock)
        self.ui = UI()
        screen_size = (constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)
        self.screen: surface.Surface = pygame.display.set_mode(screen_size,
                                                               pygame.HWSURFACE)
        self.screen.fill((0, 0, 0))

        self.world = World(self.screen)
        self.level = self.world.get_current_level()

        self._menu = Menu(
            constants.SCREEN_WIDTH,
            constants.SCREEN_HEIGHT,
            self.set_level,
            self.start_the_game,
            self.screen)

    def _initialize(self):
        SoundLibrary.stop_all()
        self.state = GameState.RUNNING

    def main_loop(self):
        while True:
            self._handle_input()
            self._process_game_logic()
            self._draw()

    def _init_pygame(self):
        pygame.init()
        pygame.display.set_caption("Softwaroids")
        pygame.font.init()
        init_sounds()
        init_sprites()

    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._menu.menu.enable()
                self._menu.menu.mainloop(self.screen)

        is_key_pressed = pygame.key.get_pressed()

        if self.level.spaceship and self.state is GameState.RUNNING:
            if is_key_pressed[pygame.K_RIGHT]:
                self.level.spaceship.rotate(clockwise=True)
            elif is_key_pressed[pygame.K_LEFT]:
                self.level.spaceship.rotate(clockwise=False)
            if is_key_pressed[pygame.K_UP]:
                self.level.spaceship.accelerate()
            if is_key_pressed[pygame.K_SPACE]:
                if self.ellapsed_frames > 10:
                    self.level.spaceship.shoot()
                    self.ellapsed_frames = 0

        self.ellapsed_frames += 1

        if is_key_pressed[pygame.K_RETURN] and self.state is not GameState.RUNNING:
            if self.state == GameState.WON:
                self.level = self.world.get_next_level()
            if self.state == GameState.LOST:
                self.level = self.world.get_level(0)
            self._initialize()

        if is_key_pressed[pygame.K_1]:
            self.state = GameState.RUNNING
            self.level = self.world.get_level(0)
            self._initialize()

        if is_key_pressed[pygame.K_2]:
            self.state = GameState.RUNNING
            self.level = self.world.get_level(1)
            self._initialize()

        # quick switch level
        if is_key_pressed[pygame.K_z]:
            self.state = GameState.WON

    def _process_game_logic(self):

        if self.state is not GameState.RUNNING:
            return

        for game_object in self._get_game_objects():
            game_object.move(self.screen)

        if self.level.spaceship:
            for asteroid in self.level.asteroids:
                if collides_with(asteroid.geometry, self.level.spaceship.geometry):
                    self.level.remove_spaceship()
                    self.state = GameState.LOST
                    break

        for bullet in self.level.bullets[:]:
            for asteroid in self.level.asteroids[:]:
                if collides_with(asteroid.geometry, bullet.geometry):
                    self.level.remove_asteroid(asteroid)
                    self.level.remove_bullet(bullet)
                    asteroid.split()
                    break

        for bullet in self.level.bullets[:]:
            if not self.screen.get_rect().collidepoint(bullet.geometry.position):
                self.level.remove_bullet(bullet)

        if not self.level.asteroids and self.level.spaceship:
            self.state = GameState.WON

    def _draw(self):

        for game_object in self._get_game_objects():
            game_object.draw(self.screen)

        self.ui.draw(self.screen, self.state)

        pygame.display.flip()
        self.clock.tick(60)

    def _get_game_objects(self) -> List[GameObject]:
        game_objects: List[GameObject] = self.level.get_game_objects()
        game_objects.append(self.stats)

        return game_objects
