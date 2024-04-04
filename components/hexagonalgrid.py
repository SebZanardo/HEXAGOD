from __future__ import annotations
from typing import Optional
import math
from enum import Enum, auto
from dataclasses import dataclass, astuple
import random
import pygame

from components.camera import Camera


# This script uses flat-top oriented hexagons and a cube coordinate system
# https://www.redblobgames.com/grids/hexagons/


SIZE = 24
WIDTH = 2 * SIZE
HEIGHT = math.sqrt(3) * SIZE

OUTLINE_WIDTH = 2

RENDER_OFFSETS_EVEN = ((0, -6), (-5, 1), (5, 1))
RENDER_OFFSETS_ODD = ((0, 4), (-5, -2), (5, -2))


class Biome(Enum):
    SWAMP = auto()
    GRASS = auto()
    SAND = auto()
    FOREST = auto()
    MOUNTAIN = auto()
    SNOW = auto()


BIOME_COLOUR_MAP = {
    Biome.SWAMP: (191, 148, 228),
    Biome.GRASS: (87, 167, 115),
    Biome.SAND: (255, 225, 86),
    Biome.FOREST: (11, 83, 81),
    Biome.MOUNTAIN: (99, 89, 92),
    Biome.SNOW: (208, 229, 227),
}

DARK = 25
BIOME_FAILED_COLOUR_MAP = {
    Biome.SWAMP: (191 - DARK, 148 - DARK, 228 - DARK),
    Biome.GRASS: (87 - DARK, 167 - DARK, 115 - DARK),
    Biome.SAND: (255 - DARK, 225 - DARK, 86 - DARK),
    Biome.FOREST: (0, 83 - DARK, 81 - DARK),
    Biome.MOUNTAIN: (99 - DARK, 89 - DARK, 92 - DARK),
    Biome.SNOW: (208 - DARK, 229 - DARK, 227 - DARK),
}


OUTLINE_COLOUR = (50, 30, 50)
HOVER_COLOUR = (255, 255, 255)
HIGHLIGHT_COLOUR = (255, 255, 0)
OPEN_COLOUR = (20, 150, 170)


class SideStates(Enum):
    UNKNOWN = auto()
    MATCH = auto()
    MISSMATCH = auto()


HexSides = tuple[
    Optional[Biome],
    Optional[Biome],
    Optional[Biome],
    Optional[Biome],
    Optional[Biome],
    Optional[Biome],
]


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
    sides: HexSides
    sides_touching: HexSides
    sector_sprites: Optional[list[tuple[int]]]
    matching_sides: int = 0
    can_be_perfect: bool = True


HEXAGONAL_NEIGHBOURS = (
    HexPosition(+1, -1, 0),
    HexPosition(+1, 0, -1),
    HexPosition(0, +1, -1),
    HexPosition(-1, +1, 0),
    HexPosition(-1, 0, +1),
    HexPosition(0, -1, +1),
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
        return list(self.grid.values())

    def get_open_tiles(self) -> list[HexTile]:
        return self.open

    def is_open(self, hex_position: HexPosition) -> bool:
        return astuple(hex_position) in self.open


def hex_corner(cx: float, cy: float, i: int, size: float = SIZE) -> tuple[float, float]:
    angle_deg = 60 * i
    angle_rad = math.pi / 180 * angle_deg
    return (cx + size * math.cos(angle_rad), cy + size * math.sin(angle_rad))


def get_hex_corners(
    cx: float, cy: float, size: float = SIZE
) -> list[tuple[float, float]]:
    return [hex_corner(cx, cy, i, size) for i in range(6)]


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


def render_hex(
    surface: pygame.Surface,
    camera: Camera,
    hex: HexTile,
    hex_sprites: list[pygame.Surface],
) -> None:
    centre = hex_to_world(hex.position)
    corners = get_hex_corners(*centre)
    screen_centre = camera.world_to_screen(*centre)
    screen_corners = [camera.world_to_screen(*c) for c in corners]

    for i in range(6):
        colour = (
            BIOME_COLOUR_MAP[hex.sides[i]]
            if hex.can_be_perfect
            else BIOME_FAILED_COLOUR_MAP[hex.sides[i]]
        )
        sector = [screen_corners[i - 1], screen_corners[i], screen_centre]
        pygame.draw.polygon(surface, colour, sector)

        if hex.sector_sprites is None:
            continue

        middle_x, middle_y = 0, 0
        for p in sector:
            middle_x += p[0]
            middle_y += p[1]
        middle_x /= len(sector)
        middle_y /= len(sector)

        for p in range(3):
            if hex.sector_sprites[i][p] is None:
                continue
            offset = RENDER_OFFSETS_EVEN[p] if i % 2 == 0 else RENDER_OFFSETS_ODD[p]
            surface.blit(
                hex_sprites[hex.sector_sprites[i][p]],
                (middle_x - 4 + offset[0], middle_y - 4 + offset[1]),
            )

    for i in range(6):
        if hex.sides_touching[i] is not None:
            continue
        pygame.draw.line(
            surface,
            OUTLINE_COLOUR,
            screen_corners[i - 1],
            screen_corners[i],
            OUTLINE_WIDTH,
        )

    # for i in range(6):
    #     pygame.draw.circle(surface, OUTLINE_COLOUR, screen_corners[i], 1)


def render_open_hex(
    surface: pygame.Surface, camera: Camera, hex_position: HexPosition
) -> None:
    centre = hex_to_world(hex_position)
    corners = get_hex_corners(*centre)
    screen_corners = [camera.world_to_screen(*c) for c in corners]

    pygame.draw.polygon(surface, OPEN_COLOUR, screen_corners)


def render_highlighted_hex(
    surface: pygame.Surface,
    camera: Camera,
    hex_position: HexPosition,
    sides: list[SideStates],
) -> None:
    centre = hex_to_world(hex_position)
    corners = get_hex_corners(*centre)
    screen_corners = [camera.world_to_screen(*c) for c in corners]

    for i in range(6):
        if sides[i] == SideStates.MISSMATCH:
            continue
        colour = HIGHLIGHT_COLOUR if sides[i] == SideStates.MATCH else HOVER_COLOUR
        pygame.draw.line(
            surface, colour, screen_corners[i - 1], screen_corners[i], OUTLINE_WIDTH
        )


def render_preview_hex(
    surface: pygame.Surface, cx: int, cy: int, sides: HexSides
) -> None:
    screen_corners = get_hex_corners(cx, cy)

    for i in range(6):
        colour = BIOME_COLOUR_MAP[sides[i]]
        sector = [screen_corners[i - 1], screen_corners[i], (cx, cy)]
        pygame.draw.polygon(surface, colour, sector)

    pygame.draw.polygon(surface, OUTLINE_COLOUR, screen_corners, OUTLINE_WIDTH)


def generate_hex_art(
    hex_sides: HexSides, biome_sprite_map: dict[Biome, list[int]]
) -> list[list[Optional[int]]]:
    # Generate art for placed tile
    sector_sprites = []
    for biome in hex_sides:
        count = random.randint(1, 3)
        sprites = [None] * 3
        spots = [0, 1, 2]
        random.shuffle(spots)
        for i in range(count):
            spot = spots.pop()
            sprites[spot] = random.choice(biome_sprite_map[biome])
        sector_sprites.append(sprites)
    return sector_sprites
