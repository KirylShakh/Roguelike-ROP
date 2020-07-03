import tcod

from components.component import Component
from game_messages import Message

class Inventory(Component):
    def __init__(self, capacity):
        self.capacity = capacity
        self.items = []

    def add_item(self, item):
        results = []

        if len(self.items) >= self.capacity:
            results.append({
                'item_added': None,
                'message': Message('You cannot carry any more, your inventory is full', tcod.yellow)
            })
        else:
            results.append({
                'item_added': item,
                'message': Message('You pick up the {0}'.format(item.name), tcod.blue)
            })
            self.items.append(item)

        return results

    def remove_item(self, item):
        self.items.remove(item)

    def drop_item(self, item):
        results = []

        if (self.owner.equipment.main_hand == item
                or self.owner.equipment.off_hand == item):
            self.owner.equipment.toggle_equip(item)

        item.x = self.owner.x
        item.y = self.owner.y

        self.remove_item(item)
        results.append({'item_dropped': item,
                        'message': Message('You dropped the {0}'.format(item.name), tcod.yellow)})

        return results

    def use(self, item_entity, **kwargs):
        results = []

        item_component = item_entity.item
        if item_component.action_class is None:
            if item_entity.equippable:
                results.append({'equip': item_entity})
            else:
                results.append({'message': Message('The {0} cannot be used'.format(item_entity.name), tcod.yellow)})
        else:
            if item_component.targeting and not (kwargs.get('target_x') or kwargs.get('target_y')):
                results.append({'targeting': item_entity})
            else:
                kwargs = {**item_component.action_args, **kwargs}
                item_use_results = self.run_use_action(item_component.action_class, **kwargs)

                for item_use_result in item_use_results:
                    if item_use_result.get('consumed'):
                        self.remove_item(item_entity)
                results.extend(item_use_results)

        return results

    def run_use_action(self, action_class, **kwargs):
        caster_level = kwargs.get('caster_level')
        engine = kwargs.get('engine')
        target_x = kwargs.get('target_x')
        target_y = kwargs.get('target_y')
        spell_class = kwargs.get('spell')

        action_args = {}
        if target_x is not None:
            action_args['target_point'] = (target_x, target_y)
        if spell_class is not None:
            action_args['spell_class'] = spell_class
        if caster_level is not None:
            action_args['caster_level'] = caster_level

        action = action_class(engine)
        return action.run(self.owner, **action_args)
