import tcod

from game_vars import color_vars, screen_vars, panel_vars, menu_vars
from game_states import GameStates
from menus import inventory_menu, level_up_menu, character_screen


class Renderer:
    def __init__(self):
        self.screen_width = screen_vars.width
        self.screen_height = screen_vars.height

    def render_root(self):
        tcod.console_set_custom_font(screen_vars.font_img,
                            tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD)
        self.root = tcod.console_init_root(self.screen_width, self.screen_height,
                        screen_vars.title, False, tcod.RENDERER_SDL2, 'F', True)
        self.con = tcod.console.Console(self.screen_width, self.screen_height)
        self.panel = tcod.console.Console(self.screen_width, self.screen_height)

    def render_world(self, entities, world_map, fov_map, fov_recompute,
                    message_log, whats_under_mouse, game_state):
        if fov_recompute:
            for y in range(world_map.height):
                for x in range(world_map.width):
                    tile = world_map.tiles[x][y]
                    visible = fov_map.fov[x][y]

                    if visible:
                        tcod.console_set_char_background(self.con, x, y, tile.bg_color,
                                                            tcod.BKGND_SET)
                        self.con.default_fg = tile.color
                        tcod.console_put_char(self.con, x, y, tile.char, tcod.BKGND_NONE)
                        tile.explored = True
                    elif tile.explored:
                        tcod.console_set_char_background(self.con, x, y, tile.distant_bg_color,
                                                            tcod.BKGND_SET)
                        self.con.default_fg = tile.distant_color
                        tcod.console_put_char(self.con, x, y, tile.char, tcod.BKGND_NONE)

        entities_in_render_order = sorted(entities.all, key=lambda x: x.render_order.value)
        for entity in entities_in_render_order:
            visible = fov_map.fov[entity.x][entity.y]
            if visible:
                self.con.default_fg = entity.color
                tcod.console_put_char(self.con, entity.x, entity.y, entity.char, tcod.BKGND_NONE)

        self.con.blit(self.root)

        self.panel.default_bg = tcod.black
        self.panel.clear()
        self.render_hud(entities.player, None, message_log, whats_under_mouse)

        self.render_menus(entities.player, game_state)

    def render_all(self, entities, game_map, fov_map, fov_recompute,
                    message_log, entities_under_mouse, game_state):
        if fov_recompute:
            self.render_lit_map(game_map, fov_map)

        entities_in_render_order = sorted(entities.all, key=lambda x: x.render_order.value)
        for entity in entities_in_render_order:
            self.draw_entity(entity, fov_map, game_map)

        self.con.blit(self.root)

        self.panel.default_bg = tcod.black
        self.panel.clear()
        self.render_hud(entities.player, game_map, message_log, entities_under_mouse)

        self.render_menus(entities.player, game_state)

    def render_lit_map(self, game_map, fov_map):
        for y in range(game_map.height):
            for x in range(game_map.width):
                visible = fov_map.fov[x][y]
                wall = game_map.tiles[x][y].block_sight

                if visible:
                    if wall:
                        tcod.console_set_char_background(self.con, x, y, color_vars.light_wall,
                                                            tcod.BKGND_SET)
                    else:
                        tcod.console_set_char_background(self.con, x, y, color_vars.light_ground,
                                                            tcod.BKGND_SET)
                    game_map.tiles[x][y].explored = True
                elif game_map.tiles[x][y].explored:
                    if wall:
                        tcod.console_set_char_background(self.con, x, y, color_vars.dark_wall,
                                                            tcod.BKGND_SET)
                    else:
                        tcod.console_set_char_background(self.con, x, y, color_vars.dark_ground,
                                                            tcod.BKGND_SET)

    def render_hud(self, player, game_map, message_log, entities_under_mouse):
        # Print the game messages, one line at a time
        y = 1
        for message in message_log.messages:
            self.panel.default_fg = message.color
            tcod.console_print_ex(self.panel, message_log.x, y, tcod.BKGND_NONE, tcod.LEFT, message.text)
            y += 1

        self.render_bar(1, 1, 'HP', player.fighter.hp, player.fighter.max_hp,
                        tcod.light_red, tcod.darker_red)
        if game_map:
            tcod.console_print_ex(self.panel, 1, 3, tcod.BKGND_NONE, tcod.LEFT,
                                'Dungeon level: {0}'.format(game_map.dungeon_level))

        self.panel.default_fg = tcod.light_gray
        tcod.console_print_ex(self.panel, 1, 0, tcod.BKGND_NONE, tcod.LEFT, entities_under_mouse)

        self.panel.blit(self.root, 0, panel_vars.y, 0, 0, self.screen_width, panel_vars.height)

    def render_menus(self, player, game_state):
        if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
            if game_state == GameStates.SHOW_INVENTORY:
                inventory_title = menu_vars.inventory_show_title
            else:
                inventory_title = menu_vars.inventory_drop_title

            inventory_menu(inventory_title, menu_vars.inventory_width, player, self)
        elif game_state == GameStates.LEVEL_UP:
            level_up_menu(menu_vars.level_up_title, menu_vars.level_up_width, player, self)
        elif game_state == GameStates.CHARACTER_SCREEN:
            character_screen(player, menu_vars.character_screen_width,
                    menu_vars.character_screen_height, self)

    def clear_all(self, entities):
        for entity in entities.all:
            self.clear_entity(entity)

    def draw_entity(self, entity, fov_map, game_map):
        if fov_map.fov[entity.x][entity.y] or (entity.stairs and game_map.tiles[entity.x][entity.y].explored):
            self.con.default_fg = entity.color
            tcod.console_put_char(self.con, entity.x, entity.y, entity.char, tcod.BKGND_NONE)

    def clear_entity(self, entity):
        tcod.console_put_char(self.con, entity.x, entity.y, ' ', tcod.BKGND_NONE)

    def clear(self):
        self.con.clear()

    def render_bar(self, x, y, name, value, maximum, bar_color, back_color):
        panel = self.panel
        total_width = panel_vars.bar_width
        bar_width = int(float(value) / maximum * total_width)

        panel.default_bg = back_color
        tcod.console_rect(panel, x, y, total_width, 1, False, tcod.BKGND_SCREEN)
        panel.default_bg = bar_color
        if bar_width > 0:
            tcod.console_rect(panel, x, y, bar_width, 1, False, tcod.BKGND_SCREEN)

        panel.default_fg = tcod.white
        tcod.console_print_ex(panel, int(x + total_width / 2), y, tcod.BKGND_NONE, tcod.CENTER,
                                '{0}: {1}/{2}'.format(name, value, maximum))
