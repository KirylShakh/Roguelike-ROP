import math
from random import randint, choice
import tcod

from map_objects.landmarks.hut import Hut
from map_objects.room import Room
from map_objects.char_object import Char
from map_objects.rectangle import Rect
from game_vars import color_vars


class House(Hut):
    def __init__(self, name, parent=None):
        super().__init__(name, parent=parent)

        self.chair_char = Char(char='_', color=color_vars.wood, name='Stool in {0}'.format(name))
        self.bag_char = Char(char='&', color=color_vars.wood, name='Bag in {0}'.format(name))

    def init_constants(self):
        super().init_constants()

        self.min_width = 6
        self.max_width = 12

        self.min_height = 6
        self.max_height = 12

    def make_walls(self):
        super().make_walls()

        self.rooms = [Room(self.rect.x1, self.rect.y1, self.rect.w, self.rect.h)]
        room_number = round(math.sqrt(self.rect.w * self.rect.h) / 3)
        for _ in range(1, room_number):
            room = self.find_biggest_room()

            if room.w >= room.h:
                wall_x = randint(room.x1 + 2, room.x2 - 3)
                wall_start = (wall_x, room.y1)
                wall_end = (wall_x + 1, room.y2)
            else:
                wall_y = randint(room.y1 + 2, room.y2 - 3)
                wall_start = (room.x1, wall_y)
                wall_end = (room.x2, wall_y + 1)

            wall_start_x, wall_start_y = wall_start
            wall_end_x, wall_end_y = wall_end

            for x in range(wall_start_x, wall_end_x):
                for y in range(wall_start_y, wall_end_y):
                    if (x, y) not in self.walls:
                        self.walls.append((x, y))

            new_room_1 = Room(room.x1, room.y1, wall_end_x - room.x1, wall_end_y - room.y1)
            new_room_2 = Room(wall_start_x, wall_start_y, room.x2 - wall_start_x, room.y2 - wall_start_y)

            self.rooms.extend([new_room_1, new_room_2])

    def find_biggest_room(self):
        biggest = self.rooms[0]
        index = 0
        for i, room in enumerate(self.rooms):
            if room.area > biggest.area:
                biggest = room
                index = i
        return self.rooms.pop(index)

    def make_door(self):
        super().make_door()

        self.inner_doors = []
        entrance_room = self.entrance_room()
        if not entrance_room:
            # door is right between inner rooms, for now just adjust its position one space
            x, y = self.door
            if self.door_side_direction in ['west', 'east']:
                self.door = (x, y - 1)
            else:
                self.door = (x - 1, y)

            entrance_room = self.entrance_room()

        self.handle_room(entrance_room)

    def entrance_room(self):
        for room in self.rooms:
            if self.door in room.sides[self.door_side_direction]:
                return room
        return None

    def handle_room(self, next_room):
        delayed_rooms = []
        for room in self.rooms:
            if room != next_room and room.intersect(next_room):
                if not room.inner_doors:
                    new_door = next_room.make_door_with(room)
                    self.inner_doors.append(new_door)

                    # gives a 33% chance for a room to have multiple inner doors to adjancent rooms (66% chance?)
                    if randint(0, 2) == 0:
                        self.handle_room(room)
                    else:
                        delayed_rooms.append(room)

        for room in delayed_rooms:
            self.handle_room(room)

    def make_furniture(self):
        self.assign_room_types()
        self.furniture = []

        for room in self.rooms:
            if room.type == 'dining':
                chair_x, chair_y = room.random_inside_tile()
                table_x, table_y = room.random_inside_tile()
                while (table_x, table_y) == (chair_x, chair_y):
                    table_x, table_y = room.random_inside_tile()

                self.furniture.append((chair_x, chair_y, self.chair_char))
                self.furniture.append((table_x, table_y, self.table_char))
            if room.type == 'bedroom':
                bed_x, bed_y = room.random_inside_tile()
                self.furniture.append((bed_x, bed_y, self.bed_char))
            if room.type == 'workarea':
                table_x, table_y = room.random_inside_tile()
                self.furniture.append((table_x, table_y, self.table_char))
            if room.type == 'storage':
                bag_x, bag_y = room.random_inside_tile()
                self.furniture.append((bag_x, bag_y, self.bag_char))

    def assign_room_types(self):
        self.rooms.sort(key=lambda room: room.area, reverse=True)
        types = ['dining', 'bedroom', 'workarea', 'storage']
        for i in range(0, len(self.rooms)):
            if i < len(types):
                room_type = types[i]
            room = self.rooms[i]
            room.type = room_type

    def place(self, game_map):
        super().place(game_map)

        for (x, y) in self.inner_doors:
            game_map.tiles[x][y].unblock()
            game_map.tiles[x][y].char = self.door_char
