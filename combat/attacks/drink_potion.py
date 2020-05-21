from game_messages import Message
from combat.spells.spell import SpellTags


class DrinkPotion:
    def __init__(self, target, spell):
        self.target = target
        self.spell = spell

    @property
    def affected_attribute(self):
        return self.target.attribute_by_name(self.spell.affected_attribute)

    def execute(self):
        results = [{'message': Message(self.drink_message())}]
        if SpellTags.HEAL in self.spell.tags:
            results.extend(self.apply_healing_effect())

        return results

    def apply_healing_effect(self):
        heal_amount = self.spell.heal_amount
        self.affected_attribute.heal(heal_amount)

        return self.log_healing_effect(heal_amount)

    def log_healing_effect(self, heal_amount):
        return [{'message': Message(self.spell.heal_message(self.target))}]

    def drink_message(self):
        return '{0} drink potion of "{1}"'.format(self.target.name.capitalize(), self.spell.name)
