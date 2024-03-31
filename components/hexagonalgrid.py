from __future__ import annotations
from typing import Optional
import math
from enum import Enum, auto
from dataclasses import dataclass, astuple
import pygame

from components.camera import Camera


# This script uses flat-top oriented hexagons and a cube coordinate system
# https://www.redblobgames.com/grids/hexagons/


MIN_SIZE = 8
MAX_SIZE = 64
SIZE = 32
WIDTH = 2 * SIZE
HEIGHT = math.sqrt(3) * SIZE


class Biome(Enum):
    WATER = auto()
    GRASS = auto()
    SAND = auto()
    FOREST = auto()
    MOUNTAIN = auto()
    SNOW = auto()


BIOME_COLOUR_MAP = {
    Biome.WATER: (83, 216, 251),
    Biome.GRASS: (87, 167, 115),
    Biome.SAND: (255, 225, 86),
    Biome.FOREST: (11, 83, 81),
    Biome.MOUNTAIN: (99, 89, 92),
    Biome.SNOW: (208, 229, 227),
}


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
        self.open.discard(astuple(hex.position))

        self.write_tile(hex)

        for neighbour in HEXAGONAL_NEIGHBOURS:
            adj_hex_position = hex.position + neighbour
            if astuple(adj_hex_position) not in self.grid:
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


def get_hex_corners(cx: float, cy: float) -> list[tuple[float, float]]:
    return [hex_corner(cx, cy, i) for i in range(6)]


def hex_to_world(hex: HexPosition) -> tuple[float, float]:
    x = SIZE * (3 / 2 * hex.q)
    y = SIZE * (math.sqrt(3) / 2 * hex.q + math.sqrt(3) * hex.r)
    return (x, y)


def world_to_hex(x: int, y: int) -> HexPosition:
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


def render_hex(surface: pygame.Surface, camera: Camera, hex: HexTile) -> None:
    centre = camera.world_to_screen(*hex_to_world(hex.position))
    corners = get_hex_corners(*centre)

    for i in range(6):
        colour = BIOME_COLOUR_MAP[hex.edges[i]]
        sector = [corners[i - 1], corners[i], centre]
        pygame.draw.polygon(surface, colour, sector)

    for i in range(6):
        pygame.draw.line(surface, (0, 0, 0), corners[i - 1], corners[i], SIZE // 8)

    for i in range(6):
        pygame.draw.circle(surface, (0, 0, 0), corners[i], SIZE // 8)


def render_open_hex(
    surface: pygame.Surface, camera: Camera, hex_position: HexPosition
) -> None:
    centre = camera.world_to_screen(*hex_to_world(hex_position))
    corners = get_hex_corners(*centre)

    pygame.draw.polygon(surface, (102, 195, 255), corners)


def render_highlighted_hex(
    surface: pygame.Surface, camera: Camera, hex_position: HexPosition
) -> None:
    centre = camera.world_to_screen(*hex_to_world(hex_position))
    corners = get_hex_corners(*centre)

    pygame.draw.polygon(surface, (255, 255, 255), corners, SIZE // 8)


# HACK: Before I implement zooming properly (also broken)
def zoom_in() -> None:
    global SIZE, WIDTH, HEIGHT
    SIZE = max(MIN_SIZE, SIZE - 1)
    WIDTH = 2 * SIZE
    HEIGHT = math.sqrt(3) * SIZE


# HACK: Before I implement zooming properly (also broken)
def zoom_out() -> None:
    global SIZE, WIDTH, HEIGHT
    SIZE = min(MAX_SIZE, SIZE + 1)
    WIDTH = 2 * SIZE
    HEIGHT = math.sqrt(3) * SIZE
