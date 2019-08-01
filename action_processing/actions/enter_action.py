from action_processing.actions.action import Action
from game_states import GameStates
from player_locations import PlayerLocations
from map_objects.game_map import GameMap
from game_vars import map_vars, room_vars, color_vars
from game_messages import Message
from fov_functions import initialize_fov


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
            if tile.biom == 'dungeon':
                game_map = GameMap(map_vars.width, map_vars.height)
                game_map.make_map(room_vars.max_num, room_vars.min_size,
                                    room_vars.max_size, self.engine.entities)
                self.engine.world_map.current_dungeon = game_map

                self.engine.renderer.clear()
                self.engine.enter_dungeon()
                return True
            else:
                self.engine.message_log.add_message(Message('There are no dungeons nearbye', color_vars.warning))
        return False

    def enter_next_floor(self):
        if self.engine.game_state == GameStates.PLAYERS_TURN:
            player = self.engine.entities.player
            dungeon_map = self.engine.world_map.current_dungeon
            for entity in self.engine.entities.all:
                if entity.stairs and entity.x == player.x and entity.y == player.y:
                    self.engine.entities = dungeon_map.next_floor(player, self.engine.message_log)
                    self.engine.fov_map = initialize_fov(dungeon_map)
                    self.engine.fov_recompute = True
                    self.engine.renderer.clear()
                    return True
            else:
                self.engine.message_log.add_message(Message('There are no stairs here', color_vars.warning))
        return False