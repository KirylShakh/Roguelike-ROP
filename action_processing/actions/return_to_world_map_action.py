from action_processing.actions.action import Action
from player_locations import PlayerLocations
from fov_functions import initialize_world_fov
from entity_objects.map_entities import MapEntities


class ReturnToWorldMapAction(Action):
    def run(self):
        self.engine.player_location = PlayerLocations.WORLD_MAP
        self.engine.fov_map = initialize_world_fov(self.engine.world_map)
        self.engine.fov_recompute = True
        self.engine.renderer.clear()

        x, y = self.engine.world_map.current_dungeon_entry_point
        self.engine.entities.player.x = x
        self.engine.entities.player.y = y

        self.engine.world_map.current_dungeon = None
        self.engine.world_map.current_dungeon_entry_point = None

        self.engine.entities = MapEntities(self.engine.entities.player)
