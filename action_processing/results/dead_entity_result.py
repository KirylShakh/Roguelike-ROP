from game_vars import color_vars
from game_messages import Message
from game_states import GameStates
from action_processing.results.result import Result
from action_processing.animations.dying_animation import DyingAnimation


class DeadEntityResult(Result):
    def run(self, dead_entity):
        player = self.engine.entities.player
        if dead_entity == player:
            player.char.char = '%'
            player.char.set_color(color_vars.blood)

            self.engine.game_state = GameStates.PLAYER_DEAD
            self.engine.message_log.add_message(Message('You died', color=color_vars.crit_message))
            self.engine.render_tick()
        else:
            dead_entity.blocks = False
            dead_entity.fighter = None
            dead_entity.ai = None

            animation = DyingAnimation(self.engine, dead_entity)
            self.engine.animations.append(animation)
