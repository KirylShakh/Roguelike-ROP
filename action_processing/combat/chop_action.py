from action_processing.actions.action import Action
from game_messages import Message
from game_vars import color_vars
from action_processing.animations.chopped_body_part_animation import ChoppedBodyPartAnimation


class ChopAction(Action):
    def run(self):
        results = []
        results.append({'message': Message('Your heavy attack has chopped some limb off', color_vars.crit_message)})

        chop_animation = ChoppedBodyPartAnimation(self.engine, self.engine.entities.player)
        self.engine.animations.append(chop_animation)

        return results
