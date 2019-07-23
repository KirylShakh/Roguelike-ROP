import tcod

from enum import Enum

class RenderOrder(Enum):
    CORPSE = 1
    ITEM = 2
    ACTOR = 3

def render_bar(panel, x, y, total_width, name, value, maximum, bar_color, back_color):
    bar_width = int(float(value) / maximum * total_width)

    panel.default_bg = back_color
    tcod.console_rect(panel, x, y, total_width, 1, False, tcod.BKGND_SCREEN)
    panel.default_bg = bar_color
    if bar_width > 0:
        tcod.console_rect(panel, x, y, bar_width, 1, False, tcod.BKGND_SCREEN)

    panel.default_fg = tcod.white
    tcod.console_print_ex(panel, int(x + total_width / 2), y, tcod.BKGND_NONE, tcod.CENTER,
                            '{0}: {1}/{2}'.format(name, value, maximum))

class Renderer:
    def __init__(self, root, con, screen_width, screen_height):
        self.root = root
        self.con = con

        self.screen_width = screen_width
        self.screen_height = screen_height

    def render_all(self, entities, player, game_map, colors, fov_map, fov_recompute,
                    panel, bar_width, panel_height, panel_y, message_log, entities_under_mouse):
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

        self.con.blit(self.root)

        panel.default_bg = tcod.black
        panel.clear()

        # Print the game messages, one line at a time
        y = 1
        for message in message_log.messages:
            panel.default_fg = message.color
            tcod.console_print_ex(panel, message_log.x, y, tcod.BKGND_NONE, tcod.LEFT, message.text)
            y += 1

        render_bar(panel, 1, 1, bar_width, 'HP', player.fighter.hp, player.fighter.max_hp,
                    tcod.light_red, tcod.darker_red)

        panel.default_fg = tcod.light_gray
        tcod.console_print_ex(panel, 1, 0, tcod.BKGND_NONE, tcod.LEFT, entities_under_mouse)

        panel.blit(self.root, 0, panel_y, 0, 0, self.screen_width, panel_height)

    def clear_all(self, entities):
        for entity in entities:
            self.clear_entity(entity)

    def draw_entity(self, entity, fov_map):
        if tcod.map_is_in_fov(fov_map, entity.x, entity.y):
            self.con.default_fg = entity.color
            tcod.console_put_char(self.con, entity.x, entity.y, entity.char, tcod.BKGND_NONE)

    def clear_entity(self, entity):
        tcod.console_put_char(self.con, entity.x, entity.y, ' ', tcod.BKGND_NONE)
