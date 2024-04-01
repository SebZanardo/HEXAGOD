from utilities.math import clamp, PYTHAGORAS_CONSTANT


class Camera:
    def __init__(
        self,
        x: float,
        y: float,
        offset_x: int,
        offset_y: int,
        initial_zoom: float,
        zoom_minimum: int,
        zoom_maximum: int,
        move_speed: float,
        zoom_speed: float,
    ) -> None:
        self.x = x
        self.y = y
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.zoom = clamp(initial_zoom, zoom_minimum, zoom_maximum)
        self.zoom_int = int(self.zoom)
        self.zoom_minimum = zoom_minimum
        self.zoom_maximum = zoom_maximum
        self.move_speed = move_speed
        self.zoom_speed = zoom_speed

    def move(self, dt: float, dx: int, dy: int) -> None:
        # Normalise diagonal movement
        if dx != 0 and dy != 0:
            dx /= PYTHAGORAS_CONSTANT
            dy /= PYTHAGORAS_CONSTANT

        self.x += dx * self.move_speed / self.zoom * dt
        self.y += dy * self.move_speed / self.zoom * dt

    def change_zoom(self, dt: float, d: int) -> None:
        self.zoom = clamp(
            self.zoom + d * self.zoom_speed * dt, self.zoom_minimum, self.zoom_maximum
        )
        self.zoom_int = int(self.zoom)

    def world_to_screen(self, x: float, y: float) -> tuple[int, int]:
        return (
            int((x - self.x) * self.zoom + self.offset_x),
            int((y - self.y) * self.zoom + self.offset_y),
        )

    def screen_to_world(self, x: float, y: float) -> tuple[float, float]:
        return (
            (x - self.offset_x) / self.zoom + self.x,
            (y - self.offset_y) / self.zoom + self.y,
        )
