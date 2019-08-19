import tcod
import tcod.event

from game_vars import screen_vars, menu_vars
import event_handler
from render_objects.renderer import Renderer
from fov_functions import initialize_fov, recompute_fov, initialize_world_fov, recompute_world_fov
from game_states import GameStates
from loader_functions.initialize_new_game import get_game_variables
from loader_functions.data_loaders import load_game
from menus import main_menu, message_box
from player_locations import PlayerLocations

from action_processing.actions.animate_action import AnimateAction
from action_processing.actions.quit_action import QuitAction
from action_processing.actions.enter_action import EnterAction
from action_processing.actions.exit_action import ExitAction
from action_processing.actions.fullscreen_action import FullscreenAction
from action_processing.actions.info_screen_action import InfoScreenAction
from action_processing.actions.inventory_index_action import InventoryIndexAction
from action_processing.actions.level_up_action import LevelUpAction
from action_processing.actions.mouseover_action import MouseoverAction
from action_processing.actions.move_action import MoveAction
from action_processing.actions.pickup_action import PickupAction
from action_processing.actions.left_click_action import LeftClickAction
from action_processing.actions.right_click_action import RightClickAction
from action_processing.actions.return_to_world_map_action import ReturnToWorldMapAction
from action_processing.actions.wait_action import WaitAction
from action_processing.actions.world_action import WorldAction

from action_processing.actions.cast_fireball_action import CastFireballAction

