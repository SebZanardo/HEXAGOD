class Camera:
    def __init__(self, x: float, y: float, offset_x: int, offset_y: int) -> None:
        self.x = x
        self.y = y
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.zoom = 1  # TODO: Implement zooming properly

    def move(self, vx: float, vy: float) -> None:
        self.x += vx
        self.y += vy

    def world_to_screen(self, x: float, y: float) -> tuple[float, float]:
        return (
            (x - self.x) * self.zoom + self.offset_x,
            (y - self.y) * self.zoom + self.offset_y,
        )

    def screen_to_world(self, x: float, y: float) -> tuple[float, float]:
        return (
            (x - self.offset_x) / self.zoom + self.x,
            (y - self.offset_y) / self.zoom + self.y,
        )
