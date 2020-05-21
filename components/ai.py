import tcod

from random import randint

from components.component import Component
from game_messages import Message

class BasicMonster(Component):
    def take_turn(self, target, fov_map, game_map, entities):
        results = []

        monster = self.owner
        if fov_map.fov[monster.x][monster.y]:
            distance = monster.distance_to(target)
            path = game_map.path_straight(monster.x, monster.y, target.x, target.y)

            if monster.name == 'Orc' and distance >= 4 and not game_map.is_path_blocked(path, entities):
                results.append({
                    'charge': path,
                    'message': Message('The {0} charges at the {1}'.format(monster.name, target.name)),
                })
            elif distance >= 2:
                monster.move_astar(target, entities, game_map)
            elif target.fighter and not target.constitution.depleted():
                attack_results = monster.fighter.attack(target)
                results.extend(attack_results)

        return results

class ConfusedMonster(Component):
    def __init__(self, previous_ai, number_of_turns=10):
        self.previous_ai = previous_ai
        self.number_of_turns = number_of_turns

    def take_turn(self, target, fov_map, game_map, entities):
        results = []

        if self.number_of_turns > 0:
            random_x = self.owner.x + randint(0, 2) - 1
            random_y = self.owner.y + randint(0, 2) - 1

            if random_x != self.owner.x and random_y != self.owner.y:
                self.owner.move_towards(random_x, random_y, game_map, entities)

            self.number_of_turns -= 1
        else:
            self.owner.ai = self.previous_ai
            results.append({'message': Message('The {0} is no longer confused'.format(self.owner.name), tcod.red)})

        return results
