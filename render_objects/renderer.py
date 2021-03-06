import tcod

from game_vars import color_vars, screen_vars, panel_vars, menu_vars
from game_states import GameStates
from menus import inventory_menu, level_up_menu, character_screen, locations_menu, exploration_screen
from player_locations import PlayerLocations


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

    def render_all(self, engine):
        if engine.player_location == PlayerLocations.WORLD_MAP:
            self.render_world(engine.entities, engine.world_map,
                        engine.fov_map, 'fov_recompute' in engine.regulatory_flags,
                        engine.message_log, engine.whats_under_mouse, engine.game_state)
        elif engine.player_location == PlayerLocations.DUNGEON:
            self.render_dungeon(engine.entities, engine.world_map.current_dungeon,
                        engine.fov_map, 'fov_recompute' in engine.regulatory_flags,
                        engine.message_log, engine.whats_under_mouse, engine.game_state)

    def render_world(self, entities, world_map, fov_map, fov_recompute,
                    message_log, whats_under_mouse, game_state):
        if fov_recompute:
            for y in range(world_map.height):
                for x in range(world_map.width):
                    bg_color, char, fg_color = world_map.tile_render_info(x, y, fov_map.fov[x][y])

                    if bg_color:
                        tcod.console_set_char_background(self.con, x, y, bg_color, tcod.BKGND_SET)
                    if char and fg_color:
                        self.con.default_fg = fg_color
                        tcod.console_put_char(self.con, x, y, char, tcod.BKGND_NONE)

        entities_in_render_order = sorted(entities.all, key=lambda x: x.render_order.value)
        for entity in entities_in_render_order:
            visible = fov_map.fov[entity.x][entity.y]
            if visible:
                self.con.default_fg = entity.char.color
                tcod.console_put_char(self.con, entity.x, entity.y, entity.char.char, tcod.BKGND_NONE)

        self.con.blit(self.root)

        self.panel.default_bg = tcod.black
        self.panel.clear()
        self.render_hud(entities.player, None, message_log, whats_under_mouse)

        self.render_menus(entities.player, game_state, world_map=world_map)

    def render_dungeon(self, entities, game_map, fov_map, fov_recompute,
                    message_log, whats_under_mouse, game_state):
        if fov_recompute:
            self.render_lit_map(game_map, fov_map)

        entities_in_render_order = sorted(entities.all, key=lambda x: x.render_order.value)
        for entity in entities_in_render_order:
            self.draw_entity(entity, fov_map, game_map)

        self.con.blit(self.root)

        self.panel.default_bg = tcod.black
        self.panel.clear()
        self.render_hud(entities.player, game_map, message_log, whats_under_mouse)

        self.render_menus(entities.player, game_state)

    def render_lit_map(self, game_map, fov_map):
        for y in range(game_map.height):
            for x in range(game_map.width):
                bg_color, char, char_color = game_map.tile_render_info(x, y, fov_map.fov[x][y])
                if bg_color:
                    tcod.console_set_char_background(self.con, x, y, bg_color, tcod.BKGND_SET)
                if char and char_color:
                    self.con.default_fg = char_color
                    tcod.console_put_char(self.con, x, y, char, tcod.BKGND_NONE)

    def render_hud(self, player, game_map, message_log, entities_under_mouse):
        # Print the game messages, one line at a time
        y = 1
        for message in message_log.messages:
            self.panel.default_fg = message.color
            tcod.console_print_ex(self.panel, message_log.x, y, tcod.BKGND_NONE, tcod.LEFT, message.text)
            y += 1

        self.render_bar(1, 1, 'CON', player.constitution.value, player.constitution.base_value,
                        tcod.light_red, tcod.darker_red)
        if game_map:
            tcod.console_print_ex(self.panel, 1, 3, tcod.BKGND_NONE, tcod.LEFT,
                                'Dungeon level: {0}'.format(game_map.dungeon_level))

        self.panel.default_fg = tcod.light_gray
        tcod.console_print_ex(self.panel, 1, 0, tcod.BKGND_NONE, tcod.LEFT, entities_under_mouse)

        self.panel.blit(self.root, 0, panel_vars.y, 0, 0, self.screen_width, panel_vars.height)

    def render_menus(self, player, game_state, world_map=None):
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
        elif game_state == GameStates.SHOW_LOCATIONS:
            tile = world_map.tiles[player.x][player.y]
            locations_menu(menu_vars.location_list_title, menu_vars.location_list_width, tile.locations, self)
        elif game_state == GameStates.EXPLORATION_SCREEN:
            tile = world_map.tiles[player.x][player.y]
            dx, dy = world_map.potential_move
            exploration_screen(player, menu_vars.exploration_screen_width, menu_vars.exploration_screen_height,
                                world_map, (player.x + dx, player.y + dy), self)

    def clear_all(self, entities):
        for entity in entities.all:
            self.clear_entity(entity)

    def draw_entity(self, entity, fov_map, game_map):
        if fov_map.fov[entity.x][entity.y] or (hasattr(entity, 'stairs') and entity.stairs and 'explored' in game_map.tiles[entity.x][entity.y].regulatory_flags):
            self.con.default_fg = entity.char.color
            tcod.console_put_char(self.con, entity.x, entity.y, entity.char.char, tcod.BKGND_NONE)

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
