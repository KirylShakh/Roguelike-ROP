from action_processing.actions.action import Action
from combat.spells.spell import SpellTags
from game_messages import Message
from combat.attacks.cast_scroll import CastScroll
from game_vars import color_vars


class CastScrollAction(Action):
    def run(self, actor, spell_class=None, caster_level=None, target_point=None):
        if not caster_level:
            caster_level = actor.caster.level

        spell = spell_class(caster_level)
        if SpellTags.AUTO_TARGET in spell.tags:
            return self.handle_auto_target_spell(actor, spell)
        elif SpellTags.AREA in spell.tags:
            return self.handle_area_spell(actor, spell, target_point)
        elif SpellTags.TARGET in spell.tags:
            return self.handle_target_spell(actor, spell, target_point)

        return []

    def handle_auto_target_spell(self, actor, spell):
        results = []

        target = self.find_closest_target(actor, spell.maximum_range)
        if target:
            attack = CastScroll(actor, target, spell)
            if attack.too_tired_to_execute():
                results.extend(attack.log_too_tired_results())
                return results

            results.append({'consumed': True})

            animation_class = spell.animation_class()
            if animation_class:
                animation = animation_class(self.engine, (actor.x, actor.y), target, attack=attack)
                self.engine.animations.append(animation)
            else:
                results.extend(attack.execute())
        else:
            if SpellTags.DAMAGE in spell.tags:
                message = 'No enemy is close enough to strike'
            else:
                message = 'Noone is close enough to target'
            results.append({'consumed': False, 'target': None, 'message': Message(message, color_vars.error_message)})

        return results

    def find_closest_target(self, actor, maximum_range):
        target = None
        closest_distance = maximum_range + 1

        for entity in self.engine.entities.all:
            if entity.fighter and entity != actor and self.engine.fov_map.fov[entity.x][entity.y]:
                distance = actor.distance_to(entity)

                if distance < closest_distance:
                    target = entity
                    closest_distance = distance

        return target

    def handle_area_spell(self, actor, spell, target_point):
        results = []
        target_x, target_y = target_point
        if not self.engine.fov_map.fov[target_x][target_y]:
            results.append({'consumed': False, 'message': Message('You cannot target a tile outside your field of view', color_vars.warning)})
            return results

        targets = []
        for entity in self.engine.entities.all:
            if entity.distance(target_x, target_y) <= spell.radius and entity.fighter:
                targets.append(entity)

        attack = CastScroll(actor, targets, spell)
        if attack.too_tired_to_execute():
            results.extend(attack.log_too_tired_results())
            return results

        results.append({'consumed': True})

        animation_class = spell.animation_class()
        if animation_class:
            animation = animation_class(self.engine, (target_x, target_y), spell.radius, spell.color(), attack=attack)
            self.engine.animations.append(animation)
        else:
            results.extend(attack.execute())

        return results

    def handle_target_spell(self, actor, spell, target_point):
        results = []
        target_x, target_y = target_point
        if not self.engine.fov_map.fov[target_x][target_y]:
            results.append({'consumed': False, 'message': Message('You cannot target a tile outside your field of view', color_vars.warning)})
            return results

        for entity in self.engine.entities.all:
            if entity.x == target_x and entity.y == target_y and entity.ai:
                results.append({'consumed': True})

                attack = CastScroll(actor, entity, spell)
                results.extend(attack.execute())

                break
        else:
            if SpellTags.DAMAGE in spell.tags:
                message = 'There is no targetable enemy at that location'
            else:
                message = 'There is noone at that location'
            results.append({'consumed': False, 'message': Message(message, color_vars.warning)})

        return results
