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


class DungeonMap(BiomMap):
    def __init__(self, max_rooms, room_min_size, room_max_size):
        self.max_rooms = max_rooms
        self.room_min_size = room_min_size
        self.room_max_size = room_max_size

        self.default_tile_blocked = True

        self.fov_radius = 10

        self.flora = Flora()
        self.fauna = Fauna()
        self.loot = Loot()

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
        fg_color = None
        char = None

        if visible:
            if tile.blocked:
                color = color_vars.light_wall
            else:
                color = color_vars.light_ground
                if tile.char:
                    fg_color = tile.char.color
                    char = tile.char.char

            tile.explored = True
        elif tile.explored:
            if tile.blocked:
                color = color_vars.dark_wall
            else:
                color = color_vars.dark_ground
                if tile.char:
                    fg_color = tile.char.distant_color
                    char = tile.char.char

        return (color, char, fg_color)
