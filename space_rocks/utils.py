from pygame.font import Font
from pygame.image import load
from pygame.math import Vector2
from pygame.mixer import Sound
from pygame.surface import Surface
from pygame import Color
import random

from geometry import Geometry

#from models import GameObject


def load_sprite(name: str, with_alpha: bool = True) -> Surface:
    path = f"assets/sprites/{name}.png"
    loaded_sprite = load(path)
    return loaded_sprite.convert_alpha() if with_alpha else loaded_sprite.convert()


def wrap_position(position: Vector2, surface: Surface):
    w, h = surface.get_size()
    return Vector2(position.x % w, position.y % h)


def get_random_position(surface: Surface):
    return Vector2(random.randrange(surface.get_width()), random.randrange(surface.get_height()))


def get_random_velocity(min_speed: int, max_speed: int):
    speed = random.randint(min_speed, max_speed)
    angle = random.randrange(0, 360)
    return Vector2(speed, 0).rotate(angle)


def load_sound(name: str):
    path = f"assets/sounds/{name}.wav"
    return Sound(path)


def print_text(surface: Surface, text: str, font: Font, color: Color = Color("tomato")):
    text_surface: Surface = font.render(text, True, color)
    rect = text_surface.get_rect()
    rect.center = Vector2(surface.get_size()) / 2
    surface.blit(text_surface, rect)

def collides_with(obj: Geometry, other_obj: Geometry) -> bool:
    distance = obj.position.distance_to(other_obj.position)
    return distance < obj.radius + other_obj.radius