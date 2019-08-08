from random import randint

import tcod

from game_vars import room_vars
from random_utils import random_choice_from_dict, from_dungeon_level
from render_objects.render_order import RenderOrder
from map_objects.tile import Tile
from map_objects.rectangle import Rect
from entity_objects.entity import Entity
from entity_objects.map_entities import MapEntities
from game_messages import Message
import entity_objects.creators.npc_creator as npc_creator
import entity_objects.creators.item_creator as item_creator
from components.stairs import Stairs
from map_objects.path_functions import path_straight


class GameMap:
    def __init__(self, width, height, dungeon_level=1):
        self.width = width
        self.height = height
        self.dungeon_level = dungeon_level
        self.tiles = self.initialize_tiles()

    def initialize_tiles(self):
        return [[Tile(True) for y in range(self.height)] for x in range(self.width)]

    def create_room(self, room):
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.tiles[x][y].unblock()

    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[x][y].unblock()

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x][y].unblock()

    def make_map(self, max_rooms, room_min_size, room_max_size, entities):
        rooms = []
        num_rooms = 0

        center_of_last_room_x = None
        center_of_last_room_y = None

        for r in range(max_rooms):
            # random width and height
            w = randint(room_min_size, room_max_size)
            h = randint(room_min_size, room_max_size)
            # random position without going out of the boundaries of the map
            x = randint(0, self.width - w - 1)
            y = randint(0, self.height - h - 1)

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

        center_of_last_room_x = new_x
        center_of_last_room_y = new_y

        stairs_component = Stairs(self.dungeon_level + 1)
        down_stairs = Entity(center_of_last_room_x, center_of_last_room_y, '>', tcod.white,
                                'Stairs down', render_order=RenderOrder.STAIRS,
                                stairs=stairs_component)
        entities.append(down_stairs)

    def place_entities(self, room, entities):
        max_monsters_per_room = from_dungeon_level([[2, 1], [3, 4], [5, 6]], self.dungeon_level)
        max_items_per_room = from_dungeon_level([[1, 1], [2, 4]], self.dungeon_level)

        number_of_monsters = randint(0, max_monsters_per_room)
        number_of_items = randint(0, max_items_per_room)

        monster_chances = {
            'orc': 80,
            'troll': from_dungeon_level([[15, 3], [30, 5], [60, 7]], self.dungeon_level),
        }
        item_chances = {
            'healing_potion': 35,
            'sword': from_dungeon_level([[5, 4]], self.dungeon_level),
            'shield': from_dungeon_level([[15, 8]], self.dungeon_level),
            'lightning_scroll': from_dungeon_level([[25, 4]], self.dungeon_level),
            'fireball_scroll': from_dungeon_level([[25, 6]], self.dungeon_level),
            'confuse_scroll': from_dungeon_level([[10, 2]], self.dungeon_level),
        }

        for i in range(number_of_monsters):
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

        for i in range(number_of_items):
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

    def is_blocked(self, x, y):
        if self.tiles[x][y].blocked:
            return True

        return False

    def next_floor(self, player, message_log):
        self.dungeon_level += 1
        entities = MapEntities(player)

        self.tiles = self.initialize_tiles()
        self.make_map(room_vars.max_num, room_vars.min_size, room_vars.max_size, entities)

        player.fighter.heal(player.fighter.max_hp // 2)
        message_log.add_message(Message('You take a moment to rest, and recover your strength',
                                tcod.light_violet))

        return entities

    def is_path_blocked(self, path, entities):
        for x, y in path:
            if self.is_blocked(x, y) or entities.get_blocking_at_location(x, y):
                return True
        return False

    def path_straight(self, src_x, src_y, dst_x, dst_y):
        return path_straight(src_x, src_y, dst_x, dst_y)
