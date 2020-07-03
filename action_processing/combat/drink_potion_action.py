from action_processing.actions.action import Action
from combat.spells.spell import SpellTags
from game_messages import Message
from combat.attacks.drink_potion import DrinkPotion
from game_vars import color_vars


class DrinkPotionAction(Action):
    def run(self, actor, spell_class=None, caster_level=None):
        results = []

        spell = spell_class(caster_level)
        attack = DrinkPotion(actor, spell)
        results.extend(attack.execute())

        results.append({'consumed': True})

        return results
