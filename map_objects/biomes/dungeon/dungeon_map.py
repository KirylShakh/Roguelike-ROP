from random import randint

import tcod

from map_objects.biomes.biom_map import BiomMap
from map_objects.biomes.dungeon.flora import Flora
from map_objects.biomes.dungeon.fauna import Fauna
from map_objects.biomes.dungeon.loot import Loot
from map_objects.rectangle import Rect
from entity_objects.entity import Entity
from components.stairs import Stairs, StairsDirections
from render_objects.render_order import RenderOrder
from game_vars import color_vars
from random_utils import random_choice_from_dict
from map_objects.landmarks.encounters.surround_encounter import SurroundEncounter
from map_objects.landmarks.encounters.camp_encounter import CampEncounter


class DungeonMap(BiomMap):
    def __init__(self, max_rooms, room_min_size, room_max_size, landmark=None):
        super().__init__()
        self.default_tile_blocked = True

        self.max_rooms = max_rooms
        self.room_min_size = room_min_size
        self.room_max_size = room_max_size
        self.landmark = landmark

        self.player_start = None

        self.flora = Flora()
        self.fauna = Fauna()
        self.loot = Loot()

        materials = {
            'stone': color_vars.dungeon_stone,
            'dirt': color_vars.dungeon_dirt,
        }
        self.material = materials[random_choice_from_dict({
            'stone': 10,
            'dirt': 10,
        })]

    def make_map(self, entities, moving_down=True):
        if self.encounter and self.encounter.place_order == 'start':
            self.encounter.create_on(self.owner, entities)

        rooms = []
        num_rooms = 0

        for _ in range(self.max_rooms):
            # random width and height
            w = randint(self.room_min_size, self.room_max_size)
            h = randint(self.room_min_size, self.room_max_size)
            # random position without going out of the boundaries of the map
            x = randint(0, self.owner.width - w - 1)
            y = randint(0, self.owner.height - h - 1)

            new_room = Rect(x, y, w, h)
            for other_room in rooms:
                if new_room.intersect(other_room):
                    break
            else:
                # this means there are no intersections, so this room is valid
                self.create_room(new_room)
                (new_x, new_y) = new_room.center()

                if num_rooms == 0:
                    if not self.encounter:
                        self.player_start = (new_x, new_y)
                        self.place_player(entities.player)
                else:
                    # all rooms after the first:
                    # connect it to the previous room with a tunnel
                    (prev_x, prev_y) = rooms[num_rooms - 1].center()

                    # flip a coin (random number that is either 0 or 1)
                    if randint(0, 1) == 1:
                        # first move horizontally, then vertically
                        self.create_h_tunnel(prev_x, new_x, prev_y)
                        self.create_v_tunnel(prev_y, new_y, new_x)
                    else:
                        # first move vertically, then horizontally
                        self.create_v_tunnel(prev_y, new_y, prev_x)
                        self.create_h_tunnel(prev_x, new_x, new_y)

                self.fauna.populate_room(new_room, self.owner.dungeon_level, entities)
                self.loot.fill_room(new_room, self.owner.dungeon_level, entities)
                self.flora.grow_fungi(self.owner, new_room)

                rooms.append(new_room)
                num_rooms += 1

        if moving_down:
            down_stairs_x = new_x
            down_stairs_y = new_y

            up_stairs_x = entities.player.x
            up_stairs_y = entities.player.y
        else:
            down_stairs_x = entities.player.x
            down_stairs_y = entities.player.y

            up_stairs_x = new_x
            up_stairs_y = new_y

        stairs_component = Stairs(self.owner.dungeon_level + 1)
        down_stairs = Entity(down_stairs_x, down_stairs_y, char='>', color=tcod.white,
                                name='Stairs down', render_order=RenderOrder.STAIRS,
                                stairs=stairs_component)
        entities.append(down_stairs)

        if self.owner.dungeon_level == 1:
            direction = StairsDirections.WORLD
            stairs_name = 'Stairs outside'
        else:
            direction = StairsDirections.UP
            stairs_name = 'Stairs up'

        up_stairs_component = Stairs(self.owner.dungeon_level, direction=direction)
        up_stairs = Entity(up_stairs_x, up_stairs_y, char='<', color=tcod.white,
                            name=stairs_name, render_order=RenderOrder.STAIRS,
                            stairs=up_stairs_component)
        entities.append(up_stairs)

        for x in range(self.owner.width):
            for y in range(self.owner.height):
                tile = self.owner.tiles[x][y]
                if 'blocked' in tile.regulatory_flags:
                    tile.set_bg_color(self.material['wall'])
                else:
                    tile.set_bg_color(self.material['floor'])

        if self.encounter and self.encounter.place_order == 'end':
            self.encounter.create_on(self.owner, entities)

    # disable dungeon encounter until dungeon map will not be reworked
    # also until way of setting place on map for encounters and player will be defined properly
    def choose_encounter(self):
        return False

    def possible_encounters(self):
        return {
            'bandit_ambush': {
                'class': SurroundEncounter,
                'weight_factor': 20,
                'parameters': {
                    'entity_type': 'bandit',
                },
            },
            'camp': {
                'class': CampEncounter,
                'weight_factor': 10,
                'parameters': {},
            },
        }

    def place_player(self, player):
        player.x, player.y = self.player_start

    def create_room(self, room):
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.owner.tiles[x][y].unblock()

    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.owner.tiles[x][y].unblock()

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.owner.tiles[x][y].unblock()

    # (bg_color, char, char_color)
    def tile_render_info(self, x, y, visible):
        tile = self.owner.tiles[x][y]
        char_object = tile.top_char_object
        bg_color = None
        fg_color = None
        char = None

        if visible:
            if 'blocked' in tile.regulatory_flags:
                bg_color = tile.bg_color()
            else:
                bg_color = tile.bg_color()
                if char_object:
                    fg_color = char_object.color
                    char = char_object.char

            tile.regulatory_flags.add('explored')
        elif 'explored' in tile.regulatory_flags:
            if 'blocked' in tile.regulatory_flags:
                bg_color = tile.bg_color_distant()
            else:
                bg_color = tile.bg_color_distant()
                if char_object:
                    fg_color = char_object.distant_color
                    char = char_object.char

        return (bg_color, char, fg_color)
