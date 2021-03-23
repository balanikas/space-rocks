import time

import pygame
import random
from utils import load_sprite, get_random_position, print_text
from models import Spaceship, Asteroid
from pygame.transform import rotozoom


class SpaceRocks:
    MIN_ASTEROID_DISTANCE = 250

    def __init__(self):
        self._init_pygame()
        self.screen = pygame.display.set_mode((1000, 800))
        self.default_fill = (0, 0, 255)
        self.clock = pygame.time.Clock()
        self.background = load_sprite("space", False)
        self.font = pygame.font.Font(None, 64)
        self.message = ""
        pygame.font.init()
        self.stats = pygame.font.SysFont('Comic Sans MS', 20)
        self._initialize()


    def _initialize(self):
        self.bullets = []
        self.spaceship = Spaceship((500, 400), self.bullets.append)

        self.asteroids = []
        for _ in range(6):
            while True:
                position = get_random_position(self.screen)
                if (
                        position.distance_to(self.spaceship.position)
                        > self.MIN_ASTEROID_DISTANCE
                ):
                    break

            self.asteroids.append(Asteroid(position, self.asteroids.append))

    def main_loop(self):
        while True:
            self.start_time = time.perf_counter()
            self._handle_input()
            self._process_game_logic()
            self._draw()

    def _init_pygame(self):
        pygame.init()
        pygame.display.set_caption("Space Rocks")

    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                quit()
            elif (self.spaceship
                    and event.type == pygame.KEYDOWN
                    and event.key == pygame.K_SPACE
            ):
                self.spaceship.shoot()

        is_key_pressed = pygame.key.get_pressed()

        if self.spaceship:
            if is_key_pressed[pygame.K_RIGHT]:
                self.spaceship.rotate(clockwise=True)
            elif is_key_pressed[pygame.K_LEFT]:
                self.spaceship.rotate(clockwise=False)
            if is_key_pressed[pygame.K_UP]:
                self.spaceship.accelerate()
            if is_key_pressed[pygame.K_SPACE]:
                self.spaceship.shoot()

        if is_key_pressed[pygame.K_RETURN]:
            self.message = ""
            self._initialize()

    def _process_game_logic(self):

        for _ in range(150000):
            pass

        for game_object in self._get_game_objects():
            game_object.move(self.screen)

        if self.spaceship:
            for asteroid in self.asteroids:
                if asteroid.collides_with(self.spaceship):
                    self.spaceship = None
                    self.message = "You lost!"
                    break

        for bullet in self.bullets[:]:
            for asteroid in self.asteroids[:]:
                if asteroid.collides_with(bullet):
                    self.asteroids.remove(asteroid)
                    self.bullets.remove(bullet)
                    asteroid.split()
                    break

        for bullet in self.bullets[:]:
            if not self.screen.get_rect().collidepoint(bullet.position):
                self.bullets.remove(bullet)

        if not self.asteroids and self.spaceship:
            self.message = "You won!"

    def _draw(self):
        self.screen.blit(self.background, (0, 0))

        for game_object in self._get_game_objects():
            game_object.draw(self.screen)

        self._draw_stats()

        if self.message:
            print_text(self.screen, self.message, self.font)

        pygame.display.flip()
        self.clock.tick(60)

    def _draw_stats(self):
        end_time = time.perf_counter()
        ms_per_frame = 1000 / 60
        ms_since_start = (end_time - self.start_time) * 1000
        ms_wait_time_percent = (ms_since_start / ms_per_frame) * 100

        text_surface = self.stats.render(str(round(ms_wait_time_percent, 0)) + "%", False, (255, 255, 0))
        self.screen.blit(text_surface, (0, 0))

    def _get_game_objects(self):
        game_objects = [*self.asteroids, *self.bullets]

        if self.spaceship:
            game_objects.append(self.spaceship)

        return game_objects
