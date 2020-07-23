from action_processing.actions.action import Action
from game_states import GameStates
from player_locations import PlayerLocations
from game_messages import Message
from map_objects.world.biomes import Biomes

from action_processing.actions.enter_action import EnterAction
from action_processing.results.dead_entity_result import DeadEntityResult
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
        if 'visited' not in tile.regulatory_flags:
            if tile.biom == Biomes.FOREST:
                self.engine.message_log.add_message(Message('You traverse empty lifeless silent forest'))
            elif tile.biom == Biomes.DUNGEON:
                self.engine.message_log.add_message(Message('There are bottomless ruins here'))
            if self.engine.world_map.is_encounter_present_in(tile):
                action = EnterAction(self.engine)
                action.run(encounter=True)
            tile.regulatory_flags.add('visited')
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
                        action = DeadEntityResult(self.engine)
                        action.run(dead_entity)

                        if self.engine.game_state == GameStates.PLAYER_DEAD:
                            break

                if self.engine.game_state == GameStates.PLAYER_DEAD:
                    break
        else:
            self.engine.game_state = GameStates.PLAYERS_TURN
