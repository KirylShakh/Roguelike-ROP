from random import randint

from combat.spells.spell import Spell, SpellTags
from action_processing.animations.lightning_animation import LightningAnimation

class LightningBolt(Spell):
    def setup(self):
        self.name = 'lightning bolt'
        self.level = 1
        self.value_die = 6
        self.maximum_range = 5

        self.tags |= {SpellTags.DAMAGE, SpellTags.ELEMENTAL, SpellTags.ELECTRICITY, SpellTags.AUTO_TARGET}

        self.cast_attribute = 'intelligence'
        self.damage_attribute = 'constitution'

        self.caster_level = min(self.level + 4, self.caster_level) # for now spell cannot be scaled more than 4 levels above
        self.damage = self.inflicted_value()

    def harm_message(self, target):
        return 'A lightning bolt strikes the {0} with a loud thunder for {1} damage'.format(target.name, self.damage)

    def animation_class(self):
        return LightningAnimation
