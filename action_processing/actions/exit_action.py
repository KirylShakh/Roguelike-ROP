from action_processing.actions.action import Action
from game_states import GameStates
from player_locations import PlayerLocations
from game_vars import color_vars
from game_messages import Message
from fov_functions import initialize_fov, initialize_world_fov
from components.stairs import StairsDirections
from entity_objects.map_entities import MapEntities
from map_objects.world.biomes import Biomes


class ExitAction(Action):
    def run(self):
        if self.engine.player_location == PlayerLocations.WORLD_MAP:
            return self.exit_world_tile()
        elif self.engine.player_location == PlayerLocations.DUNGEON:
            return self.exit_dungeon_floor()

    def exit_world_tile(self):
        self.engine.message_log.add_message(Message('There is nowhere to climb here', color_vars.warning))
        return False

    def exit_dungeon_floor(self):
        if self.engine.game_state == GameStates.PLAYERS_TURN:
            player = self.engine.entities.player
            dungeon_map = self.engine.world_map.current_dungeon

            biom = self.engine.world_map.current_biom()
            if biom == Biomes.DUNGEON:
                for entity in self.engine.entities.all:
                    if entity.x == player.x and entity.y == player.y:
                        if entity.stairs and entity.stairs.direction == StairsDirections.UP:
                            self.engine.entities = dungeon_map.previous_floor(player, self.engine.message_log)
                            self.engine.fov_map = initialize_fov(dungeon_map)
                            self.engine.fov_recompute = True
                            self.engine.renderer.clear()
                            return True
                        elif entity.stairs and entity.stairs.direction == StairsDirections.WORLD:
                            self.return_to_world_map()
                            return True
                else:
                    self.engine.message_log.add_message(Message('There are no up stairs here', color_vars.warning))
            elif biom == Biomes.FOREST:
                self.return_to_world_map()
                return True

        return False

    def return_to_world_map(self):
        self.engine.player_location = PlayerLocations.WORLD_MAP
        self.engine.fov_map = initialize_world_fov(self.engine.world_map)
        self.engine.fov_recompute = True
        self.engine.renderer.clear()

        x, y = self.engine.world_map.current_dungeon_entry_point
        self.engine.entities.player.x = x
        self.engine.entities.player.y = y

        self.engine.world_map.current_dungeon = None
        self.engine.world_map.current_dungeon_entry_point = None

        self.engine.entities = MapEntities(self.engine.entities.player)
