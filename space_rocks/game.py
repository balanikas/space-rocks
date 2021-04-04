from typing import List

import pygame
from pygame import Vector2, surface

from audio import SoundLibrary, init_sounds
from graphics import init_sprites
from models import Asteroid, GameObject, Spaceship, Bullet, Stats, UI, GameState, Background
from utils import collides_with, get_random_position


class SpaceRocks:
    MIN_ASTEROID_DISTANCE = 250

    def __init__(self):
        self._init_pygame()
        self.screen: surface.Surface = pygame.display.set_mode((1200, 1000),
                                                               pygame.HWSURFACE)
        self.clock = pygame.time.Clock()
        self.ellapsed_frames = 0
        self.state = GameState.NOT_RUNNING

        self._initialize()

    def _initialize(self):

        self.state = GameState.RUNNING
        self.stats = Stats(self.clock)
        self.ui = UI()

        self.background = Background()
        self.bullets: List[Bullet] = []
        self.spaceship = Spaceship(Vector2(500, 400), self.bullets.append)
        self.asteroids: List[Asteroid] = []
        for _ in range(6):
            while True:
                position = get_random_position(self.screen)
                if (
                        position.distance_to(self.spaceship.geometry.position)
                        > self.MIN_ASTEROID_DISTANCE
                ):
                    break

            self.asteroids.append(Asteroid(position, self.asteroids.append))

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

        if self.spaceship:
            if is_key_pressed[pygame.K_RIGHT]:
                self.spaceship.rotate(clockwise=True)
            elif is_key_pressed[pygame.K_LEFT]:
                self.spaceship.rotate(clockwise=False)
            if is_key_pressed[pygame.K_UP]:
                self.spaceship.accelerate()
            if is_key_pressed[pygame.K_SPACE]:
                if self.ellapsed_frames > 20:
                    self.spaceship.shoot()
                    self.ellapsed_frames = 0

        self.ellapsed_frames += 1

        if is_key_pressed[pygame.K_RETURN]:
            SoundLibrary.stop("background")
            self._initialize()

    def _process_game_logic(self):

        for game_object in self._get_game_objects():
            game_object.move(self.screen)

        if self.spaceship:
            for asteroid in self.asteroids:
                if collides_with(asteroid.geometry, self.spaceship.geometry):
                    self.spaceship = None
                    self.state = GameState.LOST
                    break

        for bullet in self.bullets[:]:
            for asteroid in self.asteroids[:]:
                if collides_with(asteroid.geometry, bullet.geometry):
                    self.asteroids.remove(asteroid)
                    self.bullets.remove(bullet)
                    asteroid.split()
                    break

        for bullet in self.bullets[:]:
            if not self.screen.get_rect().collidepoint(bullet.geometry.position):
                self.bullets.remove(bullet)

        if not self.asteroids and self.spaceship:
            self.state = GameState.WON

    def _draw(self):

        for game_object in self._get_game_objects():
            game_object.draw(self.screen)

        self.ui.draw(self.screen, self.state)

        pygame.display.flip()
        self.clock.tick(60)

    def _get_game_objects(self) -> List[GameObject]:
        game_objects: List[GameObject] = [self.background, *self.asteroids, *self.bullets, self.stats]

        if self.spaceship:
            game_objects.append(self.spaceship)

        return game_objects
