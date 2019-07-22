import tcod

class Renderer:
    def __init__(self, root, con):
        self.root = root
        self.con = con

    def render_all(self, entities, game_map, colors, fov_map, fov_recompute):
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

        for entity in entities:
            self.draw_entity(entity, fov_map)
        self.con.blit(self.root)

    def clear_all(self, entities):
        for entity in entities:
            self.clear_entity(entity)

    def draw_entity(self, entity, fov_map):
        if tcod.map_is_in_fov(fov_map, entity.x, entity.y):
            self.con.default_fg = entity.color
            self.con.put_char(entity.x, entity.y, entity.char, tcod.BKGND_NONE)

    def clear_entity(self, entity):
        self.con.put_char(entity.x, entity.y, tcod.event.K_SPACE, tcod.BKGND_NONE)
