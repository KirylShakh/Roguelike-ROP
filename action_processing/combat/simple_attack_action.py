from action_processing.actions.action import Action
from game_messages import Message
from game_vars import color_vars
from action_processing.animations.chopped_body_part_animation import ChoppedBodyPartAnimation


class SimpleAttackAction(Action):
    def run(self, target):
        results = self.engine.entities.player.fighter.attack(target)
        for result in results:
            if result.get('heavy_damage_attack'):
                if result.get('chop_attack'):
                    results.append({'message': Message('Your heavy attack has chopped some limb off', color_vars.crit_message)})

                    chop_animation = ChoppedBodyPartAnimation(self.engine, target)
                    self.engine.animations.append(chop_animation)

        return results
