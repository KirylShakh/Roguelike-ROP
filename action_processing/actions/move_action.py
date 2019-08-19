from action_processing.actions.action import Action
from game_states import GameStates
from player_locations import PlayerLocations
from map_objects.world.biomes import Biomes


class MoveAction(Action):
    def run(self, move):
        if self.engine.player_location == PlayerLocations.WORLD_MAP:
            self.move_on_world_map(move)
        elif self.engine.player_location == PlayerLocations.DUNGEON:
            self.move_in_dungeon(move)

    def move_on_world_map(self, move):
        player = self.engine.entities.player
        if self.engine.game_state == GameStates.PLAYERS_TURN:
            dx, dy = move

            if not self.engine.world_map.is_void(player.x + dx, player.y + dy):
                player.move(dx, dy)
                self.engine.fov_recompute = True

                self.engine.game_state = GameStates.ENEMY_TURN

    def move_in_dungeon(self, move):
        if self.engine.game_state == GameStates.PLAYERS_TURN:
            player = self.engine.entities.player
            game_map = self.engine.world_map.current_dungeon

            dx, dy = move
            destination_x = player.x + dx
            destination_y = player.y + dy

            if not game_map.is_void(destination_x, destination_y) and not game_map.is_blocked(destination_x, destination_y):
                target = self.engine.entities.get_blocking_at_location(destination_x, destination_y)

                if target:
                    attack_results = player.fighter.attack(target)
                    self.engine.player_turn_results.extend(attack_results)
                else:
                    player.move(dx, dy)
                    self.engine.fov_recompute = True

                self.engine.game_state = GameStates.ENEMY_TURN
            elif game_map.is_void(destination_x, destination_y):
                biom = self.engine.world_map.current_biom()
                if biom == Biomes.FOREST:
                    self.engine.player_location = PlayerLocations.WORLD_MAP
                    self.engine.player_turn_results.append({'exit_location': True})
