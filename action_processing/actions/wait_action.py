from action_processing.actions.action import Action
from game_states import GameStates


class WaitAction(Action):
    def run(self):
        self.engine.game_state = GameStates.ENEMY_TURN
