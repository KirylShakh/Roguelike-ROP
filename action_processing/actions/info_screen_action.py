from action_processing.actions.action import Action
from game_states import GameStates


class InfoScreenAction(Action):
    def run(self, new_game_state):
        self.engine.previous_game_state = self.engine.game_state
        self.engine.game_state = new_game_state
