from game_vars import item_vars
from game_vars import color_vars
from entity_objects.entity import Entity
from components.equippable import Equippable
from components.equipment import EquipmentSlots
from components.item import Item
from item_functions import heal, cast_lightning, cast_fireball, cast_confuse
from render_objects.render_order import RenderOrder
from game_messages import Message

def create_dagger(x=0, y=0):
    equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=item_vars.dagger_power)
    return Entity(0, 0, item_vars.small_blades_char, color_vars.dagger, item_vars.dagger_name,
                    equippable=equippable_component)

def create_healing_potion(x=0, y=0):
    item_component = Item(use_function=heal, amount=item_vars.healing_potion_amount)
    return Entity(x, y, item_vars.potion_char, color_vars.healing_potion,
                    item_vars.healing_potion_name, render_order=RenderOrder.ITEM,
                    item=item_component)

def create_sword(x=0, y=0):
    equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=item_vars.sword_power)
    return Entity(x, y, item_vars.medium_blades_char, color_vars.sword, item_vars.sword_name,
                    equippable=equippable_component)

def create_shield(x=0, y=0):
    equippable_component = Equippable(EquipmentSlots.OFF_HAND, defense_bonus=item_vars.shield_defense)
    return Entity(x, y, item_vars.shields_char, color_vars.shield, item_vars.shield_name,
                    equippable=equippable_component)

def create_fireball_scroll(x=0, y=0):
    item_component = Item(use_function=cast_fireball, targeting=True,
                            damage=item_vars.fireball_scroll_damage,
                            radius=item_vars.fireball_scroll_radius,
                            targeting_message=Message(item_vars.fireball_target_message, color_vars.target_message))
    return Entity(x, y, item_vars.scroll_char, color_vars.fireball_scroll,
                item_vars.fireball_scroll_name, render_order=RenderOrder.ITEM,
                item=item_component)

def create_lightning_scroll(x=0, y=0):
    item_component = Item(use_function=cast_lightning, damage=item_vars.lightning_scroll_damage,
                            maximum_range=item_vars.lightning_scroll_max_range)
    return Entity(x, y, item_vars.scroll_char, color_vars.lightning_scroll,
                item_vars.lightning_scroll_name, render_order=RenderOrder.ITEM,
                item=item_component)

def create_confuse_scroll(x=0, y=0):
    item_component = Item(use_function=cast_confuse, targeting=True,
                targeting_message=Message(item_vars.confuse_target_message, color_vars.target_message))
    return Entity(x, y, item_vars.scroll_char, color_vars.confuse_scroll,
                item_vars.confuse_scroll_name, render_order=RenderOrder.ITEM,
                item=item_component)
