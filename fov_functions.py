import tcod

from game_vars import fov_vars


def initialize_world_fov(world_map):
    fov_map = tcod.map.Map(world_map.width, world_map.height, order='F')

    for y in range(world_map.height):
        for x in range(world_map.width):
            fov_map.walkable[x][y] = True
            fov_map.transparent[x][y] = True

    return fov_map

def recompute_world_fov(fov_map, x, y):
    fov_map.compute_fov(x, y, fov_vars.world_radius, False, fov_vars.algorithm)

def initialize_fov(game_map):
    fov_map = tcod.map.Map(game_map.width, game_map.height, order='F')

    for y in range(game_map.height):
        for x in range(game_map.width):
            fov_map.walkable[x][y] = 'blocked' not in game_map.tiles[x][y].regulatory_flags
            fov_map.transparent[x][y] = 'block_sight' not in game_map.tiles[x][y].regulatory_flags

    return fov_map

def recompute_fov(fov_map, x, y, fov_radius=fov_vars.radius):
    fov_map.compute_fov(x, y, fov_radius, fov_vars.light_walls, fov_vars.algorithm)
