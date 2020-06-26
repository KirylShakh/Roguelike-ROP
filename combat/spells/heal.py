from random import randint

from combat.spells.spell import Spell, SpellTags

class Heal(Spell):
    def setup(self):
        self.name = 'heal'
        self.level = 1
        self.value_die = 8

        self.tags.extend([SpellTags.HEAL])

        self.cast_attribute = 'intelligence'
        self.affected_attribute = 'constitution'

        self.caster_level = min(self.level + 4, self.caster_level) # for now spell cannot be scaled more than 4 levels above
        self.heal_amount = self.inflicted_value()

    def heal_message(self, target):
        return 'A healing light runs along the body of {0} healing its {1} for {2} damage'.format(target.name,
                        self.affected_attribute, self.heal_amount)
