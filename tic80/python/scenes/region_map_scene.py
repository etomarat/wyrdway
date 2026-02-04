from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import btnp, cls, print

    from ..contracts import DriveEnterParams, SceneNavigator
    from ..core.input_buttons import Button
    from ..core.palette import Color
    from ..core.scene_ids import SceneId


class RegionMapScene:
    SCENE_ID = SceneId.REGION_MAP

    def __init__(self, nav: "SceneNavigator") -> None:
        self._nav = nav
        self._state = nav.state
        self.selected_node = 1
        self.node_count = 5

    def enter(self, params: object | None = None) -> None:
        run = self._state.run
        if run is not None and run.node_id is not None:
            self.selected_node = run.node_id

    def update(self, dt: float) -> None:
        if btnp(Button.UP):
            self.selected_node = max(1, self.selected_node - 1)
        if btnp(Button.DOWN):
            self.selected_node = min(self.node_count, self.selected_node + 1)
        if btnp(Button.A):
            run = self._state.require_run()
            run.set_node_id(self.selected_node)
            run.ensure_delta(run.node_id)
            self._nav.go(SceneId.DRIVE, DriveEnterParams("travel"))

    def draw(self) -> None:
        cls(Color.BLACK)
        print("REGION MAP", 84, 30, Color.WHITE)
        run = self._state.run
        if run is not None:
            print("seed=" + str(run.seed), 90, 40, Color.WHITE)
        for i in range(self.node_count):
            node_id = i + 1
            marker = ">" if node_id == self.selected_node else " "
            print(marker + " NODE " + str(node_id), 70, 50 + i * 8, Color.WHITE)
        print("Z = GO", 96, 100, Color.WHITE)

    def exit(self) -> None:
        pass


def make_region_map_scene(nav: "SceneNavigator") -> "RegionMapScene":
    return RegionMapScene(nav)
