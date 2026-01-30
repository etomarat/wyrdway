from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import btnp, cls, print

    from ..contracts import DriveEnterParams
    from ..core.input_buttons import Button
    from ..core.scene_ids import SceneId
    from ..core.scene_manager import SceneNavigator


class PoiScene:
    def __init__(self, nav: "SceneNavigator") -> None:
        self._nav = nav
        self.timer = 10.0

    def enter(self, params: object | None = None) -> None:
        pass

    def _leave(self) -> None:
        self._nav.go(SceneId.DRIVE, DriveEnterParams("extract"))

    def update(self, dt: float) -> None:
        self.timer = max(0.0, self.timer - dt)
        if btnp(Button.A) or btnp(Button.B) or self.timer <= 0.0:
            self._leave()

    def draw(self) -> None:
        cls(0)
        print("POI", 112, 30, 12)
        print("timer=" + str(round(self.timer, 1)), 82, 50, 12)
        print("A = LOOT", 90, 70, 12)
        print("B = LEAVE", 88, 80, 12)

    def exit(self) -> None:
        pass


def make_poi_scene(nav: "SceneNavigator") -> "PoiScene":
    return PoiScene(nav)
