import tcod
import tcod.event
from enum import Enum, auto

from game_vars import screen_vars, fov_vars, panel_vars, menu_vars, map_vars, room_vars
import event_handler
from render_objects.renderer import Renderer
from fov_functions import initialize_fov, recompute_fov, initialize_world_fov, recompute_world_fov
from game_states import GameStates
from death_functions import kill_monster, kill_player
from game_messages import Message
from loader_functions.initialize_new_game import get_game_variables
from loader_functions.data_loaders import load_game, save_game
from menus import main_menu, message_box
from map_objects.game_map import GameMap


class PlayerLocations(Enum):
    WORLD_MAP = auto()
    DUNGEON = auto()

class Engine:
    def __init__(self):
        self.renderer = Renderer()

        self.entities = None
        self.world_map = None
        self.message_log = None
        self.game_state = None
        self.player_location = None

        self.fov_map = None
        self.fov_recompute = False

        self.targeting_item = None
        self.player_turn_results = None

    def main(self):
        self.renderer.render_root()

        show_main_menu = True
        show_load_error_message = False

        main_menu_background_image = tcod.image_load(screen_vars.menu_background_img)

        while True:
            if show_main_menu:
                main_menu(main_menu_background_image, menu_vars.main_width, self.renderer)

                for event in tcod.event.wait():
                    if show_load_error_message:
                        message_box('No save game to load', 50, self.renderer)

                    tcod.console_flush()

                    action = event_handler.handle_main_menu(event)
                    new_game = action.get('new_game')
                    load_saved_game = action.get('load_saved_game')
                    exit_game = action.get('exit_game')

                    if show_load_error_message and (new_game or load_saved_game or exit_game):
                        show_load_error_message = False
                    elif new_game:
                        self.entities, self.world_map, self.message_log, self.game_state = get_game_variables()
                        show_main_menu = False
                        break
                    elif load_saved_game:
                        try:
                            self.entities, self.world_map, self.message_log, self.game_state = load_game()
                            show_main_menu = False
                            break
                        except FileNotFoundError:
                            show_load_error_message = True
                    elif exit_game:
                        raise SystemExit
            else:
                self.renderer.clear()
                if not self.world_map.current_dungeon:
                    self.play_game()
                else:
                    self.enter_dungeon()
                show_main_menu = True

    def play_game(self):
        self.fov_recompute = True
        self.fov_map = initialize_world_fov(self.world_map)

        player = self.entities.player
        whats_under_mouse = ''
        self.previous_game_state = self.game_state

        self.player_location = PlayerLocations.WORLD_MAP

        while True:
            if self.fov_recompute:
                recompute_world_fov(self.fov_map, player.x, player.y)
            self.renderer.render_world(self.entities, self.world_map, self.fov_map,
                                self.fov_recompute, self.message_log,
                                whats_under_mouse, self.game_state)
            self.fov_recompute = False

            tcod.console_flush()
            self.renderer.clear_all(self.entities)

            for event in tcod.event.wait():
                self.player_turn_results = []
                action = event_handler.handle(event, self.game_state)

                if action.get('exit'):
                    if self.exit_action():
                        return True

                if action.get('wait'):
                    self.wait_action()

                if action.get('move'):
                    self.move_action(action.get('move'))

                if action.get('show_inventory'):
                    self.switch_game_state(GameStates.SHOW_INVENTORY)

                if action.get('drop_inventory'):
                    self.switch_game_state(GameStates.DROP_INVENTORY)

                if action.get('show_character_screen'):
                    self.switch_game_state(GameStates.CHARACTER_SCREEN)

                if action.get('take_stairs_down'):
                    if self.take_stairs_down_action():
                        return True

                if action.get('fullscreen'):
                    self.fullscreen_action()

                if action.get('mouseover'):
                    whats_under_mouse = self.mouseover_action(action.get('mouseover'))

                if self.game_state == GameStates.ENEMY_TURN:
                    self.enemy_action()

    def enter_dungeon(self):
        game_map = self.world_map.current_dungeon

        self.fov_recompute = True
        self.fov_map = initialize_fov(game_map)

        self.previous_game_state = self.game_state

        entities_under_mouse = ''
        player = self.entities.player
        self.player_location = PlayerLocations.DUNGEON

        while True:
            if self.fov_recompute:
                recompute_fov(self.fov_map, player.x, player.y)
            self.renderer.render_all(self.entities, game_map, self.fov_map, self.fov_recompute,
                                self.message_log, entities_under_mouse, self.game_state)
            self.fov_recompute = False

            tcod.console_flush()
            self.renderer.clear_all(self.entities)

            for event in tcod.event.wait():
                self.player_turn_results = []

                action = event_handler.handle(event, self.game_state)
                if action.get('exit'):
                    if self.exit_action():
                        return True

                if action.get('wait'):
                    self.wait_action()

                if action.get('move'):
                    self.move_action(action.get('move'))

                if action.get('pickup'):
                    self.pickup_action(action.get('pickup'))

                if action.get('show_inventory'):
                    self.switch_game_state(GameStates.SHOW_INVENTORY)

                if action.get('inventory_index'):
                    self.inventory_index_action(action.get('inventory_index'))

                if action.get('drop_inventory'):
                    self.switch_game_state(GameStates.DROP_INVENTORY)

                if action.get('show_character_screen'):
                    self.switch_game_state(GameStates.CHARACTER_SCREEN)

                if action.get('left_click'):
                    self.left_click_action(action.get('left_click'))

                if action.get('right_click'):
                    self.right_click_action(action.get('right_click'))

                if action.get('take_stairs_down'):
                    if self.take_stairs_down_action():
                        break

                if action.get('level_up'):
                    self.level_up_action(action.get('level_up'))

                if action.get('fullscreen'):
                    self.fullscreen_action()

                if action.get('mouseover'):
                    entities_under_mouse = self.mouseover_action(action.get('mouseover'))

                for player_turn_result in self.player_turn_results:
                    if player_turn_result.get('message'):
                        self.message_result(player_turn_result.get('message'))

                    if player_turn_result.get('targeting_cancelled'):
                        self.targeting_cancelled_result()

                    if player_turn_result.get('dead'):
                        self.dead_entity_result(player_turn_result.get('dead'))

                    if player_turn_result.get('item_added'):
                        self.item_added_result(player_turn_result.get('item_added'))

                    if player_turn_result.get('consumed'):
                        self.item_consumed_result()

                    if player_turn_result.get('item_dropped'):
                        self.item_dropped_result(player_turn_result.get('item_dropped'))

                    if player_turn_result.get('equip'):
                        self.equip_result(player_turn_result.get('equip'))

                    if player_turn_result.get('targeting'):
                        self.targeting_result(player_turn_result.get('targeting'))

                    if player_turn_result.get('xp'):
                        self.xp_result(player_turn_result.get('xp'))

                if self.game_state == GameStates.ENEMY_TURN:
                        self.enemy_action()

    def switch_game_state(self, new_game_state):
        self.previous_game_state = self.game_state
        self.game_state = new_game_state

    def exit_action(self):
        if self.game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY, GameStates.CHARACTER_SCREEN):
            self.game_state = self.previous_game_state
        elif self.game_state == GameStates.TARGETING:
            self.player_turn_results.append({'targeting_cancelled': True})
        else:
            save_game(self.entities, self.world_map, self.message_log,
                        self.game_state)
            return True
        return False

    def wait_action(self):
        self.game_state = GameStates.ENEMY_TURN

    def move_action(self, move):
        if self.player_location == PlayerLocations.WORLD_MAP:
            self.move_on_world_map(move)
        elif self.player_location == PlayerLocations.DUNGEON:
            self.move_in_dungeon(move)

    def move_on_world_map(self, move):
        player = self.entities.player
        if self.game_state == GameStates.PLAYERS_TURN:
            dx, dy = move

            if not self.world_map.is_void(player.x + dx, player.y + dy):
                player.move(dx, dy)
                self.fov_recompute = True

                self.game_state = GameStates.ENEMY_TURN

    def move_in_dungeon(self, move):
        if self.game_state == GameStates.PLAYERS_TURN:
            player = self.entities.player
            game_map = self.world_map.current_dungeon

            dx, dy = move
            destination_x = player.x + dx
            destination_y = player.y + dy

            if not game_map.is_blocked(player.x + dx, player.y + dy):
                target = self.entities.get_blocking_at_location(destination_x, destination_y)

                if target:
                    attack_results = player.fighter.attack(target)
                    self.player_turn_results.extend(attack_results)
                else:
                    player.move(dx, dy)
                    self.fov_recompute = True

                self.game_state = GameStates.ENEMY_TURN

    def take_stairs_down_action(self):
        if self.player_location == PlayerLocations.WORLD_MAP:
            return self.enter_world_tile()
        elif self.player_location == PlayerLocations.DUNGEON:
            return self.enter_next_floor()

    def enter_world_tile(self):
        if self.game_state == GameStates.PLAYERS_TURN:
            player = self.entities.player
            tile = self.world_map.tiles[player.x][player.y]
            if tile.biom == 'dungeon':
                game_map = GameMap(map_vars.width, map_vars.height)
                game_map.make_map(room_vars.max_num, room_vars.min_size,
                                    room_vars.max_size, self.entities)
                self.world_map.current_dungeon = game_map

                self.renderer.clear()
                self.enter_dungeon()
                return True
            else:
                self.message_log.add_message(Message('There are no dungeons nearbye', tcod.yellow))
        return False

    def enter_next_floor(self):
        if self.game_state == GameStates.PLAYERS_TURN:
            player = self.entities.player
            dungeon_map = self.world_map.current_dungeon
            for entity in self.entities.all:
                if entity.stairs and entity.x == player.x and entity.y == player.y:
                    self.entities = dungeon_map.next_floor(player, self.message_log)
                    self.fov_map = initialize_fov(dungeon_map)
                    self.fov_recompute = True
                    self.renderer.clear()
                    return True
            else:
                self.message_log.add_message(Message('There are no stairs here', tcod.yellow))
        return False

    def pickup_action(self, pickup):
        if self.game_state == GameStates.PLAYERS_TURN:
            player = self.entities.player
            for entity in self.entities.all:
                if entity.item and entity.x == player.x and entity.y == player.y:
                    pickup_results = player.inventory.add_item(entity)
                    self.player_turn_results.extend(pickup_results)
                    break
            else:
                self.message_log.add_message(Message('There is nothing to pick up here', tcod.yellow))

    def inventory_index_action(self, inventory_index):
        player = self.entities.player
        if (inventory_index is not None
                    and self.previous_game_state != GameStates.PLAYER_DEAD
                    and inventory_index < len(player.inventory.items)):
            item = player.inventory.items[inventory_index]

            if self.game_state == GameStates.SHOW_INVENTORY:
                self.player_turn_results.extend(player.inventory.use(item,
                            entities=self.entities, fov_map=self.fov_map))
            elif self.game_state == GameStates.DROP_INVENTORY:
                self.player_turn_results.extend(player.inventory.drop_item(item))

    def level_up_action(self, level_up):
        player = self.entities.player
        if level_up == 'hp':
            player.fighter.base_max_hp += 20
            player.fighter.heal(20)
        elif level_up == 'str':
            player.fighter.base_power += 1
        elif level_up == 'def':
            player.fighter.base_defense += 1

        self.game_state = self.previous_game_state

    def fullscreen_action(self):
        tcod.console_set_fullscreen(not tcod.console_is_fullscreen())

    def left_click_action(self, left_click):
        if self.game_state == GameStates.TARGETING:
            target_x, target_y = left_click
            player = self.entities.player

            item_use_results = player.inventory.use(self.targeting_item, entities=self.entities,
                                fov_map=self.fov_map, target_x=target_x, target_y=target_y)
            self.player_turn_results.extend(item_use_results)

    def right_click_action(self, right_click):
        if self.game_state == GameStates.TARGETING:
            self.player_turn_results.append({'targetting_cancelled': True})

    def mouseover_action(self, mouseover_tile):
        if self.player_location == PlayerLocations.WORLD_MAP:
            (x, y) = (mouseover_tile.x, mouseover_tile.y)
            if not self.world_map.is_void(x, y) and self.fov_map.fov[x][y]:
                return self.world_map.tiles[x][y].biom.capitalize()
        elif self.player_location == PlayerLocations.DUNGEON:
            (x, y) = (mouseover_tile.x, mouseover_tile.y)
            entities_under_mouse = [entity.name for entity in self.entities.all
                        if entity.x == x and entity.y == y and self.fov_map.fov[entity.x][entity.y]]
            return ', '.join(entities_under_mouse).capitalize()

    def enemy_action(self):
        if self.player_location == PlayerLocations.WORLD_MAP:
            self.enemy_action_on_world_map()
        elif self.player_location == PlayerLocations.DUNGEON:
            self.enemy_action_in_dungeon()

    def enemy_action_on_world_map(self):
        player = self.entities.player
        tile = self.world_map.tiles[player.x][player.y]
        if not tile.visited:
            if tile.biom == 'forest':
                self.message_log.add_message(Message('You traverse empty lifeless silent forest'))
            elif tile.biom == 'dungeon':
                self.message_log.add_message(Message('There are bottomless ruins here'))
            tile.visited = True
        self.game_state = GameStates.PLAYERS_TURN

    def enemy_action_in_dungeon(self):
        player = self.entities.player

        for entity in self.entities.all:
            if entity.ai:
                enemy_turn_results = entity.ai.take_turn(player, self.fov_map,
                                                self.world_map.current_dungeon, self.entities)
                for enemy_turn_result in enemy_turn_results:
                    message = enemy_turn_result.get('message')
                    dead_entity = enemy_turn_result.get('dead')

                    if message:
                        self.message_log.add_message(message)

                    if dead_entity:
                        if dead_entity == player:
                            message, self.game_state = kill_player(player)
                        else:
                            message = kill_monster(dead_entity)

                        self.message_log.add_message(message)

                        if self.game_state == GameStates.PLAYER_DEAD:
                            break

                if self.game_state == GameStates.PLAYER_DEAD:
                    break
        else:
            self.game_state = GameStates.PLAYERS_TURN

    def message_result(self, message):
        self.message_log.add_message(message)

    def targeting_cancelled_result(self):
        self.game_state = self.previous_game_state
        self.message_log.add_message(Message('Targeting cancelled'))

    def dead_entity_result(self, dead_entity):
        player = self.entities.player
        if dead_entity == player:
            message, self.game_state = kill_player(player)
        else:
            message = kill_monster(dead_entity)

        self.message_log.add_message(message)

    def item_added_result(self, item):
        self.entities.remove(item)
        self.game_state = GameStates.ENEMY_TURN

    def item_consumed_result(self):
        self.game_state = GameStates.ENEMY_TURN

    def item_dropped_result(self, item):
        self.entities.append(item)
        self.game_state = GameStates.ENEMY_TURN

    def equip_result(self, item):
        player = self.entities.player
        equip_results = player.equipment.toggle_equip(item)

        for equip_result in equip_results:
            equipped = equip_result.get('equipped')
            if equipped:
                self.message_log.add_message(Message('You equipped the {0}'.format(equipped.name)))

            dequipped = equip_result.get('dequipped')
            if dequipped:
                self.message_log.add_message(Message('You dequipped the {0}'.format(dequipped.name)))

        self.game_state = GameStates.ENEMY_TURN

    def targeting_result(self, targeting):
        self.previous_game_state = GameStates.PLAYERS_TURN
        self.game_state = GameStates.TARGETING

        self.targeting_item = targeting

        self.message_log.add_message(self.targeting_item.item.targeting_message)

    def xp_result(self, xp):
        player = self.entities.player
        leveled_up = player.level.add_xp(xp)
        self.message_log.add_message(Message('You gain {0} experience points'.format(xp)))

        if leveled_up:
            self.message_log.add_message(
                Message('Your battle skills grow stronger. You reached level {0}'.format(player.level.current_level),
                tcod.yellow)
            )
            self.previous_game_state = self.game_state
            self.game_state = GameStates.LEVEL_UP

if __name__ == '__main__':
    engine = Engine()
    engine.main()
