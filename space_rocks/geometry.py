from pygame.math import Vector2


class Geometry:
    def __init__(self, position: Vector2, radius: float, velocity: Vector2) -> None:
        self._velocity: Vector2 = velocity
        self._position: Vector2 = position
        self._radius: float = radius

    @property
    def velocity(self):
        return self._velocity

    @property
    def position(self):
        return self._position

    @property
    def radius(self):
        return self._radius

    def update_pos(self, position: Vector2):
        return Geometry(position, self.radius, self.velocity)

    def update_vel(self, velocity: Vector2):
        return Geometry(self.position, self.radius, velocity)
