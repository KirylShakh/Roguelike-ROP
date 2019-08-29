from random import randint

from action_processing.actions.action import Action
from game_states import GameStates
from player_locations import PlayerLocations
from game_messages import Message
from map_objects.world.biomes import Biomes
from map_objects.biomes.forest.forest_locations import ForestLocations
from map_objects.biomes.dungeon.dungeon_locations import DungeonLocations


class ExploreAction(Action):
    def run(self):
        if self.engine.player_location != PlayerLocations.WORLD_MAP or self.engine.game_state != GameStates.PLAYERS_TURN:
            return False

        player = self.engine.entities.player
        tile = self.engine.world_map.tiles[player.x][player.y]
        if tile.locations:
            return True

        number_of_locations = randint(1, 5)
        tile.locations = []

        biom_location_creator = self.choose_creator_for_biom(tile.biom)
        for _ in range(number_of_locations):
            location = biom_location_creator.generate_location()
            tile.locations.append(location)

        return True

    def choose_creator_for_biom(self, biom):
        if biom == Biomes.FOREST:
            return ForestLocations()
        elif biom == Biomes.DUNGEON:
            return DungeonLocations()
        return None
