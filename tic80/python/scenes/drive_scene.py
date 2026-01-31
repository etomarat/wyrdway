from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import btnp, cls, print

    from ..contracts import DriveEnterParams, ResultEnterParams
    from ..contracts import SceneNavigator
    from ..core.input_buttons import Button
    from ..core.scene_ids import SceneId
    from ..data.tuning import TUNING


class DriveScene:
    def __init__(self, nav: "SceneNavigator") -> None:
        self._nav = nav
        self._state = nav.state
        self._t = 0.0
        self._mode = "travel"

    def enter(self, params: object | None = None) -> None:
        if not isinstance(params, DriveEnterParams):
            raise TypeError("DriveScene.enter expects DriveEnterParams")
        self._mode = params.mode

    def update(self, dt: float) -> None:
        self._t += dt

        run = self._state.run
        if run is not None:
            run.car_fuel = max(0.0,
                               run.car_fuel - dt * TUNING.DRIVE.fuel_per_sec)

        if btnp(Button.A):
            if self._mode == "travel":
                self._nav.go(SceneId.POI)
            else:
                if run is not None and run.delta is not None:
                    run.delta.escape_outcome = "ok"
                self._nav.go(SceneId.RESULT, ResultEnterParams("EXTRACT OK"))

    def draw(self) -> None:
        cls(0)
        print("DRIVE", 104, 30, 12)
        print("mode=" + self._mode, 86, 50, 12)
        print("t=" + str(round(self._t, 2)), 92, 60, 12)
        run = self._state.run
        if run is not None:
            print("fuel=" + str(round(run.car_fuel, 1)), 88, 70, 12)
        if self._mode == "travel":
            print("A = ARRIVE", 80, 100, 12)
        else:
            print("A = ESCAPE", 80, 100, 12)

    def exit(self) -> None:
        pass


def make_drive_scene(nav: "SceneNavigator") -> "DriveScene":
    return DriveScene(nav)
