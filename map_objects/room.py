from random import choice

from map_objects.rectangle import Rect


class Room(Rect):
    def __init__(self, x, y, w, h, calculate_borders=True):
        super(Room, self).__init__(x, y, w, h, calculate_borders)

        self.inner_doors = []
        self.type = 'general'

    def random_intersection_side_tile(self, other_room):
        direction = self.intersection_direction(other_room)

        self_side = self.sides[direction]
        other_side = other_room.sides[self.opposite_direction(direction)]
        common_wall = [tile for tile in self_side if tile in other_side]

        # common wall can be empty: investigate under which circumstances
        if not common_wall:
            print('Cant find common wall between rooms "{0}" and "{1}"'.format(self, other_room))
            print('Self side: {0}; other side: {1}'.format(self_side, other_side))
            print(direction)
            print(self.opposite_direction(direction))

        return (direction, choice(common_wall))

    def intersection_direction(self, other_room):
        if self.x1 == other_room.x2 - 1:
            return 'west'
        if self.x2 - 1 == other_room.x1:
            return 'east'
        if self.y1 == other_room.y2 - 1:
            return 'north'
        if self.y2 - 1 == other_room.y1:
            return 'south'
        return None

    def opposite_direction(self, direction):
        if direction == 'west':
            return 'east'
        if direction == 'east':
            return 'west'
        if direction == 'north':
            return 'south'
        if direction == 'south':
            return 'north'

    def make_door_with(self, other_room):
        direction, door = self.random_intersection_side_tile(other_room)

        self.inner_doors.append((direction, door))
        other_room.inner_doors.append((self.opposite_direction(direction), door))

        return door
