from random import randint, choice


class Rect:
    def __init__(self, x, y, w, h, calculate_borders=False):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

        if calculate_borders:
            self.w = w
            self.h = h
            self.calculate_borders()
            self.area = w * h

    def center(self):
        x = int((self.x1 + self.x2) / 2)
        y = int((self.y1 + self.y2) / 2)
        return (x, y)

    def intersect(self, other):
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)

    def intersect_with_additional_space(self, other, space=1):
        return (self.x1 - space <= other.x2 and self.x2 + space >= other.x1 and
                self.y1 - space <= other.y2 and self.y2 + space >= other.y1)

    def belongs(self, x, y):
        return x >= self.x1 and x < self.x2 and y >= self.y1 and y < self.y2

    def opposite_direction(self, direction):
        if direction == 'west':
            return 'east'
        if direction == 'east':
            return 'west'
        if direction == 'north':
            return 'south'
        if direction == 'south':
            return 'north'

    def random_inside_tile(self, direction=None):
        width = self.w - 2
        height = self.h - 2

        x_min = self.x1 + 1
        x_max = self.x2 - 1
        y_min = self.y1 + 1
        y_max = self.y2 - 1

        if direction:
            if direction == 'west':
                width -= 1
                x_min += 1
            elif direction == 'east':
                width -= 1
                x_max -= 1
            elif direction == 'north':
                height -= 1
                y_min += 1
            elif direction == 'south':
                height -= 1
                y_max -= 1


        index = randint(1, width * height)
        i = 1
        for x in range(x_min, x_max):
            for y in range(y_min, y_max):
                if i == index:
                    return (x, y)
                i += 1

    def random_side_tile(self):
        return choice(self.side_tiles)

    def random_direction_side_tile(self, direction=None):
        if not direction:
            direction = choice(list(self.sides.keys()))

        return (direction, choice(self.sides[direction]))

    def random_side(self, directions=None):
        if not directions:
            directions = list(self.sides.keys())

        side_direction = choice(directions)
        return (side_direction, self.sides[side_direction])

    def random_short_side(self):
        if self.x2 - self.x1 < self.y2 - self.y1:
            return self.random_side(['north', 'south'])
        else:
            return self.random_side(['east', 'west'])

    def neighbour_sides(self, direction):
        if direction in ['east', 'west']:
            return [self.sides['north'], self.sides['south']]
        else:
            return [self.sides['east'], self.sides['west']]

    def calculate_borders(self):
        self.border_tiles = self.calculate_border_tiles()
        self.corner_tiles = self.calculate_corner_tiles()
        self.side_tiles = [t for t in self.border_tiles if t not in self.corner_tiles]
        self.sides = self.calculate_sides()

    def calculate_corner_tiles(self):
        return [(self.x1, self.y1), (self.x2 - 1, self.y1), (self.x2 - 1, self.y2 - 1), (self.x1, self.y2 - 1)]

    def calculate_sides(self):
        tiles = {}
        tiles['north'] = [(x, self.y1) for x in range(self.x1 + 1, self.x2 - 1)]
        tiles['east'] = [(self.x2 - 1, y) for y in range(self.y1 + 1, self.y2 - 1)]
        tiles['south'] = [(x, self.y2 - 1) for x in range(self.x1 + 1, self.x2 - 1)]
        tiles['west'] = [(self.x1, y) for y in range(self.y1 + 1, self.y2 - 1)]

        return tiles

    def calculate_border_tiles(self):
        tiles = []

        y = self.y1
        for x in range(self.x1, self.x2):
            tiles.append((x, y))

        x = self.x2 - 1
        for y in range(self.y1 + 1, self.y2):
            tiles.append((x, y))

        y = self.y2 - 1
        for x in range(self.x2 - 2, self.x1 - 1, -1):
            tiles.append((x, y))

        x = self.x1
        for y in range(self.y2 - 2, self.y1, -1):
            tiles.append((x, y))

        return tiles

    def __str__(self):
        return 'Rect {0}:{1}; W:{2}, H:{3}'.format((self.x1, self.y1), (self.x2, self.y2), self.w, self.h)
