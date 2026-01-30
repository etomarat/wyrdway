from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import btnp, cls, print

    from ..core.input_buttons import Button
    from ..core.scene_ids import SceneId
    from ..core.scene_manager import SceneNavigator


class GarageScene:
    def __init__(self, nav: "SceneNavigator") -> None:
        self._nav = nav
        self.note = "Press A to start run"

    def enter(self, params: object | None = None) -> None:
        pass

    def update(self, dt: float) -> None:
        if btnp(Button.A):
            self._nav.go(SceneId.REGION_MAP)

    def draw(self) -> None:
        cls(0)
        print("GARAGE", 98, 40, 12)
        print(self.note, 56, 60, 12)

    def exit(self) -> None:
        pass


def make_garage_scene(nav: "SceneNavigator") -> "GarageScene":
    return GarageScene(nav)
