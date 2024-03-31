import math
from dataclasses import dataclass
from enum import Enum, auto
import pygame

# This script uses flat-top oriented hexagons and a cube coordinate system
# https://www.redblobgames.com/grids/hexagons/


SIZE = 32
WIDTH = 2 * SIZE
HEIGHT = math.sqrt(3) * SIZE
HORIZ = 3 / 4 * WIDTH
VERT = HEIGHT


class Biome(Enum):
    WATER = auto()
    GRASS = auto()
    SAND = auto()
    FOREST = auto()
    MOUNTAIN = auto()
    SNOW = auto()


@dataclass(frozen=True)
class HexPosition:
    q: int
    r: int
    s: int


@dataclass
class HexTile:
    position: HexPosition
    edges: list[int]


class HexagonalGrid:
    def __init__(self) -> None:
        self.grid = {}
        # Store open grid cells

    def add_tile(self, hex: HexTile):
        self.grid[hex.position] = hex


def hex_corner(cx: float, cy: float, i: int) -> tuple[float, float]:
    angle_deg = 60 * i
    angle_rad = math.pi / 180 * angle_deg
    return (cx + SIZE * math.cos(angle_rad), cy + SIZE * math.sin(angle_rad))


def hex_to_pixel(hex: HexPosition) -> tuple[float, float]:
    x = SIZE * (3 / 2 * hex.q)
    y = SIZE * (math.sqrt(3) / 2 * hex.q + math.sqrt(3) * hex.r)
    return (x, y)


def pixel_to_hex(x: int, y: int) -> HexPosition:
    q = (2 / 3 * x) / SIZE
    r = (-1 / 3 * x + math.sqrt(3) / 3 * y) / SIZE
    s = -q - r
    return HexPosition(q, r, s)


def round_to_nearest_hex(hex: HexPosition) -> HexPosition:
    q = round(hex.q)
    r = round(hex.r)
    s = round(hex.s)

    q_diff = abs(q - hex.q)
    r_diff = abs(r - hex.r)
    s_diff = abs(s - hex.s)

    if q_diff > r_diff and q_diff > s_diff:
        q = -r - s
    elif r_diff > s_diff:
        r = -q - s
    else:
        s = -q - r

    return HexPosition(q, r, s)


def render_hex(
    surface: pygame.Surface, hex: HexTile, offset_x: float, offset_y: float
) -> None:
    centre = hex_to_pixel(hex.position)

    corners = []

    for c in range(6):
        x, y = hex_corner(*centre, c)
        x += offset_x
        y += offset_y
        corners.append((x, y))

    pygame.draw.polygon(surface, (0, 255, 0), corners)
    for c in range(6):
        pygame.draw.line(surface, (0, 150, 0), corners[c - 1], corners[c], 2)
    for c in range(6):
        pygame.draw.circle(surface, (0, 0, 0), corners[c], 2)
