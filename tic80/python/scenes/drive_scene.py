from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import cls, keyp, print

    from ..contracts import DriveEnterParams, ResultEnterParams, SceneNavigator
    from ..core.palette import Color
    from ..core.run_state import RunState
    from ..core.scene_ids import SceneId
    from ..data.tuning import TUNING
    from ..systems.drive.drive_input import read_drive_input
    from ..systems.drive.drive_logic_core import DriveLogic
    from ..systems.drive.drive_obstacle_hits import apply_obstacle_hits
    from ..systems.drive.drive_objects import DriveObjects, DriveZone
    from ..systems.drive.drive_telemetry import DriveTelemetry
    from ..systems.drive.drive_debug_lines import drive_debug_lines
    from ..systems.drive.drive_zone_effects import apply_zone_effects
    from ..systems.drive.drive_zones import zone_at_hitboxes
    from ..systems.drive.road_model import RoadModel
    from .drive.drive_topdown_renderer import DriveTopdownRenderer
    from .drive.drive_ui import DriveUi


class DriveScene:
    SCENE_ID = SceneId.DRIVE

    def __init__(self, nav: SceneNavigator) -> None:
        self._nav = nav
        self._state = nav.state
        self._mode = "travel"
        self._variant = "topdown"
        self._road: RoadModel | None = None
        self._logic: DriveLogic | None = None
        self._objects: DriveObjects | None = None
        self._active_zone: DriveZone | None = None
        self._evacuated = False
        self._telemetry: DriveTelemetry | None = None
        self._renderer = DriveTopdownRenderer()
        self._ui = DriveUi()
        self._last_hp = 0.0
        self._start_car_hp = 0.0
        self._start_car_fuel = 0.0

    def enter(self, params: object | None = None) -> None:
        if not isinstance(params, DriveEnterParams):
            raise TypeError("DriveScene.enter expects DriveEnterParams")
        self._mode = params.mode
        self._variant = params.variant
        self._evacuated = False
        self._road = None
        self._logic = None
        self._objects = None
        self._active_zone = None

        run = self._state.require_run()
        seed = run.seed
        self._road = RoadModel.from_tuning(seed, TUNING)
        self._logic = DriveLogic(run, self._road, TUNING)
        self._objects = DriveObjects.from_road_and_tuning(
            seed, self._road, TUNING)
        self._last_hp = run.car_hp
        self._start_car_hp = run.car_hp
        self._start_car_fuel = run.car_fuel

        if TUNING.DRIVE.telemetry_enabled:
            self._telemetry = DriveTelemetry(
                int(TUNING.DRIVE.telemetry_every_frames),
                int(TUNING.DRIVE.telemetry_max_lines)
            )
            self._telemetry.begin(run.seed, self._mode, self._variant, TUNING)
        else:
            self._telemetry = None

    def update(self, dt: float) -> None:
        run = self._state.run
        if run is None:
            return
        if self._logic is None:
            return
        if self._road is None:
            return
        if self._objects is None:
            return
        if self._state.playtest_enabled and keyp(18):
            self._restart_segment()
            return
        if self._state.playtest_enabled:
            self._state.playtest_add_time(dt)

        zones = self._objects.zones_items()
        z_before = zone_at_hitboxes(self._logic, zones)
        apply_zone_effects(self._logic, z_before, TUNING)

        allow_dash = not self._logic.finished()
        inp = read_drive_input(allow_dash)
        self._logic.update(dt, inp.steer, inp.throttle, inp.brake, inp.handbrake, inp.dash_pressed)
        z_after = zone_at_hitboxes(self._logic, zones)
        self._active_zone = z_after if z_after is not None else z_before

        self._apply_obstacle_hits(run)

        # Обновляем эффекты зон для СЛЕДУЮЩЕГО кадра (без 1-кадрового “залипания”).
        apply_zone_effects(self._logic, z_after, TUNING)
        if self._telemetry is not None:
            self._telemetry.after_update(
                dt,
                inp.steer,
                inp.throttle,
                inp.brake,
                inp.handbrake,
                inp.dash_pressed,
                run,
                self._logic
            )

        if not self._evacuated:
            if run.car_fuel <= 0:
                self._evacuate(run, "OUT OF FUEL")
                return
            if run.car_hp <= 0:
                self._evacuate(run, "CAR DESTROYED")
                return

        if self._logic.finished() and inp.a_pressed:
            if self._telemetry is not None:
                self._telemetry.dump("finish")
            if self._state.playtest_enabled:
                self._state.playtest_finish_segment()
                self._nav.go(SceneId.RESULT,
                             ResultEnterParams("SEGMENT COMPLETE"))
                return
            if self._mode == "travel":
                self._nav.go(SceneId.POI)
                return

            delta = run.ensure_delta(run.node_id)
            delta.set_escape_outcome("ok")
            self._nav.go(SceneId.RESULT, ResultEnterParams("EXTRACT OK"))

    def _apply_obstacle_hits(self, run: RunState) -> None:
        road = self._road
        logic = self._logic
        objects = self._objects
        if road is None or logic is None or objects is None:
            return
        apply_obstacle_hits(run, road, logic, objects, TUNING, self._renderer.notify_obstacle_hit)

    def _restart_segment(self) -> None:
        run = self._state.run
        if run is None:
            return
        run.reset_car_stats(self._start_car_hp, self._start_car_fuel)
        self.enter(DriveEnterParams(self._mode, self._variant))

    def draw(self) -> None:
        cls(Color.BLACK)
        self._draw_topdown()

    def _draw_topdown(self) -> None:
        """Top-down рендер DRIVE: дорога, зоны, препятствия, машина, подсказки."""
        logic = self._logic
        road = self._road
        run = self._state.run
        objects = self._objects
        if logic is None or road is None or run is None or objects is None:
            return

        # Рендер держим отдельно от сцены, чтобы позже легко подключить второй вид (cockpit)
        # и не раздувать DriveScene.
        self._renderer.draw(road, logic, objects, self._active_zone)
        self._ui.draw_stats(run, logic)
        self._ui.draw_steer_wheel(logic)
        self._ui.draw_slip_bar(logic)
        if logic.finished():
            print("Z = CONTINUE", 2, 128, Color.WHITE)
        else:
            print("ARROWS + X", 2, 128, Color.WHITE)
        self._state.set_debug_lines(
            drive_debug_lines(road, logic, run, objects, TUNING))
        return

    def exit(self) -> None:
        pass

    def _evacuate(self, run: RunState, reason: str) -> None:
        delta = run.ensure_delta(run.node_id)
        delta.set_escape_outcome("fail")
        self._evacuated = True
        if self._telemetry is not None:
            self._telemetry.dump("evac " + reason)
        self._nav.go(SceneId.RESULT, ResultEnterParams(reason))


def make_drive_scene(nav: SceneNavigator) -> DriveScene:
    return DriveScene(nav)
