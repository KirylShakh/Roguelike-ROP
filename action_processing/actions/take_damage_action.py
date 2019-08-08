from action_processing.actions.action import Action


class TakeDamageAction(Action):
    def setup(self, target, damage):
        self.target = target
        self.damage = damage

    def run(self):
        return self.target.fighter.take_damage(self.damage)
