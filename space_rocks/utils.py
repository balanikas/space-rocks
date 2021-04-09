import random

from pygame.math import Vector2
from pygame.surface import Surface

from geometry import Geometry


def PixelPerfectCollision(obj1, obj2):
    """
    If the function finds a collision, it will return True;
    if not, it will return False. If one of the objects is
    not the intended type, the function instead returns None.
    """
    try:
        # create attributes
        rect1, mask1, blank1 = obj1.rect, obj1.hitmask, obj1.blank
        rect2, mask2, blank2 = obj2.rect, obj2.hitmask, obj2.blank
        # initial examination
        if rect1.colliderect(rect2) is False:
            return False
    except AttributeError:
        return None

    # get the overlapping area
    clip = rect1.clip(rect2)

    # find where clip's top-left point is in both rectangles
    x1 = clip.left - rect1.left
    y1 = clip.top - rect1.top
    x2 = clip.left - rect2.left
    y2 = clip.top - rect2.top

    # cycle through clip's area of the hitmasks
    for x in range(clip.width):
        for y in range(clip.height):
            # returns True if neither pixel is blank
            if mask1[x1 + x][y1 + y] is not blank1 and \
                    mask2[x2 + x][y2 + y] is not blank2:
                return True

    # if there was neither collision nor error
    return False


def wrap_position(position: Vector2, surface: Surface):
    w, h = surface.get_size()
    return Vector2(position.x % w, position.y % h)


def get_random_position(surface: Surface):
    return Vector2(random.randrange(surface.get_width()), random.randrange(surface.get_height()))


def get_random_velocity(min_speed: int, max_speed: int):
    speed = random.randint(min_speed, max_speed) * random.random()
    angle = random.randrange(0, 360)
    return Vector2(speed, 0).rotate(angle)


def get_random_rotation(min_rotation: int, max_rotation):
    r = random.randint(min_rotation, max_rotation) * random.random() * random.choice([1, -1])
    return r


def collides_with(obj: Geometry, other_obj: Geometry) -> bool:
    distance = obj.position.distance_to(other_obj.position)
    return distance < obj.radius + other_obj.radius
