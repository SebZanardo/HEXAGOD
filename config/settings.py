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

CAPTION = "HEXAGOD"
FPS = 60


action_mappings = {
    Action.HOLD: [pygame.K_f],
    Action.RESTART: [pygame.K_r],
    Action.CENTRE: [pygame.K_c],
    Action.MUTE: [pygame.K_m],
}
