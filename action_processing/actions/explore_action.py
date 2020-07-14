from action_processing.actions.action import Action
from action_processing.actions.info_screen_action import InfoScreenAction
from game_states import GameStates
from player_locations import PlayerLocations


class ExploreAction(Action):
    def run(self):
        if self.engine.player_location != PlayerLocations.WORLD_MAP or self.engine.game_state != GameStates.PLAYERS_TURN:
            return

        player = self.engine.entities.player
        tile = self.engine.world_map.tiles[player.x][player.y]
        if not tile.locations:
            self.engine.world_map.make_locations(tile)

        action = InfoScreenAction(self.engine)
        action.run(GameStates.SHOW_LOCATIONS)
