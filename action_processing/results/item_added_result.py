from action_processing.results.result import Result
from game_states import GameStates


class ItemAddedResult(Result):
    def run(self, item):
        self.engine.entities.remove(item)
        self.engine.game_state = GameStates.ENEMY_TURN
