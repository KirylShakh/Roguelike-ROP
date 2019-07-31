from action_processing.actions.action import Action
from game_states import GameStates


class RightClickAction(Action):
    def run(self, right_click):
        if self.engine.game_state == GameStates.TARGETING:
            self.engine.player_turn_results.append({'targetting_cancelled': True})
