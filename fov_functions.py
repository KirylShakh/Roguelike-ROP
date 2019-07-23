import tcod

def initialize_fov(game_map):
    fov_map = tcod.map.Map(game_map.width, game_map.height, order='F')

    for y in range(game_map.height):
        for x in range(game_map.width):
            fov_map.walkable[x][y] = not game_map.tiles[x][y].blocked
            fov_map.transparent[x][y] = not game_map.tiles[x][y].block_sight

    return fov_map

def recompute_fov(fov_map, x, y, radius, light_walls=True, algorithm=True):
    fov_map.compute_fov(x, y, radius, light_walls, algorithm)
