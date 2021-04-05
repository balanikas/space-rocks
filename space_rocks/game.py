from typing import List

import pygame
from pygame import surface

from audio import SoundLibrary, init_sounds
from graphics import init_sprites
from models import GameObject, Stats, UI, GameState
from space_rocks.levels import Level, Level2
from utils import collides_with


class SpaceRocks:

    def __init__(self):
        self._init_pygame()

        self.clock = pygame.time.Clock()
        self.ellapsed_frames = 0
        self.state = GameState.NOT_RUNNING

        self._initialize()
        self.level = Level(self.screen)

    def _initialize(self):

        self._init_pygame()

        display_info = pygame.display.Info()
        screen_size = (display_info.current_w - 100, display_info.current_h - 100)
        self.screen: surface.Surface = pygame.display.set_mode(screen_size,
                                                               pygame.HWSURFACE)
        self.screen.fill((0, 0, 0))
        self.state = GameState.RUNNING
        self.stats = Stats(self.clock)
        self.ui = UI()

        print("initialized")

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
            if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                quit()

        is_key_pressed = pygame.key.get_pressed()

        if self.level.spaceship:
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

        if is_key_pressed[pygame.K_RETURN]:
            if self.state == GameState.WON:
                self.level = Level2(self.screen)
            if self.state == GameState.LOST:
                self.level = Level(self.screen)
            SoundLibrary.stop("background")
            self._initialize()

    def _process_game_logic(self):

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

        # quick switch level
        is_key_pressed = pygame.key.get_pressed()
        if is_key_pressed[pygame.K_z]:
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
