from random import randint

import tcod

from map_objects.map_components.map_component import MapComponent
from map_objects.rectangle import Rect
from random_utils import random_choice_from_dict, from_dungeon_level
from entity_objects.entity import Entity
from components.stairs import Stairs, StairsDirections
from render_objects.render_order import RenderOrder
from game_vars import color_vars

import entity_objects.creators.npc_creator as npc_creator
import entity_objects.creators.item_creator as item_creator


class Dungeon(MapComponent):
    def __init__(self, max_rooms, room_min_size, room_max_size):
        self.max_rooms = max_rooms
        self.room_min_size = room_min_size
        self.room_max_size = room_max_size

        self.default_tile_blocked = True

        self.fov_radius = 10

    def make_map(self, entities, moving_down=True):
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
                    entities.player.x = new_x
                    entities.player.y = new_y
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

                self.place_entities(new_room, entities)
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
        down_stairs = Entity(down_stairs_x, down_stairs_y, '>', tcod.white,
                                'Stairs down', render_order=RenderOrder.STAIRS,
                                stairs=stairs_component)
        entities.append(down_stairs)

        if self.owner.dungeon_level == 1:
            direction = StairsDirections.WORLD
            stairs_name = 'Stairs outside'
        else:
            direction = StairsDirections.UP
            stairs_name = 'Stairs up'

        up_stairs_component = Stairs(self.owner.dungeon_level, direction=direction)
        up_stairs = Entity(up_stairs_x, up_stairs_y, '<', tcod.white,
                            stairs_name, render_order=RenderOrder.STAIRS,
                            stairs=up_stairs_component)
        entities.append(up_stairs)

    def place_entities(self, room, entities):
        max_monsters_per_room = from_dungeon_level([[2, 1], [3, 4], [5, 6]], self.owner.dungeon_level)
        max_items_per_room = from_dungeon_level([[1, 1], [2, 4]], self.owner.dungeon_level)

        number_of_monsters = randint(0, max_monsters_per_room)
        number_of_items = randint(0, max_items_per_room)

        monster_chances = {
            'orc': 80,
            'troll': from_dungeon_level([[15, 3], [30, 5], [60, 7]], self.owner.dungeon_level),
        }
        item_chances = {
            'healing_potion': 35,
            'sword': from_dungeon_level([[5, 4]], self.owner.dungeon_level),
            'shield': from_dungeon_level([[15, 8]], self.owner.dungeon_level),
            'lightning_scroll': from_dungeon_level([[25, 4]], self.owner.dungeon_level),
            'fireball_scroll': from_dungeon_level([[25, 6]], self.owner.dungeon_level),
            'confuse_scroll': from_dungeon_level([[10, 2]], self.owner.dungeon_level),
        }

        for _ in range(number_of_monsters):
            # Choose a random location in room
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)
            if not entities.find_by_point(x, y):
                monster_choice = random_choice_from_dict(monster_chances)
                if monster_choice == 'orc':
                    monster = npc_creator.create_orc(x, y)
                elif monster_choice == 'troll':
                    monster = npc_creator.create_troll(x, y)

                entities.append(monster)

        for _ in range(number_of_items):
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            if not entities.find_by_point(x, y):
                item_choice = random_choice_from_dict(item_chances)

                if item_choice == 'healing_potion':
                    item = item_creator.create_healing_potion(x, y)
                elif item_choice == 'sword':
                    item = item_creator.create_sword(x, y)
                elif item_choice == 'shield':
                    item = item_creator.create_shield(x, y)
                elif item_choice == 'fireball_scroll':
                    item = item_creator.create_fireball_scroll(x, y)
                elif item_choice == 'confuse_scroll':
                    item = item_creator.create_confuse_scroll(x, y)
                elif item_choice == 'lightning_scroll':
                    item = item_creator.create_lightning_scroll(x, y)
                entities.append(item)

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
        color = None

        if visible:
            if tile.blocked:
                color = color_vars.light_wall
            else:
                color = color_vars.light_ground

            tile.explored = True
        elif tile.explored:
            if tile.blocked:
                color = color_vars.dark_wall
            else:
                color = color_vars.dark_ground

        return (color, None, None)
