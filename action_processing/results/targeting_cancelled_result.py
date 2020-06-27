from action_processing.results.result import Result
from game_messages import Message


class TargetingCancelledResult(Result):
    def run(self):
        self.engine.game_state = self.engine.previous_game_state
        self.engine.message_log.add_message(Message('Targeting cancelled'))

        self.engine.targeting_item = None
        self.engine.targeting_ability = None

        self.engine.render_tick()
