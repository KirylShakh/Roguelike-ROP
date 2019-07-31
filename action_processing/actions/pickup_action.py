from action_processing.actions.action import Action
from game_states import GameStates
from game_vars import color_vars
from game_messages import Message


class PickupAction(Action):
    def run(self):
        if self.engine.game_state == GameStates.PLAYERS_TURN:
            player = self.engine.entities.player
            for entity in self.engine.entities.all:
                if entity.item and entity.x == player.x and entity.y == player.y:
                    pickup_results = player.inventory.add_item(entity)
                    self.engine.player_turn_results.extend(pickup_results)
                    break
            else:
                self.engine.message_log.add_message(Message('There is nothing to pick up here',
                                                    color_vars.warning))
