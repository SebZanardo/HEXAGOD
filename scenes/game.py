import pygame

from utilities.typehints import ActionBuffer, MouseBuffer
from config.input import InputState, MouseButton, Action
from baseclasses.scenemanager import Scene, SceneManager
import scenes.mainmenu
from config.settings import WINDOW_CENTRE, WINDOW_WIDTH, WINDOW_HEIGHT
from components.hexagonalgrid import (
    SIZE,
    PREVIEW_MULTIPLIER,
    Biome,
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
from components.tilemanager import TileManager
from components.camera import Camera
from components.ui import render_centered_text


PREVIEW_OFFSET = SIZE * PREVIEW_MULTIPLIER * 2 + SIZE
PREVIEW_X = WINDOW_WIDTH - PREVIEW_OFFSET
PREVIEW_Y = 20
HELD_X = PREVIEW_OFFSET
HELD_Y = WINDOW_HEIGHT - PREVIEW_OFFSET


class Game(Scene):
    def __init__(self, scene_manager: SceneManager) -> None:
        super().__init__(scene_manager)
        self.font = pygame.freetype.Font("assets/joystix.otf", 10)
        self.font.antialiased = False

        self.hex_grid = HexagonalGrid()
        self.hex_grid.add_tile(HexTile(HexPosition(0, 0, 0), [Biome.GRASS] * 6))
        self.tile_manager = TileManager(5, 50)

        self.camera = Camera(0, 0, *WINDOW_CENTRE, 4, *(1, 16), 200, 10)

        self.hovered_tile = HexPosition(0, 0, 0)

    def handle_input(
        self, action_buffer: ActionBuffer, mouse_buffer: MouseBuffer
    ) -> None:
        if action_buffer[Action.START][InputState.PRESSED]:
            self.scene_manager.switch_scene(scenes.mainmenu.MainMenu)

        self.zoom_input = 0
        if action_buffer[Action.ZOOM_IN][InputState.HELD]:
            self.zoom_input += 1
        if action_buffer[Action.ZOOM_OUT][InputState.HELD]:
            self.zoom_input -= 1

        self.input_x, self.input_y = 0, 0
        if action_buffer[Action.LEFT][InputState.HELD]:
            self.input_x -= 1
        if action_buffer[Action.RIGHT][InputState.HELD]:
            self.input_x += 1
        if action_buffer[Action.UP][InputState.HELD]:
            self.input_y -= 1
        if action_buffer[Action.DOWN][InputState.HELD]:
            self.input_y += 1

        self.hold = action_buffer[Action.HOLD][InputState.PRESSED]
        self.rotate = mouse_buffer[MouseButton.RIGHT][InputState.PRESSED]
        self.try_place = mouse_buffer[MouseButton.LEFT][InputState.PRESSED]

    def update(self, dt: float) -> None:
        self.camera.move(dt, self.input_x, self.input_y)
        self.camera.change_zoom(dt, self.zoom_input)

        mouse_position = pygame.mouse.get_pos()
        offset_mouse_position = self.camera.screen_to_world(*mouse_position)
        hex = world_to_hex(*offset_mouse_position)
        self.hovered_tile = round_to_nearest_hex(hex)

        if self.hold:
            self.tile_manager.swap_held_tile()

        if self.rotate:
            self.tile_manager.rotate_active_tile()

        if self.try_place and self.hex_grid.is_open(self.hovered_tile):
            tile = self.tile_manager.create_active_tile(self.hovered_tile)
            if tile is not None:
                self.hex_grid.add_tile(tile)
                self.tile_manager.get_next_tile()

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((0, 255, 255))

        for hex_position_tuple in self.hex_grid.get_open_tiles():
            render_open_hex(surface, self.camera, HexPosition(*hex_position_tuple))

        active_tile = self.tile_manager.create_active_tile(self.hovered_tile)
        if active_tile is not None:
            render_hex(surface, self.camera, active_tile)

        for hex in self.hex_grid.get_placed_tiles():
            render_hex(surface, self.camera, hex)

        render_highlighted_hex(surface, self.camera, self.hovered_tile)

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

        self.font.render_to(surface, (0, 20), f"{self.hovered_tile}")