from action_processing.results.dead_entity_result import DeadEntityResult
from action_processing.results.equip_result import EquipResult
from action_processing.results.item_added_result import ItemAddedResult
from action_processing.results.item_consumed_result import ItemConsumedResult
from action_processing.results.item_dropped_result import ItemDroppedResult
from action_processing.results.message_result import MessageResult
from action_processing.results.targeting_cancelled_result import TargetingCancelledResult
from action_processing.results.targeting_result import TargetingResult
from action_processing.results.xp_result import XpResult


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
        self.whats_under_mouse = ''

        self.animations = []

        self.targeting_ability = None

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
                if self.world_map.current_dungeon:
                    self.player_location = PlayerLocations.DUNGEON
                self.play_game()

                self.player_location = PlayerLocations.WORLD_MAP
                show_main_menu = True

    def play_game(self):
        if self.player_location == None:
            self.player_location = PlayerLocations.WORLD_MAP

        if self.player_location == PlayerLocations.WORLD_MAP:
            self.fov_recompute = True
            self.fov_map = initialize_world_fov(self.world_map)

            self.whats_under_mouse = ''
            self.previous_game_state = self.game_state
        elif self.player_location == PlayerLocations.DUNGEON:
            if self.enter_dungeon():
                return True

        while True:
            if self.fov_recompute:
                recompute_world_fov(self.fov_map, self.entities.player.x, self.entities.player.y)
            self.render_tick()

            for event in tcod.event.wait():
                self.player_turn_results = []
                processed_event = event_handler.handle(event, self.game_state)

                if processed_event.get('exit'):
                    action = QuitAction(self)
                    if action.run():
                        return True

                if processed_event.get('wait'):
                    action = WaitAction(self)
                    action.run()

                if processed_event.get('move'):
                    action = MoveAction(self)
                    action.run(processed_event.get('move'))

                if processed_event.get('show_inventory'):
                    action = InfoScreenAction(self)
                    action.run(GameStates.SHOW_INVENTORY)

                if processed_event.get('drop_inventory'):
                    action = InfoScreenAction(self)
                    action.run(GameStates.DROP_INVENTORY)

                if processed_event.get('show_character_screen'):
                    action = InfoScreenAction(self)
                    action.run(GameStates.CHARACTER_SCREEN)

                if processed_event.get('take_stairs_down'):
                    action = EnterAction(self)
                    if action.run():
                        return True
                    else:
                        break

                if processed_event.get('fullscreen'):
                    action = FullscreenAction(self)
                    action.run()

                if processed_event.get('mouseover'):
                    action = MouseoverAction(self)
                    self.whats_under_mouse = action.run(processed_event.get('mouseover'))

                if self.game_state == GameStates.ENEMY_TURN:
                    action = WorldAction(self)
                    action.run()

    def enter_dungeon(self):
        game_map = self.world_map.current_dungeon

        self.fov_recompute = True
        self.fov_map = initialize_fov(game_map)

        self.previous_game_state = self.game_state

        self.whats_under_mouse = ''
        player = self.entities.player
        self.player_location = PlayerLocations.DUNGEON

        while True:
            if self.player_location == PlayerLocations.WORLD_MAP:
                action = ReturnToWorldMapAction(self)
                action.run()
                return False

            exit_location = False

            if self.fov_recompute:
                recompute_fov(self.fov_map, player.x, player.y, self.world_map.current_dungeon.map_creator.fov_radius)
            self.render_tick()

            for event in tcod.event.wait():
                self.player_turn_results = []
                processed_event = event_handler.handle(event, self.game_state)

                if processed_event.get('exit'):
                    action = QuitAction(self)
                    if action.run():
                        return True

                if processed_event.get('wait'):
                    action = WaitAction(self)
                    action.run()

                if processed_event.get('move'):
                    action = MoveAction(self)
                    action.run(processed_event.get('move'))

                if processed_event.get('pickup'):
                    action = PickupAction(self)
                    action.run()

                if processed_event.get('show_inventory'):
                    action = InfoScreenAction(self)
                    action.run(GameStates.SHOW_INVENTORY)

                if processed_event.get('inventory_index') is not None:
                    action = InventoryIndexAction(self)
                    action.run(processed_event.get('inventory_index'))

                if processed_event.get('drop_inventory'):
                    action = InfoScreenAction(self)
                    action.run(GameStates.DROP_INVENTORY)

                if processed_event.get('show_character_screen'):
                    action = InfoScreenAction(self)
                    action.run(GameStates.CHARACTER_SCREEN)

                if processed_event.get('left_click'):
                    action = LeftClickAction(self)
                    action.run(processed_event.get('left_click'))

                if processed_event.get('right_click'):
                    action = LeftClickAction(self)
                    action.run(processed_event.get('right_click'))

                if processed_event.get('level_up'):
                    action = LevelUpAction(self)
                    action.run(processed_event.get('level_up'))

                if processed_event.get('take_stairs_down'):
                    action = EnterAction(self)
                    action.run()

                if processed_event.get('take_stairs_up'):
                    action = ExitAction(self)
                    action.run()

                if processed_event.get('fullscreen'):
                    action = FullscreenAction(self)
                    action.run()

                if processed_event.get('mouseover'):
                    action = MouseoverAction(self)
                    self.whats_under_mouse = action.run(processed_event.get('mouseover'))

                if processed_event.get('cast_fireball'):
                    action = CastFireballAction(self)
                    action.run()

                for player_turn_result in self.player_turn_results:
                    if player_turn_result.get('message'):
                        result = MessageResult(self)
                        result.run(player_turn_result.get('message'))

                    if player_turn_result.get('targeting_cancelled'):
                        result = TargetingCancelledResult(self)
                        result.run()

                    if player_turn_result.get('dead'):
                        result = DeadEntityResult(self)
                        result.run(player_turn_result.get('dead'))

                    if player_turn_result.get('item_added'):
                        result = ItemAddedResult(self)
                        result.run(player_turn_result.get('item_added'))

                    if player_turn_result.get('consumed'):
                        result = ItemConsumedResult(self)
                        result.run()

                    if player_turn_result.get('item_dropped'):
                        result = ItemDroppedResult(self)
                        result.run(player_turn_result.get('item_dropped'))

                    if player_turn_result.get('equip'):
                        result = EquipResult(self)
                        result.run(player_turn_result.get('equip'))

                    if player_turn_result.get('targeting'):
                        result = TargetingResult(self)
                        result.run(player_turn_result.get('targeting'))

                    if player_turn_result.get('xp'):
                        result = XpResult(self)
                        result.run(player_turn_result.get('xp'))

                    if player_turn_result.get('exit_location'):
                        exit_location = True

                if exit_location:
                    break

                if len(self.animations) > 0:
                    self.process_animations()

                if self.game_state == GameStates.ENEMY_TURN:
                    action = WorldAction(self)
                    action.run()

                if self.game_state == GameStates.ANIMATING:
                    self.process_animations()

    def render_tick(self):
        self.renderer.render_all(self)
        self.fov_recompute = False

        tcod.console_flush()
        self.renderer.clear_all(self.entities)

    def process_animations(self):
        action = AnimateAction(self)
        animate_results = action.run()

        for animate_result in animate_results:
            if animate_result.get('message'):
                result = MessageResult(self)
                result.run(animate_result.get('message'))

            if animate_result.get('dead'):
                result = DeadEntityResult(self)
                result.run(animate_result.get('dead'))

            if animate_result.get('xp'):
                result = XpResult(self)
                result.run(animate_result.get('xp'))

if __name__ == '__main__':
    engine = Engine()
    engine.main()
