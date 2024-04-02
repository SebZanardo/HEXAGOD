import pygame
import pygame.freetype


def render_centered_text(
    surface: pygame.Surface, font: pygame.freetype.Font, text: str, dest
):
    text_rect = font.get_rect(text)
    text_rect.center = dest
    font.render_to(surface, text_rect, text)
