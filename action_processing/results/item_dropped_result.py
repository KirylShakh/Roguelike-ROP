from action_processing.results.result import Result
from game_states import GameStates


class ItemDroppedResult(Result):
    def run(self, item):
        self.engine.entities.append(item)
        self.engine.game_state = GameStates.ENEMY_TURN
