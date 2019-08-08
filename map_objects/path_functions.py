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

def path_by_distance(src_x, src_y, dst_x, dst_y):
    path = []
    x = src_x
    y = src_y
    while True:
        neighbours = [(x + 1, y), (x + 1, y + 1), (x, y + 1), (x - 1, y + 1),
                    (x - 1, y), (x - 1, y - 1), (x, y - 1), (x + 1, y -1)]

        min_distance_sq = (x - dst_x) ** 2 + (y - dst_y) ** 2
        next_point = (x, y)
        for dx, dy in neighbours:
            distance_sq = (dx - dst_x) ** 2 + (dy - dst_y) ** 2
            if distance_sq < min_distance_sq:
                min_distance_sq = distance_sq
                next_point = (dx, dy)

        x, y = next_point
        if x == dst_x and y == dst_y:
            break
        path.append(next_point)

    return path

def mult(i, sign, multiplier):
    if i != 0:
        i += sign * multiplier
        if abs(i) >= 1:
            i -= sign
    else:
        i += sign * multiplier
    return i
