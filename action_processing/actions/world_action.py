from action_processing.actions.action import Action
from game_states import GameStates
from player_locations import PlayerLocations
from game_messages import Message
from death_functions import kill_monster, kill_player
from map_objects.world.biomes import Biomes

from action_processing.animations.charge_animation import ChargeAnimation


class WorldAction(Action):
    def run(self):
        if self.engine.player_location == PlayerLocations.WORLD_MAP:
            self.enemy_action_on_world_map()
        elif self.engine.player_location == PlayerLocations.DUNGEON:
            self.enemy_action_in_dungeon()

    def enemy_action_on_world_map(self):
        player = self.engine.entities.player
        tile = self.engine.world_map.tiles[player.x][player.y]
        if not tile.visited:
            if tile.biom == Biomes.FOREST:
                self.engine.message_log.add_message(Message('You traverse empty lifeless silent forest'))
            elif tile.biom == Biomes.DUNGEON:
                self.engine.message_log.add_message(Message('There are bottomless ruins here'))
            tile.visited = True
        self.engine.game_state = GameStates.PLAYERS_TURN

    def enemy_action_in_dungeon(self):
        player = self.engine.entities.player

        for entity in self.engine.entities.all:
            if entity.ai:
                enemy_turn_results = entity.ai.take_turn(player, self.engine.fov_map,
                                                self.engine.world_map.current_dungeon,
                                                self.engine.entities)
                for enemy_turn_result in enemy_turn_results:
                    message = enemy_turn_result.get('message')
                    dead_entity = enemy_turn_result.get('dead')

                    if message:
                        self.engine.message_log.add_message(message)

                    charge = enemy_turn_result.get('charge')
                    if charge:
                        animation = ChargeAnimation(self.engine, entity, charge, player)
                        self.engine.animations.append(animation)

                    if dead_entity:
                        if dead_entity == player:
                            message, self.engine.game_state = kill_player(player)
                        else:
                            message = kill_monster(dead_entity)

                        self.engine.message_log.add_message(message)

                        if self.engine.game_state == GameStates.PLAYER_DEAD:
                            self.play_animations_for_dead_player()
                            break

                if self.engine.game_state == GameStates.PLAYER_DEAD:
                    self.play_animations_for_dead_player()
                    break
        else:
            if self.need_play_animations():
                self.engine.game_state = GameStates.ANIMATING
                self.engine.previous_game_state = GameStates.PLAYERS_TURN
            else:
                self.engine.game_state = GameStates.PLAYERS_TURN

    def need_play_animations(self):
        return len(self.engine.animations) > 0

    def play_animations_for_dead_player(self):
        if self.need_play_animations():
            self.engine.game_state = GameStates.ANIMATING
            self.engine.previous_game_state = GameStates.PLAYER_DEAD
