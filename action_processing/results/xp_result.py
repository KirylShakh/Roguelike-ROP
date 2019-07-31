from action_processing.results.result import Result
from game_states import GameStates
from game_messages import Message
from game_vars import color_vars


class XpResult(Result):
    def run(self, xp):
        player = self.engine.entities.player
        leveled_up = player.level.add_xp(xp)
        self.engine.message_log.add_message(Message('You gain {0} experience points'.format(xp)))

        if leveled_up:
            self.engine.message_log.add_message(
                Message('Your battle skills grow stronger. You reached level {0}'.format(player.level.current_level),
                color_vars.warning)
            )
            self.engine.previous_game_state = self.engine.game_state
            self.engine.game_state = GameStates.LEVEL_UP
