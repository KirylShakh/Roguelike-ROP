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
from action_processing.actions.explore_action import ExploreAction
from action_processing.actions.fullscreen_action import FullscreenAction
from action_processing.actions.info_screen_action import InfoScreenAction
from action_processing.actions.inventory_index_action import InventoryIndexAction
from action_processing.actions.level_up_action import LevelUpAction
from action_processing.actions.mouseover_action import MouseoverAction
from action_processing.actions.move_action import MoveAction
from action_processing.actions.pickup_action import PickupAction
from action_processing.actions.left_click_action import LeftClickAction
from action_processing.actions.right_click_action import RightClickAction
from action_processing.actions.setup_new_location_action import SetupNewLocationAction
from action_processing.actions.wait_action import WaitAction
from action_processing.actions.world_action import WorldAction

from action_processing.actions.cast_fireball_action import CastFireballAction
from action_processing.combat.chop_action import ChopAction

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

        self.targeting_item = None
        self.player_turn_results = None
        self.whats_under_mouse = ''

        self.animations = []

        self.targeting_ability = None # temp property for casting fireball

    def main(self):
        self.renderer.render_root()

        show_main_menu = True
        show_load_error_message = False

        main_menu_background_image = tcod.image_load(screen_vars.menu_background_img)

        while True:
            if show_main_menu:
                main_menu(main_menu_background_image, menu_vars.main_width, self.renderer)

                for raw_event in tcod.event.wait():
                    if show_load_error_message:
                        message_box('No save game to load', 50, self.renderer)

                    tcod.console_flush()

                    event = event_handler.handle_main_menu(raw_event)
                    new_game = event.get('new_game')
                    load_saved_game = event.get('load_saved_game')
                    exit_game = event.get('exit_game')

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
        self.regulatory_flags = set()
        self.setup_game_map()

        turn_count = 0
        while self.game_state != GameStates.EXIT:
            self.run_turn()
            if self.game_state != GameStates.EXIT:
                turn_count += 1
        print("Turns passed {0}".format(turn_count))

    def setup_game_map(self):
        if self.player_location == None:
            self.player_location = PlayerLocations.WORLD_MAP

        self.regulatory_flags.add('fov_recompute')
        self.whats_under_mouse = ''
        self.previous_game_state = self.game_state

        if self.player_location == PlayerLocations.WORLD_MAP:
            self.fov_map = initialize_world_fov(self.world_map)
        elif self.player_location == PlayerLocations.DUNGEON:
            self.fov_map = initialize_fov(self.world_map.current_dungeon)

    def render_tick(self):
        if 'fov_recompute' in self.regulatory_flags:
            if self.player_location == PlayerLocations.WORLD_MAP:
                recompute_world_fov(self.fov_map, self.entities.player.x, self.entities.player.y)
            elif self.player_location == PlayerLocations.DUNGEON:
                recompute_fov(self.fov_map, self.entities.player.x, self.entities.player.y,
                                self.world_map.current_dungeon.map_creator.fov_radius)

        self.renderer.render_all(self)
        self.regulatory_flags.discard('fov_recompute')

        tcod.console_flush()
        self.renderer.clear_all(self.entities)

    def run_turn(self):
        self.on_turn_start()
        self.run_player_turn()
        self.run_world_turn()
        self.on_turn_end()

    def on_turn_start(self):
        self.render_tick()

        if self.player_location == PlayerLocations.DUNGEON:
            self.entities.on_turn_start()

    def run_player_turn(self):
        while self.game_state != GameStates.ENEMY_TURN and self.game_state != GameStates.EXIT:
            for raw_event in tcod.event.wait():
                event = event_handler.handle(raw_event, self.game_state)
                self.player_turn_results = []

                if event.get('exit'):
                    action = QuitAction(self)
                    action.run()

                if event.get('wait'):
                    action = WaitAction(self)
                    action.run()

                if event.get('move'):
                    action = MoveAction(self)
                    action.run(event.get('move'))

                if event.get('show_inventory'):
                    action = InfoScreenAction(self)
                    action.run(GameStates.SHOW_INVENTORY)

                if event.get('drop_inventory'):
                    action = InfoScreenAction(self)
                    action.run(GameStates.DROP_INVENTORY)

                if event.get('show_character_screen'):
                    action = InfoScreenAction(self)
                    action.run(GameStates.CHARACTER_SCREEN)

                if event.get('take_stairs_down'):
                    action = EnterAction(self)
                    action.run()

                if event.get('fullscreen'):
                    action = FullscreenAction(self)
                    action.run()

                if event.get('mouseover'):
                    action = MouseoverAction(self)
                    action.run(event.get('mouseover'))

                if event.get('level_up'):
                    action = LevelUpAction(self)
                    action.run(event.get('level_up'))

                if self.player_location == PlayerLocations.WORLD_MAP:
                    if event.get('explore'):
                        action = ExploreAction(self)
                        action.run()

                    if event.get('location_index') is not None:
                        action = EnterAction(self)
                        action.run(event.get('location_index'))

                if self.player_location == PlayerLocations.DUNGEON:
                    if event.get('pickup'):
                        action = PickupAction(self)
                        action.run()

                    if event.get('inventory_index') is not None:
                        action = InventoryIndexAction(self)
                        action.run(event.get('inventory_index'))

                    if event.get('left_click'):
                        action = LeftClickAction(self)
                        action.run(event.get('left_click'))

                    if event.get('right_click'):
                        action = RightClickAction(self)
                        action.run(event.get('right_click'))

                    if event.get('take_stairs_up'):
                        action = ExitAction(self)
                        action.run()

                    if event.get('cast_fireball'):
                        action = CastFireballAction(self)
                        action.run()

                    if event.get('chop_attack'):
                        action = ChopAction(self)
                        self.player_turn_results.extend(action.run())

                for player_turn_result in self.player_turn_results:
                    if player_turn_result.get('message'):
                        result = MessageResult(self)
                        result.run(player_turn_result.get('message'))

                    if player_turn_result.get('equip'):
                        result = EquipResult(self)
                        result.run(player_turn_result.get('equip'))

                    if player_turn_result.get('dead'):
                        result = DeadEntityResult(self)
                        result.run(player_turn_result.get('dead'))

                    if player_turn_result.get('xp'):
                        result = XpResult(self)
                        result.run(player_turn_result.get('xp'))

                    if self.player_location == PlayerLocations.DUNGEON:
                        if player_turn_result.get('targeting_cancelled'):
                            result = TargetingCancelledResult(self)
                            result.run()

                        if player_turn_result.get('item_added'):
                            result = ItemAddedResult(self)
                            result.run(player_turn_result.get('item_added'))

                        if player_turn_result.get('consumed'):
                            result = ItemConsumedResult(self)
                            result.run()

                        if player_turn_result.get('item_dropped'):
                            result = ItemDroppedResult(self)
                            result.run(player_turn_result.get('item_dropped'))

                        if player_turn_result.get('targeting'):
                            result = TargetingResult(self)
                            result.run(player_turn_result.get('targeting'))

                if len(self.animations) > 0:
                    self.process_animations()

                if 'change_location' in self.regulatory_flags:
                    action = SetupNewLocationAction(self)
                    action.run()

                if self.game_state == GameStates.ENEMY_TURN or self.game_state == GameStates.EXIT:
                    break

    def run_world_turn(self):
        if self.game_state == GameStates.EXIT:
            return

        action = WorldAction(self)
        action.run()

        if len(self.animations) > 0:
            self.process_animations()

    def on_turn_end(self):
        if self.game_state == GameStates.EXIT:
            return

        if self.player_location == PlayerLocations.DUNGEON:
            self.entities.on_turn_end()

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
