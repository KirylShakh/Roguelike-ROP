import tcod
from random import randint

from map_objects.world.world_tile import WorldTile
from entity_objects.entity import Entity
from game_vars import color_vars
from random_utils import random_choice_from_dict
from map_objects.world.biomes import Biomes
from map_objects.biomes.forest.forest_locations import ForestLocations
from map_objects.biomes.dungeon.dungeon_locations import DungeonLocations


class WorldMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()

        self.current_dungeon = None
        self.current_dungeon_entry_point = (0, 0)

        self.potential_move = None

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
                tree_entity = Entity(x, y, char=random_choice_from_dict(forest_chars), color=color_vars.forest)
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
        dungeon_entity = Entity(dungeon_entrance_x, dungeon_entrance_y, char=tcod.CHAR_RADIO_SET, color=tcod.darker_grey)
        dungeon_tile.place_static_entity(dungeon_entity)

    def make_locations(self, tile):
        if tile.locations:
            return

        number_of_locations = randint(1, 5)
        tile.locations = []

        biom_location_creator = self.choose_creator_for_biom(tile.biom)
        for _ in range(number_of_locations):
            location = biom_location_creator.generate_location()
            tile.locations.append(location)

    def choose_creator_for_biom(self, biom):
        if biom == Biomes.FOREST:
            return ForestLocations()
        elif biom == Biomes.DUNGEON:
            return DungeonLocations()
        return None

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
