from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import btn, btnp, cls, print

    from ..contracts import DriveEnterParams, ResultEnterParams, SceneNavigator
    from ..core.input_buttons import Button
    from ..core.scene_ids import SceneId
    from ..core.run_state import RunState
    from ..data.tuning import TUNING
    from ..systems.drive.drive_logic import DriveLogic
    from ..systems.drive.road_model import RoadModel


class DriveScene:
    SCENE_ID = SceneId.DRIVE

    def __init__(self, nav: SceneNavigator) -> None:
        self._nav = nav
        self._state = nav.state
        self._mode = "travel"
        self._variant = "topdown"
        self._road: RoadModel | None = None
        self._logic: DriveLogic | None = None
        self._evacuated = False

    def enter(self, params: object | None = None) -> None:
        if not isinstance(params, DriveEnterParams):
            raise TypeError("DriveScene.enter expects DriveEnterParams")
        self._mode = params.mode
        self._variant = params.variant
        self._evacuated = False
        self._road = None
        self._logic = None

        run = self._state.require_run()
        seed = run.seed
        self._road = RoadModel.from_tuning(seed, TUNING)
        self._logic = DriveLogic(run, self._road, TUNING)

    def update(self, dt: float) -> None:
        run = self._state.run
        if run is None:
            return
        if self._logic is None:
            return

        steer = 0
        if btn(Button.LEFT):
            steer -= 1
        if btn(Button.RIGHT):
            steer += 1

        throttle = btn(Button.UP)
        brake = btn(Button.DOWN)
        handbrake = btn(Button.B)

        self._logic.update(dt, steer, throttle, brake, handbrake)

        if not self._evacuated:
            if run.car_fuel <= 0:
                self._evacuate(run, "OUT OF FUEL")
                return
            if run.car_hp <= 0:
                self._evacuate(run, "CAR DESTROYED")
                return

        if self._logic.finished() and btnp(Button.A):
            if self._mode == "travel":
                self._nav.go(SceneId.POI)
                return

            delta = run.ensure_delta(run.node_id)
            delta.set_escape_outcome("ok")
            self._nav.go(SceneId.RESULT, ResultEnterParams("EXTRACT OK"))

    def draw(self) -> None:
        cls(0)
        print("DRIVE", 104, 30, 12)
        print("mode=" + self._mode, 86, 40, 12)
        print("view=" + self._variant, 82, 50, 12)
        run = self._state.run
        if run is not None:
            print("fuel=" + str(round(run.car_fuel, 1)), 88, 60, 12)
            print("hp=" + str(round(run.car_hp, 1)), 94, 70, 12)

        logic = self._logic
        road = self._road
        if logic is not None and road is not None:
            print("s=" + str(int(logic.s)) + "/" + str(int(road.segment_total_length)),
                  70, 82, 12)
            print("d=" + str(round(logic.d, 2)), 90, 92, 12)
            print("spd=" + str(round(logic.speed, 1)), 84, 102, 12)
            if logic.offroad:
                print("OFFROAD", 96, 112, 2)
            if logic.finished():
                print("A = CONTINUE", 70, 122, 12)
            else:
                print("UP/DN/LR + B", 68, 122, 12)

    def exit(self) -> None:
        pass

    def _evacuate(self, run: RunState, reason: str) -> None:
        delta = run.ensure_delta(run.node_id)
        delta.set_escape_outcome("fail")
        self._evacuated = True
        self._nav.go(SceneId.RESULT, ResultEnterParams(reason))


def make_drive_scene(nav: SceneNavigator) -> DriveScene:
    return DriveScene(nav)
