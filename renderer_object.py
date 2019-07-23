import tcod

from enum import Enum

class RenderOrder(Enum):
    CORPSE = 1
    ITEM = 2
    ACTOR = 3

class Renderer:
    def __init__(self, root, con, screen_height):
        self.root = root
        self.con = con

        self.screen_height = screen_height

    def render_all(self, entities, player, game_map, colors, fov_map, fov_recompute):
        if fov_recompute:
            for y in range(game_map.height):
                for x in range(game_map.width):
                    visible = tcod.map_is_in_fov(fov_map, x, y)
                    wall = game_map.tiles[x][y].block_sight

                    if visible:
                        if wall:
                            tcod.console_set_char_background(self.con, x, y, colors.get('light_wall'), tcod.BKGND_SET)
                        else:
                            tcod.console_set_char_background(self.con, x, y, colors.get('light_ground'), tcod.BKGND_SET)
                        game_map.tiles[x][y].explored = True
                    elif game_map.tiles[x][y].explored:
                        if wall:
                            tcod.console_set_char_background(self.con, x, y, colors.get('dark_wall'), tcod.BKGND_SET)
                        else:
                            tcod.console_set_char_background(self.con, x, y, colors.get('dark_ground'), tcod.BKGND_SET)

        entities_in_render_order = sorted(entities, key=lambda x: x.render_order.value)
        for entity in entities_in_render_order:
            self.draw_entity(entity, fov_map)

        self.con.default_fg = tcod.white
        tcod.console_print_ex(self.con, 1, self.screen_height - 2, tcod.BKGND_NONE, tcod.LEFT,
                                'HP: {0:02}/{1:02}'.format(player.fighter.hp, player.fighter.max_hp))

        self.con.blit(self.root)

    def clear_all(self, entities):
        for entity in entities:
            self.clear_entity(entity)

    def draw_entity(self, entity, fov_map):
        if tcod.map_is_in_fov(fov_map, entity.x, entity.y):
            self.con.default_fg = entity.color
            tcod.console_put_char(self.con, entity.x, entity.y, entity.char, tcod.BKGND_NONE)

    def clear_entity(self, entity):
        tcod.console_put_char(self.con, entity.x, entity.y, ' ', tcod.BKGND_NONE)
