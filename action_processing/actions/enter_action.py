from action_processing.actions.action import Action
from game_states import GameStates
from player_locations import PlayerLocations
from map_objects.game_map import GameMap
from map_objects.biomes.dungeon.dungeon_map import DungeonMap
from map_objects.biomes.forest.forest_map import ForestMap
from map_objects.world.biomes import Biomes
from game_vars import map_vars, room_vars, color_vars
from game_messages import Message
from fov_functions import initialize_fov
from components.stairs import StairsDirections


class EnterAction(Action):
    def run(self, location_index=None):
        # maybe change that in future so someone can sent player into another location on its turn
        if self.engine.game_state != GameStates.PLAYERS_TURN:
            return

        if self.engine.player_location == PlayerLocations.WORLD_MAP and location_index is not None:
            self.enter_location(location_index)
        elif self.engine.player_location == PlayerLocations.WORLD_MAP:
            self.enter_world_tile()
        elif self.engine.player_location == PlayerLocations.DUNGEON:
            self.enter_next_floor()

    def enter_world_tile(self):
        player = self.engine.entities.player
        tile = self.engine.world_map.tiles[player.x][player.y]
        if tile.biom == Biomes.DUNGEON:
            map_creator = DungeonMap(room_vars.max_num, room_vars.min_size, room_vars.max_size)
            self.enter_nameless_location(map_creator)
        elif tile.biom == Biomes.FOREST:
            map_creator = ForestMap(5)
            self.enter_nameless_location(map_creator)
        else:
            self.engine.message_log.add_message(Message('There is nowhere to enter here', color_vars.warning))

    def enter_location(self, location_index):
        player = self.engine.entities.player
        self.engine.world_map.current_dungeon_entry_point = (player.x, player.y)

        locations = self.engine.world_map.tiles[player.x][player.y].locations
        if location_index < 0 or location_index >= len(locations):
            return
        game_map = locations[location_index]
        game_map.make_map(self.engine.entities)
        self.engine.world_map.current_dungeon = game_map
        self.engine.player_location = PlayerLocations.DUNGEON
        self.engine.player_turn_results.append({'change_location': True})

    def enter_nameless_location(self, map_creator):
        player = self.engine.entities.player
        self.engine.world_map.current_dungeon_entry_point = (player.x, player.y)

        game_map = GameMap(map_vars.width, map_vars.height, map_creator=map_creator)
        game_map.make_map(self.engine.entities)
        self.engine.world_map.current_dungeon = game_map
        self.engine.player_location = PlayerLocations.DUNGEON
        self.engine.player_turn_results.append({'change_location': True})

    def enter_next_floor(self):
        player = self.engine.entities.player
        dungeon_map = self.engine.world_map.current_dungeon
        for entity in self.engine.entities.all:
            if entity.x == player.x and entity.y == player.y:
                if entity.stairs and entity.stairs.direction == StairsDirections.DOWN:
                    self.engine.entities = dungeon_map.next_floor(player, self.engine.message_log)
                    self.engine.player_turn_results.append({'change_location': True})
                elif entity.stairs and entity.stairs.direction == StairsDirections.WORLD:
                    return # implement - not sure what situations there could be to allow this yet
        else:
            self.engine.message_log.add_message(Message('There are no down stairs here', color_vars.warning))
