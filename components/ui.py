import pygame
import pygame.freetype

from components.animationplayer import AnimationPlayer
from components.camera import Camera


def render_centered_text(
    surface: pygame.Surface, font: pygame.freetype.Font, text: str, dest
):
    text_rect = font.get_rect(text)
    text_rect.center = dest
    font.render_to(surface, text_rect, text)


class PopupText:
    def __init__(
        self, x: float, y: float, font: pygame.freetype.Font, text: str, duration: float
    ) -> None:
        self.x = x
        self.y = y

        frames = []
        length = int(duration / 0.05)
        for i in range(length):
            frames.append(
                font.render(
                    text,
                    (
                        font.fgcolor[0],
                        font.fgcolor[1],
                        font.fgcolor[2],
                        i * (255 / length),
                    ),
                )
            )
        frames.reverse()

        rect = frames[0][1]
        self.offset_x = rect.w // 2
        self.offset_y = rect.h // 2

        self.animator = AnimationPlayer("fade", frames, duration / length, False)

    def move(self, new_x: float, new_y: float) -> None:
        self.x = new_x
        self.y = new_y
        self.animator.reset()

    def update(self, dt: float) -> None:
        self.animator.update(dt)
        self.y -= 10 * dt

    def render(self, surface: pygame.Surface, camera: Camera) -> None:
        screen_pos = camera.world_to_screen(self.x, self.y)
        screen_pos = (screen_pos[0] - self.offset_x, screen_pos[1] - self.offset_y)
        surface.blit(self.animator.get_frame()[0], screen_pos)
