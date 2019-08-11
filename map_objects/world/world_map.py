import tcod

from map_objects.world.world_tile import WorldTile
from game_vars import color_vars
from random_utils import random_choice_from_dict


class WorldMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()

        self.current_dungeon = None
        self.current_dungeon_entry_point = None

    def initialize_tiles(self):
        forest_chars = {
            str(chr(tcod.CHAR_ARROW_N)): 25,
            str(chr(tcod.CHAR_VLINE)): 5,
            str(chr(tcod.CHAR_ARROW2_S)): 10,
            '|': 3,
            '\\': 7,
            '/': 7,
            'T': 40,
            'Y': 35,
        }

        tiles = [[WorldTile('forest', random_choice_from_dict(forest_chars), color_vars.forest, color_vars.forest_bg)
                    for y in range(self.height)] for x in range(self.width)]
        return tiles

    def make_map(self, entities):
        entities.player.x = int(self.width * (2 / 3))
        entities.player.y = int(self.height * (2 / 3))
        self.tiles[entities.player.x][entities.player.y].visited = True

        dungeon_entrance_x = self.width // 2
        dungeon_entrance_y = self.height // 2
        dungeon_tile = self.tiles[dungeon_entrance_x][dungeon_entrance_y]
        dungeon_tile.biom = 'dungeon'
        dungeon_tile.char = tcod.CHAR_RADIO_SET
        dungeon_tile.color = tcod.darker_grey
        dungeon_tile.bg_color = tcod.black
        dungeon_tile.distant_color = dungeon_tile.get_distant_color(dungeon_tile.color)
        dungeon_tile.distant_bg_color = dungeon_tile.get_distant_color(dungeon_tile.bg_color)

    def is_void(self, x, y):
        return x < 0 or y < 0 or x >= self.width or y >= self.height
