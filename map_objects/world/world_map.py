import tcod

from map_objects.world.world_tile import WorldTile
from entity_objects.static_entity import StaticEntity
from game_vars import color_vars
from random_utils import random_choice_from_dict
from map_objects.world.biomes import Biomes


class WorldMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()

        self.current_dungeon = None
        self.current_dungeon_entry_point = (0, 0)

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

        tiles = [[None for y in range(self.height)] for x in range(self.width)]
        for x in range(self.width):
            for y in range(self.height):
                tile = WorldTile(biom=Biomes.FOREST, bg_color=color_vars.forest_bg)
                tree_entity = StaticEntity(x, y, char=random_choice_from_dict(forest_chars), color=color_vars.forest)
                tile.place_static_entity(tree_entity)

                tiles[x][y] = tile

        return tiles

    def make_map(self, entities):
        entities.player.x = int(self.width * (2 / 3))
        entities.player.y = int(self.height * (2 / 3))
        self.tiles[entities.player.x][entities.player.y].regulatory_flags.add('visited')

        dungeon_entrance_x = self.width // 2
        dungeon_entrance_y = self.height // 2
        dungeon_tile = self.tiles[dungeon_entrance_x][dungeon_entrance_y]
        dungeon_tile.clear_static_entities()
        dungeon_tile.biom = Biomes.DUNGEON
        dungeon_entity = StaticEntity(dungeon_entrance_x, dungeon_entrance_y, char=tcod.CHAR_RADIO_SET, color=tcod.darker_grey)
        dungeon_tile.place_static_entity(dungeon_entity)

    def is_void(self, x, y):
        return x < 0 or y < 0 or x >= self.width or y >= self.height

    def current_biom(self, player=None):
        if self.current_dungeon:
            x, y = self.current_dungeon_entry_point
            return self.tiles[x][y].biom
        elif player and not self.current_dungeon:
            return self.tiles[player.x][player.y].biom
        return None

    # (bg_color, char, char_color)
    def tile_render_info(self, x, y, visible):
        tile = self.tiles[x][y]
        char_object = tile.top_char_object

        if visible:
            tile.regulatory_flags.add('explored')
            return (tile.bg_color(), char_object.char, char_object.color)
        elif 'explored' in tile.regulatory_flags:
            return (tile.bg_color_distant(), char_object.char, char_object.distant_color)

        return (None, None, None)
