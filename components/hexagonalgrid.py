from __future__ import annotations
from typing import Optional
import math
from enum import Enum, auto
from dataclasses import dataclass, astuple
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


@dataclass
class HexPosition:
    q: int
    r: int
    s: int

    def __add__(self, other: HexPosition) -> HexPosition:
        return HexPosition(self.q + other.q, self.r + other.r, self.s + other.s)


@dataclass
class HexTile:
    position: HexPosition
    edges: list[int]


HEXAGONAL_NEIGHBOURS = (
    HexPosition(0, -1, +1),
    HexPosition(+1, -1, 0),
    HexPosition(+1, 0, -1),
    HexPosition(0, +1, -1),
    HexPosition(-1, +1, 0),
    HexPosition(-1, 0, +1),
)


class HexagonalGrid:
    def __init__(self) -> None:
        self.grid = {}
        self.open = set()

    def write_tile(self, hex: HexTile) -> None:
        self.grid[astuple(hex.position)] = hex

    def get_tile(self, hex_position: HexPosition) -> Optional[HexTile]:
        return self.grid.get(astuple(hex_position))

    def add_tile(self, hex: HexTile) -> None:
        self.write_tile(hex)

        self.open.discard(astuple(hex.position))

        for neighbour in HEXAGONAL_NEIGHBOURS:
            adj_hex_position = hex.position + neighbour
            self.open.add(astuple(adj_hex_position))

    def get_placed_tiles(self) -> list[HexTile]:
        return self.grid.values()

    def get_open_tiles(self) -> list[HexTile]:
        return self.open

    def is_open(self, hex_position: HexPosition) -> bool:
        return astuple(hex_position) in self.open


def hex_corner(cx: float, cy: float, i: int) -> tuple[float, float]:
    angle_deg = 60 * i
    angle_rad = math.pi / 180 * angle_deg
    return (cx + SIZE * math.cos(angle_rad), cy + SIZE * math.sin(angle_rad))


def get_screen_hex_corners(
    cx: float, cy: float, offset_x: float, offset_y: float
) -> list[tuple[float, float]]:
    corners = []
    for i in range(6):
        x, y = hex_corner(cx, cy, i)
        x += offset_x
        y += offset_y
        corners.append((x, y))
    return corners


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
    corners = get_screen_hex_corners(*centre, offset_x, offset_y)

    pygame.draw.polygon(surface, (0, 255, 0), corners)

    for i in range(6):
        pygame.draw.line(surface, (0, 150, 0), corners[i - 1], corners[i], 2)
    for i in range(6):
        pygame.draw.circle(surface, (0, 0, 0), corners[i], 2)


def render_open_hex(
    surface: pygame.Surface, hex_position: HexPosition, offset_x: float, offset_y: float
) -> None:
    centre = hex_to_pixel(hex_position)
    corners = get_screen_hex_corners(*centre, offset_x, offset_y)

    pygame.draw.polygon(surface, (100, 200, 200), corners)
