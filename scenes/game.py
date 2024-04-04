import math
import pygame

from utilities.typehints import ActionBuffer, MouseBuffer
from config.input import InputState, MouseButton, Action
from baseclasses.scenemanager import Scene, SceneManager
from config.settings import WINDOW_CENTRE, WINDOW_WIDTH, WINDOW_HEIGHT
from components.hexagonalgrid import (
    SIZE,
    HEXAGONAL_NEIGHBOURS,
    OPEN_COLOUR,
    OUTLINE_COLOUR,
    HIGHLIGHT_COLOUR,
    HOVER_COLOUR,
    Biome,
    SideStates,
    HexPosition,
    HexTile,
    HexagonalGrid,
    get_hex_corners,
    hex_to_world,
    world_to_hex,
    round_to_nearest_hex,
    render_hex,
    render_open_hex,
    render_highlighted_hex,
    render_preview_hex,
    generate_hex_art,
)
from components.tilemanager import TileManager, STARTING_BIOME
from components.camera import Camera
from components.ui import render_centered_text, PopupText, render_to
from utilities.spriteloading import slice_sheet
from components.animationplayer import AnimationPlayer


PREVIEW_OFFSET = SIZE * 2
PREVIEW_X = WINDOW_WIDTH - SIZE
PREVIEW_Y = SIZE / 2 + 2

HELD_X = SIZE
HELD_Y = WINDOW_CENTRE[1]

MOVE_X = WINDOW_CENTRE[0] - PREVIEW_OFFSET
MOVE_Y = WINDOW_CENTRE[1] - SIZE


