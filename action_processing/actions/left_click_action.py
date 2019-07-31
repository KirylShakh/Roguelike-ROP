from action_processing.actions.action import Action
from game_states import GameStates


class LeftClickAction(Action):
    def run(self, left_click):
        if self.engine.game_state == GameStates.TARGETING:
            target_x, target_y = left_click
            player = self.engine.entities.player

            item_use_results = player.inventory.use(self.engine.targeting_item,
                                entities=self.engine.entities, fov_map=self.engine.fov_map,
                                target_x=target_x, target_y=target_y)
            self.engine.player_turn_results.extend(item_use_results)
