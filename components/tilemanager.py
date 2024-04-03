import random
from typing import Optional

from components.hexagonalgrid import Biome, HexTile, HexPosition, HexSides


STARTING_BIOME = Biome.GRASS


class TileManager:
    def __init__(self, preview_length: int, remaining_tiles: int) -> None:
        self.remaining = remaining_tiles
        self.active = None
        self.held = None

        self.preview_length = preview_length
        self.preview = [pick_random_starting_tile() for i in range(self.preview_length)]
        self.get_next_tile()

    def get_remaining(self) -> int:
        return self.remaining

    def get_active(self) -> Optional[HexSides]:
        return self.active

    def get_held(self) -> Optional[HexSides]:
        return self.held

    def get_preview(self) -> list[Optional[HexSides]]:
        return self.preview

    def create_active_tile(self, hex_position: HexPosition) -> Optional[HexTile]:
        if self.active is None:
            return None

        return HexTile(hex_position, self.active, [None] * 6)

    def swap_held_tile(self) -> None:
        if self.held is not None:
            temp = self.active
            self.active = self.held
            self.held = temp
        else:
            self.held = self.active
            self.get_next_tile()

    def get_next_tile(self) -> None:
        if self.remaining == 0:
            self.active = self.held
            self.held = None
            return

        self.active = self.preview.pop(0)
        self.remaining -= 1

        if self.remaining >= self.preview_length:
            self.preview.append(pick_random_tile())
        else:
            self.preview.append(None)

    def add_to_remaining(self, amount: int) -> None:
        update_preview = self.remaining < self.preview_length
        self.remaining += abs(amount)

        if not update_preview:
            return

        for i in range(self.preview_length):
            if self.preview[i] is None and self.remaining - i > 0:
                self.preview[i] = pick_random_tile()

    def rotate_active_tile(self) -> None:
        last = self.active.pop()
        self.active.insert(0, last)


# Probability for number of unique biomes on a tile
UNIQUE_BIOME_PROBABILITY = [0.1, 0.6, 0.2, 0.05, 0.03, 0.02]


def pick_random_tile() -> HexSides:
    unique_biomes = pick_number_of_unique_biomes()
    picked_biomes = pick_unique_biomes(unique_biomes)
    return random_tile(picked_biomes)


# Ensures that starting biome is picked
def pick_random_starting_tile() -> HexSides:
    unique_biomes = pick_number_of_unique_biomes()
    picked_biomes = [STARTING_BIOME] + pick_unique_biomes(unique_biomes - 1)
    return random_tile(picked_biomes)


def random_tile(picked_biomes: list[Biome]) -> HexSides:
    sides = [None] * 6
    open = [i for i in range(6)]
    random.shuffle(open)

    # Ensure every unique biome is picked once
    for b in picked_biomes:
        sides[open.pop()] = b

    while open:
        sides[open.pop()] = random.choice(picked_biomes)

    return sides


def pick_number_of_unique_biomes() -> int:
    r = random.random()
    for i, p in enumerate(UNIQUE_BIOME_PROBABILITY):
        if r <= p:
            return i + 1
        r -= p
    return 1  # Should never be hit


def pick_unique_biomes(n: int) -> list[Biome]:
    available = list(Biome)
    random.shuffle(available)
    return available[: min(len(available), abs(n))]
