from random import randint

def random_choice_index(chances):
    random_chance = randint(1, sum(chances))

    running_sum = 0
    choice = 0
    for w in chances:
        running_sum += w

        if random_chance <= running_sum:
            return choice
        choice += 1

def random_choice_from_dict(choice_dict):
    choices = list(choice_dict.keys())
    chances = list(choice_dict.values())

    return choices[random_choice_index(chances)]

def from_dungeon_level(table, dungeon_level):
    for (value, level) in reversed(table):
        if dungeon_level >= level:
            return value
    return 0

def weight_factor(d, dungeon_level=1):
    weights = {}
    for k, v in d.items():
        if isinstance(v['weight_factor'], list):
            weights[k] = from_dungeon_level(v['weight_factor'], dungeon_level)
        else:
            weights[k] = v['weight_factor']

    return weights
