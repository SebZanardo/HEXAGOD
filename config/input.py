from enum import Enum, auto


class InputState(Enum):
    PRESSED = auto()
    HELD = auto()
    RELEASED = auto()


class MouseButton(Enum):
    LEFT = 0
    MIDDLE = 1
    RIGHT = 2


class Action(Enum):
    LEFT = auto()
    RIGHT = auto()
    UP = auto()
    DOWN = auto()
    ZOOM_IN = auto()
    ZOOM_OUT = auto()
    HOLD = auto()
    SELECT = auto()
    START = auto()
