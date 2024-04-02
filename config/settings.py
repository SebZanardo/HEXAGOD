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
    Action.LEFT: [pygame.K_a, pygame.K_LEFT],
    Action.RIGHT: [pygame.K_d, pygame.K_RIGHT],
    Action.UP: [pygame.K_w, pygame.K_UP],
    Action.DOWN: [pygame.K_s, pygame.K_DOWN],
    Action.ZOOM_IN: [pygame.K_z, pygame.K_SLASH, pygame.K_q],
    Action.ZOOM_OUT: [pygame.K_x, pygame.K_PERIOD, pygame.K_e],
    Action.HOLD: [pygame.K_c, pygame.K_COMMA, pygame.K_f],
    Action.SELECT: [pygame.K_LSHIFT, pygame.K_RSHIFT],
    Action.START: [pygame.K_RETURN, pygame.K_SPACE],
}
