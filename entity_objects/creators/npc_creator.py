from game_vars import npc_vars
from game_vars import color_vars
from entity_objects.entity import Entity
from components.fighter import Fighter
from components.ai import BasicMonster
from render_objects.render_order import RenderOrder


def create_orc(x=0, y=0):
    fighter_component = Fighter(hp=npc_vars.orc_hp, defense=npc_vars.orc_defense,
                                power=npc_vars.orc_power, xp=npc_vars.orc_xp)
    ai_component = BasicMonster()
    return Entity(x, y, npc_vars.orc_char, color_vars.greenskin, npc_vars.orc_name, blocks=True,
                    render_order=RenderOrder.ACTOR, fighter=fighter_component, ai=ai_component)

def create_troll(x=0, y=0):
    fighter_component = Fighter(hp=npc_vars.troll_hp, defense=npc_vars.troll_defense,
                                power=npc_vars.troll_power, xp=npc_vars.troll_xp)
    ai_component = BasicMonster()
    return Entity(x, y, npc_vars.troll_char, color_vars.troll, npc_vars.troll_name, blocks=True,
            render_order=RenderOrder.ACTOR, fighter=fighter_component, ai=ai_component)
