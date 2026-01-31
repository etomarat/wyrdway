from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import btn, btnp, cls, print

    from ..contracts import DriveEnterParams, ResultEnterParams, SceneNavigator
    from ..core.input_buttons import Button
    from ..core.run_state import RunState
    from ..core.scene_ids import SceneId
    from ..data.tuning import TUNING


class DriveScene:
    SCENE_ID = SceneId.DRIVE

    def __init__(self, nav: SceneNavigator) -> None:
        self._nav = nav
        self._state = nav.state
        self._t = 0.0
        self._mode = "travel"
        self._x = 0.0
        self._y = 68.0
        self._finished = False
        self._evacuated = False

    def enter(self, params: object | None = None) -> None:
        if not isinstance(params, DriveEnterParams):
            raise TypeError("DriveScene.enter expects DriveEnterParams")
        self._mode = params.mode
        self._x = 10.0
        self._finished = False
        self._evacuated = False

    def update(self, dt: float) -> None:
        self._t += dt

        run = self._state.run
        move = 0.0
        if btn(Button.LEFT):
            move -= TUNING.DRIVE.move_speed * dt
        if btn(Button.RIGHT):
            move += TUNING.DRIVE.move_speed * dt
        if move != 0.0:
            self._x += move

        if run is not None:
            if move != 0.0:
                run.consume_fuel(dt * TUNING.DRIVE.fuel_per_sec)

            run.apply_damage(dt * TUNING.DRIVE.damage_per_sec)

            if not self._evacuated:
                if run.car_fuel <= 0:
                    self._evacuate(run, "OUT OF FUEL")
                    return
                if run.car_hp <= 0:
                    self._evacuate(run, "CAR DESTROYED")
                    return

        finish_x = TUNING.DRIVE.segment_length
        if self._x < 0:
            self._x = 0.0
        if self._x > finish_x:
            self._x = finish_x
        if self._x >= finish_x:
            self._finished = True
        else:
            self._finished = False

        if self._finished and btnp(Button.A):
            if self._mode == "travel":
                self._nav.go(SceneId.POI)
            else:
                if run is not None and run.delta is not None:
                    run.delta.set_escape_outcome("ok")
                self._nav.go(SceneId.RESULT, ResultEnterParams("EXTRACT OK"))

    def draw(self) -> None:
        cls(0)
        print("DRIVE", 104, 30, 12)
        print("mode=" + self._mode, 86, 50, 12)
        print("t=" + str(round(self._t, 2)), 92, 60, 12)
        run = self._state.run
        if run is not None:
            print("fuel=" + str(round(run.car_fuel, 1)), 88, 70, 12)
            print("hp=" + str(run.car_hp), 98, 80, 12)
        print("finish=" + str(int(TUNING.DRIVE.segment_length)),
              74, 90, 12)
        print("x=" + str(int(self._x)), 104, 100, 12)
        if self._finished:
            if self._mode == "travel":
                print("A = ARRIVE", 80, 110, 12)
            else:
                print("A = ESCAPE", 80, 110, 12)
        else:
            print("HOLD -> or <- ", 92, 110, 12)

    def exit(self) -> None:
        pass

    def _evacuate(self, run: RunState, reason: str) -> None:
        delta = run.ensure_delta(run.node_id)
        delta.set_escape_outcome("fail")
        self._evacuated = True
        self._nav.go(SceneId.RESULT, ResultEnterParams(reason))


def make_drive_scene(nav: SceneNavigator) -> DriveScene:
    return DriveScene(nav)
