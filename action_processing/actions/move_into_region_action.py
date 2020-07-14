from action_processing.actions.action import Action
from player_locations import PlayerLocations


class MoveIntoRegionAction(Action):
    def run(self):
        if self.engine.player_location == PlayerLocations.WORLD_MAP:
            player = self.engine.entities.player
            dx, dy = self.engine.world_map.potential_move
            player.move(dx, dy)
            self.engine.regulatory_flags.add('fov_recompute')

            self.engine.game_state = self.engine.previous_game_state
