import random
from typing import Optional

from components.hexagonalgrid import Biome, HexTile, HexPosition, HexSides


class TileManager:
    def __init__(self, preview_length: int, remaining_tiles: int) -> None:
        self.remaining = remaining_tiles
        self.active = None
        self.held = None

        self.preview_length = preview_length
        self.preview = [pick_random_edges() for i in range(self.preview_length)]
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

        return HexTile(hex_position, self.active)

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
            self.preview.append(pick_random_edges())
        else:
            self.preview.append(None)

    def add_to_remaining(self, amount: int) -> None:
        update_preview = self.remaining < self.preview_length
        self.remaining += abs(amount)

        if not update_preview:
            return

        for i in range(self.preview_length):
            if self.preview[i] is None and self.remaining - i + 1 > 0:
                self.preview[i] = pick_random_edges()


# TODO: Make more balanced random piece system
def pick_random_edges() -> HexSides:
    return [random.choice(tuple(Biome)) for i in range(6)]
