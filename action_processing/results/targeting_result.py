from action_processing.results.result import Result
from game_states import GameStates


class TargetingResult(Result):
    def run(self, targeting):
        self.engine.previous_game_state = GameStates.PLAYERS_TURN
        self.engine.game_state = GameStates.TARGETING

        self.engine.targeting_item = targeting

        self.engine.message_log.add_message(self.engine.targeting_item.item.targeting_message)
