from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import btnp, cls, print

    from ..contracts import DriveEnterParams, ResultEnterParams
    from ..core.input_buttons import Button
    from ..core.scene_ids import SceneId
    from ..core.scene_manager import SceneNavigator


class DriveScene:
    def __init__(self, nav: "SceneNavigator") -> None:
        self._nav = nav
        self._t = 0.0
        self._mode = "travel"

    def enter(self, params: object | None = None) -> None:
        if not isinstance(params, DriveEnterParams):
            raise TypeError("DriveScene.enter expects DriveEnterParams")
        self._mode = params.mode

    def update(self, dt: float) -> None:
        self._t += dt
        if btnp(Button.A):
            if self._mode == "travel":
                self._nav.go(SceneId.POI)
            else:
                self._nav.go(SceneId.RESULT, ResultEnterParams("EXTRACT OK"))

    def draw(self) -> None:
        cls(0)
        print("DRIVE", 104, 30, 12)
        print("mode=" + self._mode, 86, 50, 12)
        print("t=" + str(round(self._t, 2)), 92, 60, 12)
        if self._mode == "travel":
            print("A = ARRIVE", 80, 100, 12)
        else:
            print("A = ESCAPE", 80, 100, 12)

    def exit(self) -> None:
        pass


def make_drive_scene(nav: "SceneNavigator") -> "DriveScene":
    return DriveScene(nav)
