import tcod

from game_messages import Message
from combat.spells.confuse import Confuse
from combat.attacks.cast_scroll import CastScroll

from action_processing.actions.action import Action


class CastConfuseAction(Action):
    def run(self, actor, target_point, caster_level=None):
        if not caster_level:
            caster_level = actor.caster.level

        results = []
        target_x, target_y = target_point
        if not self.engine.fov_map.fov[target_x][target_y]:
            results.append({'consumed': False, 'message': Message('You cannot target a tile outside your field of view', tcod.yellow)})
            return results

        for entity in self.engine.entities.all:
            if entity.x == target_x and entity.y == target_y and entity.ai:
                attack = CastScroll(actor, entity, Confuse(caster_level))
                results.extend(attack.execute())

                results.append({'consumed': True})
                break
            else:
                results.append({'consumed': False, 'message': Message('There is no targetable enemy at that location', tcod.yellow)})

        return results
