import time
from typing import List

import pygame

from pygame import Vector2, surface
from audio import SoundLibrary, init_sounds

from models import Asteroid, GameObject, Spaceship, Bullet
from utils import collides_with, get_random_position, load_sprite, print_text


class SpaceRocks:
    MIN_ASTEROID_DISTANCE = 250

    def __init__(self):
        self._init_pygame()
        self.screen: surface.Surface = pygame.display.set_mode((1000, 800))
        self.clock = pygame.time.Clock()
        self.background = load_sprite("space", False)
        self.font = pygame.font.Font(None, 64)
        self.message = ""
        self.ellapsed_frames = 0
        pygame.font.init()
        self.stats = pygame.font.SysFont(None, 20)

        self._initialize()

    def _initialize(self):

        SoundLibrary.play("background")
        self.bullets: List[Bullet] = []
        self.spaceship = Spaceship(Vector2(500, 400), self.bullets.append)

        self.asteroids: List[Asteroid] = []
        for _ in range(6):
            while True:
                position = get_random_position(self.screen)
                if (position.distance_to(self.spaceship.geometry.position) > self.MIN_ASTEROID_DISTANCE):
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
        init_sounds()

    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
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
                if(self.ellapsed_frames > 20):
                    self.spaceship.shoot()
                    self.ellapsed_frames = 0

        self.ellapsed_frames += 1   

        if is_key_pressed[pygame.K_RETURN]:
            SoundLibrary.stop("background")
            self.message = ""
            self._initialize()

    def _process_game_logic(self):

        for game_object in self._get_game_objects():
            game_object.move(self.screen)

        if self.spaceship:
            for asteroid in self.asteroids:
                if collides_with(asteroid.geometry, self.spaceship.geometry):
                    self.spaceship = None
                    self.message = "You lost! Press RETURN to replay"
                    break

        for bullet in self.bullets[:]:
            for asteroid in self.asteroids[:]:
                if  collides_with(asteroid.geometry,bullet.geometry):
                    self.asteroids.remove(asteroid)
                    self.bullets.remove(bullet)
                    asteroid.split()
                    break

        for bullet in self.bullets[:]:
            if not self.screen.get_rect().collidepoint(bullet.geometry.position):
                self.bullets.remove(bullet)

        if not self.asteroids and self.spaceship:
            self.message = "You won! Press RETURN to replay"

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

        text_surface = self.stats.render(
            str(round(ms_wait_time_percent, 0)) + "%", False, (255, 255, 0)
        )
        self.screen.blit(text_surface, (0, 0))

    def _get_game_objects(self) -> List[GameObject]:
        game_objects: List[GameObject] = [*self.asteroids, *self.bullets]

        if self.spaceship:
            game_objects.append(self.spaceship)

        return game_objects
