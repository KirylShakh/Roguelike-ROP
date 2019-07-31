from action_processing.results.result import Result
from game_states import GameStates


class ItemConsumedResult(Result):
    def run(self):
        self.engine.game_state = GameStates.ENEMY_TURN
