from action_processing.actions.action import Action
from player_locations import PlayerLocations


class MouseoverAction(Action):
    def run(self, mouseover_tile):
        if self.engine.player_location == PlayerLocations.WORLD_MAP:
            x, y = (mouseover_tile.x, mouseover_tile.y)
            if not self.engine.world_map.is_void(x, y) and self.engine.fov_map.fov[x][y]:
                return self.engine.world_map.tiles[x][y].biom.name.capitalize()
        elif self.engine.player_location == PlayerLocations.DUNGEON:
            x, y = (mouseover_tile.x, mouseover_tile.y)
            tile_contents = [entity.name for entity in self.engine.entities.all
                        if entity.x == x and entity.y == y and self.engine.fov_map.fov[entity.x][entity.y]]

            if not self.engine.world_map.current_dungeon.is_void(x, y):
                tile = self.engine.world_map.current_dungeon.tiles[x][y]
                if 'explored' in tile.regulatory_flags:
                    tile_contents.extend(tile.whats_there())
            self.engine.whats_under_mouse = ', '.join(tile_contents) + ' {0}'.format((x, y))
            self.engine.render_tick()
