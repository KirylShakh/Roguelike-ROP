from action_processing.actions.action import Action
from game_states import GameStates
from game_vars import color_vars
from game_messages import Message
from action_processing.combat.cast_scroll_action import CastScrollAction
from combat.spells.fireball import Fireball


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
                            target_x=target_x, target_y=target_y, engine=self.engine)
        self.engine.player_turn_results.extend(item_use_results)
        self.engine.targeting_item = None

    def cast_fireball(self, target_x, target_y):
        action = CastScrollAction(self.engine)
        results = action.run(self.engine.entities.player, spell_class=Fireball, target_point=(target_x, target_y), caster_level=5)
        self.engine.player_turn_results.extend(results)
        self.engine.targeting_ability = None
