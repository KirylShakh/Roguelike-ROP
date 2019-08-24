from action_processing.actions.action import Action
from game_states import GameStates
from game_messages import Message
from game_vars import message_vars


class CastFireballAction(Action):
    def run(self):
        self.engine.previous_game_state = GameStates.PLAYERS_TURN
        self.engine.game_state = GameStates.TARGETING
        self.engine.targeting_ability = 'cast_fireball'
        self.engine.player_turn_results.append({'message': Message(message_vars.fireball_target_message)})