class Game(Scene):
    def __init__(self, scene_manager: SceneManager) -> None:
        super().__init__(scene_manager)

        self.muted = False
        self.hold_sfx = pygame.mixer.Sound("assets/hold.ogg")
        self.perfect_sfx = pygame.mixer.Sound("assets/perfect.ogg")
        self.place_sfx = pygame.mixer.Sound("assets/place.ogg")
        self.rotate_sfx = pygame.mixer.Sound("assets/rotate.ogg")

        self.popup_font = pygame.font.Font("assets/joystix.ttf", 8)
        self.font = pygame.font.Font("assets/joystix.ttf", 10)
        self.big_font = pygame.font.Font("assets/joystix.ttf", 20)

        self.BIOME_SPRITES = slice_sheet("assets/tiles-Sheet.png", 8, 8)
        self.BIOME_SPRITE_MAP = {
            Biome.SWAMP: [0, 6, 12],
            Biome.GRASS: [1, 7, 13],
            Biome.SAND: [2, 8, 14],
            Biome.FOREST: [3, 9, 15],
            Biome.MOUNTAIN: [4, 10, 16],
            Biome.SNOW: [5, 11, 17],
        }

        self.hex_grid = HexagonalGrid()
        start_hex = HexTile(
            HexPosition(0, 0, 0), [STARTING_BIOME] * 6, [None] * 6, None
        )
        start_hex.sector_sprites = generate_hex_art(
            start_hex.sides, self.BIOME_SPRITE_MAP
        )
        self.hex_grid.add_tile(start_hex)

        self.tile_manager = TileManager(6, 50)
        self.camera = Camera(0, 0, *WINDOW_CENTRE)

        self.hovered_tile = HexPosition(0, 0, 0)
        self.score = 0

        place_frames = []
        place_length = 16
        for i in range(place_length):
            frame = pygame.Surface((SIZE * 4, SIZE * 4), pygame.SRCALPHA)
            waves = get_hex_corners(
                SIZE * 2, SIZE * 2, SIZE * (1.5 - i / (place_length * 2))
            )
            pygame.draw.polygon(frame, (0, 0, 0, i * (150 / place_length)), waves, 2)
            place_frames.append(frame)
        place_frames.reverse()
        self.place_animation = AnimationPlayer("place", place_frames, 0.05, False)
        self.place_location = (0, 0)

        perfect_frames = []
        perfect_length = 16
        for i in range(perfect_length):
            frame = pygame.Surface((SIZE * 2, SIZE * 2), pygame.SRCALPHA)
            waves = get_hex_corners(SIZE, SIZE, SIZE * (i / (place_length)))
            pygame.draw.polygon(
                frame, (255, 255, 255, i * (150 / place_length)), waves, 2
            )
            perfect_frames.append(frame)
        perfect_frames.reverse()
        self.perfect_animations = [
            AnimationPlayer("perfect", perfect_frames, 0.05, False) for i in range(7)
        ]
        self.perfect_locations = [(1000, 1000) for i in range(7)]

        self.edge_popup_text = [
            PopupText(1000, 1000, self.popup_font, "+10", HOVER_COLOUR, 0.7)
            for _ in range(6)
        ]
        self.perfect_popup_text = [
            PopupText(1000, 1000, self.popup_font, "PERFECT!", HIGHLIGHT_COLOUR, 1)
            for _ in range(7)
        ]

    def handle_input(
        self, action_buffer: ActionBuffer, mouse_buffer: MouseBuffer
    ) -> None:
        if action_buffer[Action.BACK][InputState.PRESSED]:
            self.scene_manager.switch_scene(None)
        if action_buffer[Action.RESTART][InputState.PRESSED]:
            self.scene_manager.switch_scene(Game)

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
        self.centre = action_buffer[Action.CENTRE][InputState.PRESSED]
        self.toggle_mute = action_buffer[Action.MUTE][InputState.PRESSED]

    def update(self, dt: float) -> None:
        self.camera.move(dt, self.input_x, self.input_y)

        if self.toggle_mute:
            self.muted = not self.muted
            if self.muted:
                pygame.mixer.Channel(0).set_volume(0)
                pygame.mixer.Channel(1).set_volume(0)
                pygame.mixer.Channel(2).set_volume(0)
                pygame.mixer.Channel(3).set_volume(0)
                pygame.mixer.Channel(4).set_volume(0)
            else:
                pygame.mixer.Channel(0).set_volume(0.5)
                pygame.mixer.Channel(1).set_volume(1)
                pygame.mixer.Channel(2).set_volume(1)
                pygame.mixer.Channel(3).set_volume(1)
                pygame.mixer.Channel(4).set_volume(1)

        if self.centre:
            self.camera.x = 0
            self.camera.y = 0

        if self.hold:
            self.tile_manager.swap_held_tile()
            pygame.mixer.Channel(1).play(self.hold_sfx)

        if self.rotate:
            self.tile_manager.rotate_active_tile()
            pygame.mixer.Channel(4).play(self.rotate_sfx)

        if self.try_place and self.hex_grid.is_open(self.hovered_tile):
            tile = self.tile_manager.create_active_tile(self.hovered_tile)
            if tile is not None:
                tile.sector_sprites = generate_hex_art(
                    tile.sides, self.BIOME_SPRITE_MAP
                )

                self.hex_grid.add_tile(tile)
                pygame.mixer.Channel(3).play(self.place_sfx)

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
                        popup_pos = hex_to_world(tile.position)
                        offset_pos = hex_to_world(neighbour)
                        edge_pos = (
                            popup_pos[0] + offset_pos[0] // 2,
                            popup_pos[1] + offset_pos[1] // 2,
                        )
                        self.edge_popup_text[i].move(*edge_pos)
                        self.score += 10
                        tile.matching_sides += 1
                        adj_tile.matching_sides += 1

                        if adj_tile.matching_sides == 6:
                            self.score += 100
                            self.tile_manager.add_to_remaining(3)
                            self.perfect_popup_text[i + 1].move(
                                *hex_to_world(adj_tile.position)
                            )
                            pygame.mixer.Channel(2).play(self.perfect_sfx)
                            self.perfect_locations[i + 1] = hex_to_world(
                                adj_tile.position
                            )
                            self.perfect_animations[i + 1].reset()
                    else:
                        tile.can_be_perfect = False
                        adj_tile.can_be_perfect = False

                if tile.matching_sides == 6:
                    self.score += 100
                    self.tile_manager.add_to_remaining(3)

                    self.perfect_popup_text[0].move(*popup_pos)
                    pygame.mixer.Channel(2).play(self.perfect_sfx)
                    self.perfect_locations[0] = hex_to_world(tile.position)
                    self.perfect_animations[0].reset()

                self.tile_manager.get_next_tile()

                self.place_location = hex_to_world(tile.position)
                self.place_animation.reset()

        self.place_animation.update(dt)
        for anim in self.perfect_animations:
            anim.update(dt)

        for text in self.edge_popup_text:
            text.update(dt)

        for text in self.perfect_popup_text:
            text.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((83, 216, 251))

        for hex_position_tuple in self.hex_grid.get_open_tiles():
            render_open_hex(surface, self.camera, HexPosition(*hex_position_tuple))

        place_screen = self.camera.world_to_screen(*self.place_location)
        place_screen = (place_screen[0] - SIZE * 2, place_screen[1] - SIZE * 2)
        surface.blit(self.place_animation.get_frame(), place_screen)

        active_tile = self.tile_manager.create_active_tile(self.hovered_tile)
        if active_tile is not None:
            render_hex(surface, self.camera, active_tile, self.BIOME_SPRITES)

        for hex in self.hex_grid.get_placed_tiles():
            render_hex(surface, self.camera, hex, self.BIOME_SPRITES)

        matching_sides = [SideStates.UNKNOWN] * 6
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
                    matching_sides[i] = SideStates.MATCH
                else:
                    matching_sides[i] = SideStates.MISSMATCH

        render_highlighted_hex(surface, self.camera, self.hovered_tile, matching_sides)

        for i, anim in enumerate(self.perfect_animations):
            perfect_screen = self.camera.world_to_screen(*self.perfect_locations[i])
            perfect_screen = (perfect_screen[0] - SIZE, perfect_screen[1] - SIZE)
            surface.blit(anim.get_frame(), perfect_screen)

        for text in self.edge_popup_text:
            text.render(surface, self.camera)

        for text in self.perfect_popup_text:
            text.render(surface, self.camera)

        pygame.draw.rect(
            surface,
            OPEN_COLOUR,
            ((0, 0), (WINDOW_WIDTH, WINDOW_CENTRE[1] - MOVE_Y)),
        )
        pygame.draw.rect(
            surface,
            OPEN_COLOUR,
            ((0, 0), (WINDOW_CENTRE[0] - MOVE_X, WINDOW_HEIGHT)),
        )
        pygame.draw.rect(
            surface,
            OPEN_COLOUR,
            (
                (WINDOW_CENTRE[0] + MOVE_X, 0),
                (WINDOW_CENTRE[0] - MOVE_X, WINDOW_HEIGHT),
            ),
        )
        pygame.draw.rect(
            surface,
            OPEN_COLOUR,
            ((0, WINDOW_CENTRE[1] + MOVE_Y), (WINDOW_WIDTH, WINDOW_CENTRE[1] - MOVE_Y)),
        )

        for i, preview in enumerate(self.tile_manager.get_preview()):
            if preview is None:
                break
            render_preview_hex(
                surface, PREVIEW_X, (i + 1) * PREVIEW_OFFSET + 10, preview
            )

        held_tile = self.tile_manager.get_held()
        if held_tile is not None:
            render_preview_hex(surface, HELD_X, HELD_Y, held_tile)

        render_centered_text(
            surface, self.font, "HELD", (HELD_X, HELD_Y - SIZE - 16), OUTLINE_COLOUR
        )

        render_centered_text(
            surface,
            self.big_font,
            f"{self.tile_manager.get_remaining()}",
            (PREVIEW_X, PREVIEW_Y),
            HOVER_COLOUR,
        )

        render_centered_text(
            surface, self.font, "LEFT", (PREVIEW_X, PREVIEW_Y + 14), OUTLINE_COLOUR
        )

        render_centered_text(
            surface,
            self.font,
            f"{self.hovered_tile}",
            (WINDOW_CENTRE[0], WINDOW_HEIGHT - 10),
            OUTLINE_COLOUR,
        )

        render_centered_text(
            surface,
            self.big_font,
            f"{self.score}",
            (WINDOW_CENTRE[0], PREVIEW_Y),
            HOVER_COLOUR,
        )

        if self.tile_manager.get_remaining() == 0:
            render_to(surface, self.font, "GAME OVER!", (3, 5), OUTLINE_COLOUR)
            render_to(
                surface,
                self.font,
                "PRESS R TO RESTART",
                (3, WINDOW_HEIGHT - 15),
                OUTLINE_COLOUR,
            )
