from action_processing.results.result import Result
from death_functions import kill_monster, kill_player


class DeadEntityResult(Result):
    def run(self, dead_entity):
        player = self.engine.entities.player
        if dead_entity == player:
            message, self.engine.game_state = kill_player(player)
        else:
            message = kill_monster(dead_entity)

        self.engine.message_log.add_message(message)
