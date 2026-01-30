from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import btnp, cls, print

    from ..contracts import DriveEnterParams
    from ..core.input_buttons import Button
    from ..core.scene_ids import SceneId
    from ..core.scene_manager import SceneNavigator


class RegionMapScene:
    def __init__(self, nav: "SceneNavigator") -> None:
        self._nav = nav
        self.selected_node = 1
        self.node_count = 5

    def enter(self, params: object | None = None) -> None:
        pass

    def update(self, dt: float) -> None:
        if btnp(Button.UP):
            self.selected_node = max(1, self.selected_node - 1)
        if btnp(Button.DOWN):
            self.selected_node = min(self.node_count, self.selected_node + 1)
        if btnp(Button.A):
            self._nav.go(SceneId.DRIVE, DriveEnterParams("travel"))

    def draw(self) -> None:
        cls(0)
        print("REGION MAP", 84, 30, 12)
        for i in range(self.node_count):
            node_id = i + 1
            marker = ">" if node_id == self.selected_node else " "
            print(marker + " NODE " + str(node_id), 70, 50 + i * 8, 12)
        print("A = GO", 96, 100, 12)

    def exit(self) -> None:
        pass


def make_region_map_scene(nav: "SceneNavigator") -> "RegionMapScene":
    return RegionMapScene(nav)
