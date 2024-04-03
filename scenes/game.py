import math
import pygame

from utilities.typehints import ActionBuffer, MouseBuffer
from config.input import InputState, MouseButton, Action
from baseclasses.scenemanager import Scene, SceneManager
import scenes.mainmenu
from config.settings import WINDOW_CENTRE, WINDOW_WIDTH, WINDOW_HEIGHT
from components.hexagonalgrid import (
    WIDTH,
    HEIGHT,
    HEXAGONAL_NEIGHBOURS,
    HexPosition,
    HexTile,
    HexagonalGrid,
    world_to_hex,
    round_to_nearest_hex,
    render_hex,
    render_open_hex,
    render_highlighted_hex,
    render_preview_hex,
)
from components.tilemanager import TileManager, STARTING_BIOME
from components.camera import Camera
from components.ui import render_centered_text


PREVIEW_OFFSET = HEIGHT * 1.5
PREVIEW_X = WINDOW_WIDTH - 40
PREVIEW_Y = 20

HELD_X = 40
HELD_Y = WINDOW_CENTRE[1]

MOVE_X = WINDOW_CENTRE[0] - PREVIEW_OFFSET
MOVE_Y = WINDOW_CENTRE[1] - 20

VIEWPORT_RECT = (
    WINDOW_CENTRE[0] - MOVE_X,
    WINDOW_CENTRE[1] - MOVE_Y,
    MOVE_X * 2,
    MOVE_Y * 2,
)


class Game(Scene):
    def __init__(self, scene_manager: SceneManager) -> None:
        super().__init__(scene_manager)
        self.font = pygame.freetype.Font("assets/joystix.otf", 10)
        self.font.antialiased = False

        self.hex_grid = HexagonalGrid()
        self.hex_grid.add_tile(
            HexTile(HexPosition(0, 0, 0), [STARTING_BIOME] * 6, [None] * 6)
        )
        self.tile_manager = TileManager(3, 50)

        self.camera = Camera(0, 0, *WINDOW_CENTRE)

        self.hovered_tile = HexPosition(0, 0, 0)

        self.score = 0

    def handle_input(
        self, action_buffer: ActionBuffer, mouse_buffer: MouseBuffer
    ) -> None:
        if action_buffer[Action.BACK][InputState.PRESSED]:
            self.scene_manager.switch_scene(scenes.mainmenu.MainMenu)

        self.input_x, self.input_y = 0, 0
        mx, my = pygame.mouse.get_pos()
        dx = WINDOW_CENTRE[0] - mx
        dy = WINDOW_CENTRE[1] - my
        d = math.sqrt(dx**2 + dy**2)

        if abs(dx) > MOVE_X or abs(dy) > MOVE_Y:
            self.input_x = -dx / d
            self.input_y = -dy / d
        else:
            offset_mouse_position = self.camera.screen_to_world(mx, my)
            hex = world_to_hex(*offset_mouse_position)
            self.hovered_tile = round_to_nearest_hex(hex)

        self.hold = action_buffer[Action.HOLD][InputState.PRESSED]
        self.rotate = mouse_buffer[MouseButton.RIGHT][InputState.PRESSED]
        self.try_place = mouse_buffer[MouseButton.LEFT][InputState.PRESSED]

    def update(self, dt: float) -> None:
        self.camera.move(dt, self.input_x, self.input_y)

        if self.hold:
            self.tile_manager.swap_held_tile()

        if self.rotate:
            self.tile_manager.rotate_active_tile()

        if self.try_place and self.hex_grid.is_open(self.hovered_tile):
            tile = self.tile_manager.create_active_tile(self.hovered_tile)
            if tile is not None:
                self.hex_grid.add_tile(tile)

                # Scoring
                for i, neighbour in enumerate(HEXAGONAL_NEIGHBOURS):
                    position = self.hovered_tile + neighbour
                    adj_tile = self.hex_grid.get_tile(position)

                    if adj_tile is None:
                        continue

                    # If same biomes are touching
                    tile.sides_touching[i] = adj_tile.sides[(i + 3) % 6]
                    adj_tile.sides_touching[(i + 3) % 6] = tile.sides[i]
                    if tile.sides[i] == adj_tile.sides[(i + 3) % 6]:
                        self.score += 10
                        tile.matching_sides += 1
                        adj_tile.matching_sides += 1

                        if tile.matching_sides == 6:
                            self.score += 100
                            self.tile_manager.add_to_remaining(3)
                        if adj_tile.matching_sides == 6:
                            self.score += 100
                            self.tile_manager.add_to_remaining(3)

                self.tile_manager.get_next_tile()

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((83, 216, 251))

        for hex_position_tuple in self.hex_grid.get_open_tiles():
            render_open_hex(surface, self.camera, HexPosition(*hex_position_tuple))

        active_tile = self.tile_manager.create_active_tile(self.hovered_tile)
        if active_tile is not None:
            render_hex(surface, self.camera, active_tile)

        for hex in self.hex_grid.get_placed_tiles():
            render_hex(surface, self.camera, hex)

        matching_sides = [False] * 6
        if (
            self.hex_grid.is_open(self.hovered_tile)
            and self.tile_manager.get_active() is not None
        ):
            for i, neighbour in enumerate(HEXAGONAL_NEIGHBOURS):
                position = self.hovered_tile + neighbour
                adj_tile = self.hex_grid.get_tile(position)

                if adj_tile is None:
                    continue

                # If same biomes are touching
                if self.tile_manager.get_active()[i] == adj_tile.sides[(i + 3) % 6]:
                    matching_sides[i] = True

        render_highlighted_hex(surface, self.camera, self.hovered_tile, matching_sides)

        pygame.draw.rect(surface, (200, 200, 200), VIEWPORT_RECT, 8)
        pygame.draw.rect(
            surface,
            (255, 255, 255),
            ((0, 0), (WINDOW_WIDTH, WINDOW_CENTRE[1] - MOVE_Y)),
        )
        pygame.draw.rect(
            surface,
            (255, 255, 255),
            ((0, 0), (WINDOW_CENTRE[0] - MOVE_X, WINDOW_HEIGHT)),
        )
        pygame.draw.rect(
            surface,
            (255, 255, 255),
            (
                (WINDOW_CENTRE[0] + MOVE_X, 0),
                (WINDOW_CENTRE[0] - MOVE_X, WINDOW_HEIGHT),
            ),
        )
        pygame.draw.rect(
            surface,
            (255, 255, 255),
            ((0, WINDOW_CENTRE[1] + MOVE_Y), (WINDOW_WIDTH, WINDOW_CENTRE[1] - MOVE_Y)),
        )

        for i, preview in enumerate(self.tile_manager.get_preview()):
            if preview is None:
                break
            render_preview_hex(surface, PREVIEW_X, (i + 1) * PREVIEW_OFFSET, preview)

        held_tile = self.tile_manager.get_held()
        if held_tile is not None:
            render_preview_hex(surface, HELD_X, HELD_Y, held_tile)

        render_centered_text(
            surface,
            self.font,
            f"{self.tile_manager.get_remaining()}",
            (PREVIEW_X, PREVIEW_Y),
        )

        render_centered_text(
            surface,
            self.font,
            f"{self.hovered_tile}",
            (WINDOW_CENTRE[0], WINDOW_HEIGHT - 10),
        )
        render_centered_text(
            surface, self.font, f"{self.score}", (WINDOW_CENTRE[0], 10)
        )
