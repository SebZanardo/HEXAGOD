import pygame

from components.animationplayer import AnimationPlayer
from components.camera import Camera
from utilities.math import clamp


def render_to(
    surface: pygame.Surface, font: pygame.font.Font, text: str, dest, colour
) -> None:
    text_render = font.render(text, False, colour)
    surface.blit(text_render, dest)


def render_centered_text(
    surface: pygame.Surface, font: pygame.font.Font, text: str, dest, colour
):
    text_render = font.render(text, False, colour)
    text_rect = text_render.get_rect()
    text_rect.center = dest

    surface.blit(text_render, text_rect)


class PopupText:
    def __init__(
        self,
        x: float,
        y: float,
        font: pygame.font.Font,
        text: str,
        colour,
        duration: float,
    ) -> None:
        self.x = x
        self.y = y

        frames = []
        length = int(duration / 0.05)
        for i in range(length):
            frame = font.render(text, False, colour)
            frame.set_alpha(clamp(i * (1000 / length), 0, 255))

            frames.append(frame)
        frames.reverse()

        rect = frames[0].get_rect()
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
        surface.blit(self.animator.get_frame(), screen_pos)
