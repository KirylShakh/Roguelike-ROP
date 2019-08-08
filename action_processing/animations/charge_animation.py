from action_processing.animations.move_animation import MoveAnimation
from action_processing.animations.push_animation import PushAnimation
from game_messages import Message


class ChargeAnimation(MoveAnimation):
    def __init__(self, engine, entity, path, target):
        super(ChargeAnimation, self).__init__(engine, entity)

        self.path = path
        self.target = target

    def complete(self):
        self.completed = True
        if abs(self.entity.x - self.target.x) <= 1 and abs(self.entity.y - self.target.y) <= 1:
            next_animation = PushAnimation(self.engine, self.target,
                                            (self.entity.x, self.entity.y), 3)
            self.engine.animations.append(next_animation)
            return [{'message': Message('The {0} slammed into the {1}, sending {1} flying'.format(
                self.entity.name, self.target.name
            ))}]
        return []
