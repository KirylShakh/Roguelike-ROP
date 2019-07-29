from game_vars import player_vars
from game_vars import color_vars
from entity_objects.entity import Entity
from components.fighter import Fighter
from components.inventory import Inventory
from components.level import Level
from components.equipment import Equipment
from render_objects.render_order import RenderOrder


def create_player():
    fighter_component = Fighter(hp=player_vars.hp, defense=player_vars.defense,
                                power=player_vars.power)
    inventory_component = Inventory(player_vars.inventory_size)
    level_component = Level()
    equipment_component = Equipment()
    return Entity(0, 0, player_vars.char, color_vars.player, player_vars.name, blocks=True,
                    render_order=RenderOrder.ACTOR, fighter=fighter_component,
                    inventory=inventory_component, level=level_component,
                    equipment=equipment_component)
