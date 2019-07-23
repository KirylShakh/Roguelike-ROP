import tcod

from components.component import Component

class BasicMonster(Component):
    def take_turn(self, target, fov_map, game_map, entities):
        results = []

        monster = self.owner
        if fov_map.fov[monster.x][monster.y]:
            if monster.distance_to(target) >= 2:
                monster.move_astar(target, entities, game_map)
            elif target.fighter and target.fighter.hp > 0:
                attack_results = monster.fighter.attack(target)
                results.extend(attack_results)

        return results
