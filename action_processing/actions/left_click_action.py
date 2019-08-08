from action_processing.actions.action import Action
from game_states import GameStates
from game_vars import item_vars, color_vars
from game_messages import Message
from action_processing.animations.explosion_animation import ExplosionAnimation


class LeftClickAction(Action):
    def run(self, left_click):
        if self.engine.game_state == GameStates.TARGETING:
            target_x, target_y = left_click

            if self.engine.targeting_item:
                self.use_item(target_x, target_y)
            elif self.engine.targeting_ability == 'cast_fireball':
                self.cast_fireball(target_x, target_y)

    def use_item(self, target_x, target_y):
        player = self.engine.entities.player

        item_use_results = player.inventory.use(self.engine.targeting_item,
                            entities=self.engine.entities, fov_map=self.engine.fov_map,
                            target_x=target_x, target_y=target_y, engine=self.engine)
        self.engine.player_turn_results.extend(item_use_results)
        self.engine.targeting_item = None

    def cast_fireball(self, target_x, target_y):
        if not self.engine.fov_map.fov[target_x][target_y]:
            self.engine.player_turn_results.append({'message': Message('You cannot target a tile outside your field of view', color_vars.warning)})
        else:
            radius = item_vars.fireball_scroll_radius
            damage = item_vars.fireball_scroll_damage

            self.engine.player_turn_results.append({'consumed': True, 'message': Message('The fireball explodes, burning everything within {0} tiles'.format(radius), color_vars.spell)})

            animation = ExplosionAnimation(self.engine, (target_x, target_y), radius, color_vars.fireball_explosion, damage)
            self.engine.animations.append(animation)

            self.engine.targeting_ability = None
