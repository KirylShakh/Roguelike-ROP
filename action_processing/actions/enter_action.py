from action_processing.actions.action import Action
from game_states import GameStates
from player_locations import PlayerLocations
from map_objects.game_map import GameMap
from map_objects.map_components.dungeon import Dungeon
from map_objects.map_components.forest import Forest
from map_objects.world.biomes import Biomes
from game_vars import map_vars, room_vars, color_vars
from game_messages import Message
from fov_functions import initialize_fov
from components.stairs import StairsDirections


class EnterAction(Action):
    def run(self):
        if self.engine.player_location == PlayerLocations.WORLD_MAP:
            return self.enter_world_tile()
        elif self.engine.player_location == PlayerLocations.DUNGEON:
            return self.enter_next_floor()

    def enter_world_tile(self):
        if self.engine.game_state == GameStates.PLAYERS_TURN:
            player = self.engine.entities.player
            tile = self.engine.world_map.tiles[player.x][player.y]
            if tile.biom == Biomes.DUNGEON:
                map_creator = Dungeon(room_vars.max_num, room_vars.min_size, room_vars.max_size)
                return self.enter_location(map_creator)
            elif tile.biom == Biomes.FOREST:
                map_creator = Forest(5)
                return self.enter_location(map_creator)
            else:
                self.engine.message_log.add_message(Message('There is nowhere to enter here', color_vars.warning))
        return False

    def enter_location(self, map_creator):
        player = self.engine.entities.player
        self.engine.world_map.current_dungeon_entry_point = (player.x, player.y)

        game_map = GameMap(map_vars.width, map_vars.height, map_creator=map_creator)
        game_map.make_map(self.engine.entities)
        self.engine.world_map.current_dungeon = game_map

        self.engine.renderer.clear()
        return self.engine.enter_dungeon()

    def enter_next_floor(self):
        if self.engine.game_state == GameStates.PLAYERS_TURN:
            player = self.engine.entities.player
            dungeon_map = self.engine.world_map.current_dungeon
            for entity in self.engine.entities.all:
                if entity.x == player.x and entity.y == player.y:
                    if entity.stairs and entity.stairs.direction == StairsDirections.DOWN:
                        self.engine.entities = dungeon_map.next_floor(player, self.engine.message_log)
                        self.engine.fov_map = initialize_fov(dungeon_map)
                        self.engine.fov_recompute = True
                        self.engine.renderer.clear()

                        self.engine.player_turn_results.append({'exit_location': True})
                        return True
                    elif entity.stairs and entity.stairs.direction == StairsDirections.WORLD:
                        return False # implement
            else:
                self.engine.message_log.add_message(Message('There are no down stairs here', color_vars.warning))
        return False
