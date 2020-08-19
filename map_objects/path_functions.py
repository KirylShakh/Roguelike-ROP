from random import randint


def path_straight(src_x, src_y, dst_x, dst_y, max_distance=10):
    delta_x = dst_x - src_x
    delta_y = dst_y - src_y

    sign_x = -1 if delta_x < 0 else 1
    sign_y = -1 if delta_y < 0 else 1

    path = []

    if abs(delta_x) < abs(delta_y):
        multiplier_x = abs(delta_x / delta_y)
        multiplier_y = 1
    else:
        multiplier_y = abs(delta_y / delta_x)
        multiplier_x = 1

    x = src_x
    y = src_y
    dx = 0
    dy = 0
    while not ((abs(dst_x - x) <= 1 and abs(dst_y - y) <= 1) or len(path) > max_distance):
        dx = mult(dx, sign_x, multiplier_x)
        dy = mult(dy, sign_y, multiplier_y)

        rounded_dx = round(dx)
        rounded_dy = round(dy)
        x += rounded_dx
        y += rounded_dy

        path.append((x, y))

        if abs(dx) == 1:
            dx = 0
        elif abs(rounded_dx) == 1:
            dx -= 0.5
        if abs(dy) == 1:
            dy = 0
        elif abs(rounded_dy) == 1:
            dy -= 0.5

    return path

def mult(i, sign, multiplier):
    if i != 0:
        i += sign * multiplier
        if abs(i) >= 1:
            i -= sign
    else:
        i += sign * multiplier
    return i

# area_map is a 2-dimensional array - map where path is calculated
# values of this array: -1 for tiles which can be part of path, -2 for blocked
def find_path_in_area(start_tile, end_tile, area_map, max_distance=100):
    x, y = end_tile
    counter = 0

    area_map[x][y] = counter
    queue = [(x, y)]

    while start_tile not in queue:
        next_queue = []
        counter += 1
        if counter > max_distance:
            return []

        for i, j in queue:
            for x, y in get_neighbors(i, j, area_map):
                if area_map[x][y] == -1:
                    next_queue.append((x, y))
                    area_map[x][y] = counter

        queue = next_queue

    path = []
    current_tile = start_tile
    while current_tile != end_tile:
        i, j = current_tile
        neighbors = get_neighbors(i, j, area_map)
        min_x, min_y = neighbors[0]

        for x, y in neighbors:
            if area_map[min_x][min_y] < 0:
                min_x, min_y = x, y
            elif area_map[x][y] < 0:
                continue
            elif area_map[x][y] < area_map[min_x][min_y]:
                min_x, min_y = x, y
        candidates = [(x, y) for x, y in neighbors if (x, y) == (min_x, min_y)]
        current_tile = candidates[randint(0, len(candidates) - 1)]
        path.append(current_tile)

    return path[:-1]

def get_neighbors(i, j, area_map):
    belongs = lambda x, y : x >= 0 and x < len(area_map) and y >= 0 and y < len(area_map[0])

    return list(filter(
        lambda neighbour: belongs(neighbour[0], neighbour[1]),
        [
            (i + 1, j),
            (i - 1, j),
            (i, j + 1),
            (i, j - 1),
            (i + 1, j + 1),
            (i - 1, j + 1),
            (i + 1, j - 1),
            (i - 1, j - 1),
        ]
    ))
