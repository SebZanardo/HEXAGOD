MAX_MOVE_SPEED = 200


class Camera:
    def __init__(self, x: float, y: float, offset_x: int, offset_y: int) -> None:
        self.x = x
        self.y = y
        self.offset_x = offset_x
        self.offset_y = offset_y

    def move(self, dt: float, dx: int, dy: int) -> None:
        self.x += dx * MAX_MOVE_SPEED * dt
        self.y += dy * MAX_MOVE_SPEED * dt

    def world_to_screen(self, x: float, y: float) -> tuple[int, int]:
        return int(x - self.x + self.offset_x), int(y - self.y + self.offset_y)

    def screen_to_world(self, x: float, y: float) -> tuple[float, float]:
        return x - self.offset_x + self.x, y - self.offset_y + self.y
