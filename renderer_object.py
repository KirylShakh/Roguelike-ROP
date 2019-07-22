import tcod

class Renderer:
    def __init__(self, root, con):
        self.root = root
        self.con = con

    def render_all(self, entities, game_map, colors):
        for y in range(game_map.height):
            for x in range(game_map.width):
                wall = game_map.tiles[x][y].block_sight

                if wall:
                    tcod.console_set_char_background(self.con, x, y, colors.get('dark_wall'), tcod.BKGND_SET)
                else:
                    tcod.console_set_char_background(self.con, x, y, colors.get('dark_ground'), tcod.BKGND_SET)

        for entity in entities:
            self.draw_entity(entity)
        self.con.blit(self.root)

    def clear_all(self, entities):
        for entity in entities:
            self.clear_entity(entity)

    def draw_entity(self, entity):
        self.con.default_fg = entity.color
        self.con.put_char(entity.x, entity.y, entity.char, tcod.BKGND_NONE)

    def clear_entity(self, entity):
        self.con.put_char(entity.x, entity.y, tcod.event.K_SPACE, tcod.BKGND_NONE)
