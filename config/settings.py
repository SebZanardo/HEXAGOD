import pygame

from config.input import Action


WINDOW_WIDTH = 640
WINDOW_HEIGHT = 360
WINDOW_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)
WINDOW_CENTRE = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)

WINDOW_SETUP = {
    "size": WINDOW_SIZE,
    "flags": pygame.SCALED | pygame.RESIZABLE,
    "depth": 0,
    "display": 0,
    "vsync": 1,
}

CAPTION = "Pygame Community Spring Jam 2024"
FPS = 60


action_mappings = {
    Action.HOLD: [pygame.K_f],
    Action.UNDO: [pygame.K_x],
    Action.SELECT: [pygame.K_LSHIFT, pygame.K_RSHIFT],
    Action.START: [pygame.K_RETURN, pygame.K_SPACE],
    Action.BACK: [pygame.K_ESCAPE],
}
