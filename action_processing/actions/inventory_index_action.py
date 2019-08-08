from action_processing.actions.action import Action
from game_states import GameStates


class InventoryIndexAction(Action):
    def run(self, inventory_index):
        player = self.engine.entities.player
        if (inventory_index is not None
                    and self.engine.previous_game_state != GameStates.PLAYER_DEAD
                    and inventory_index < len(player.inventory.items)):
            item = player.inventory.items[inventory_index]

            if self.engine.game_state == GameStates.SHOW_INVENTORY:
                self.engine.player_turn_results.extend(player.inventory.use(item,
                            entities=self.engine.entities, fov_map=self.engine.fov_map,
                            engine=self.engine))
            elif self.engine.game_state == GameStates.DROP_INVENTORY:
                self.engine.player_turn_results.extend(player.inventory.drop_item(item))
