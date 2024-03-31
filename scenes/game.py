import random
import pygame

from utilities.typehints import ActionBuffer, MouseBuffer
from config.input import InputState, MouseButton, Action
from baseclasses.scenemanager import Scene, SceneManager
import scenes.mainmenu
from utilities.math import PYTHAGORAS_CONSTANT
from config.settings import WINDOW_CENTRE
from components.hexagonalgrid import (
    Biome,
    HexPosition,
    HexTile,
    HexagonalGrid,
    world_to_hex,
    round_to_nearest_hex,
    render_hex,
    render_open_hex,
    render_highlighted_hex,
    zoom_in,
    zoom_out,
)
from components.camera import Camera


class Game(Scene):
    def __init__(self, scene_manager: SceneManager) -> None:
        super().__init__(scene_manager)
        self.font = pygame.freetype.Font("assets/joystix.otf", 10)
        self.font.antialiased = False

        self.hex_grid = HexagonalGrid()
        self.hex_grid.add_tile(HexTile(HexPosition(0, 0, 0), [Biome.GRASS] * 6))

        self.camera = Camera(0, 0, *WINDOW_CENTRE)
        self.move_speed = 5

        self.hovered_tile = HexPosition(0, 0, 0)

    def handle_input(
        self, action_buffer: ActionBuffer, mouse_buffer: MouseBuffer
    ) -> None:
        if action_buffer[Action.START][InputState.PRESSED]:
            self.scene_manager.switch_scene(scenes.mainmenu.MainMenu)

        if action_buffer[Action.A][InputState.HELD]:
            zoom_in()
        if action_buffer[Action.B][InputState.HELD]:
            zoom_out()

        input_x, input_y = 0, 0
        if action_buffer[Action.LEFT][InputState.HELD]:
            input_x -= 1
        if action_buffer[Action.RIGHT][InputState.HELD]:
            input_x += 1
        if action_buffer[Action.UP][InputState.HELD]:
            input_y -= 1
        if action_buffer[Action.DOWN][InputState.HELD]:
            input_y += 1

        if input_x != 0 and input_y != 0:
            input_x /= PYTHAGORAS_CONSTANT
            input_y /= PYTHAGORAS_CONSTANT

        self.camera.move(input_x * self.move_speed, input_y * self.move_speed)

        self.try_place = mouse_buffer[MouseButton.LEFT][InputState.PRESSED]

    def update(self, dt: float) -> None:
        mouse_position = pygame.mouse.get_pos()
        offset_mouse_position = self.camera.screen_to_world(*mouse_position)
        hex = world_to_hex(*offset_mouse_position)
        self.hovered_tile = round_to_nearest_hex(hex)

        if self.try_place and self.hex_grid.is_open(self.hovered_tile):
            # TODO: Move piece generation to separate class
            edges = [random.choice(list(Biome)) for i in range(6)]
            self.hex_grid.add_tile(HexTile(self.hovered_tile, edges))

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((0, 255, 255))

        for hex_position_tuple in self.hex_grid.get_open_tiles():
            render_open_hex(surface, self.camera, HexPosition(*hex_position_tuple))

        for hex in self.hex_grid.get_placed_tiles():
            render_hex(surface, self.camera, hex)

        render_highlighted_hex(surface, self.camera, self.hovered_tile)

        self.font.render_to(surface, (0, 20), f"{self.hovered_tile}")
