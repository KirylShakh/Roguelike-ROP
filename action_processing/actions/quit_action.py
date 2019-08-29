from action_processing.actions.action import Action
from game_states import GameStates
from loader_functions.data_loaders import save_game


class QuitAction(Action):
    def run(self):
        if self.engine.game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY, GameStates.CHARACTER_SCREEN, GameStates.SHOW_LOCATIONS):
            self.engine.game_state = self.engine.previous_game_state
        elif self.engine.game_state == GameStates.TARGETING:
            self.engine.player_turn_results.append({'targeting_cancelled': True})
        else:
            save_game(self.engine.entities, self.engine.world_map, self.engine.message_log,
                        self.engine.game_state)
            return True
        return False
