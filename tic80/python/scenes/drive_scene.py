from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import btn, btnp, cls, print

    from ..contracts import DriveEnterParams, ResultEnterParams, SceneNavigator
    from ..core.input_buttons import Button
    from ..core.palette import Color
    from ..core.run_state import RunState
    from ..core.scene_ids import SceneId
    from ..data.tuning import TUNING
    from ..systems.drive.drive_input import DriveInput, read_drive_input
    from ..systems.drive.drive_logic_core import DriveLogic
    from ..systems.drive.drive_obstacle_hits import apply_obstacle_hits
    from ..systems.drive.drive_objects import DriveObjects, DriveZone
    from ..systems.drive.drive_telemetry import DriveTelemetry
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
        if self._state.playtest_enabled:
            self._state.playtest_add_time(dt)

        zones = self._objects.zones_items_view()
        z_before = zone_at_hitboxes(self._logic, zones)
        self._apply_zone_effects(z_before)

        allow_dash = not self._logic.finished()
        inp = read_drive_input(allow_dash)
        self._logic.update(dt, inp.steer, inp.throttle, inp.brake, inp.handbrake, inp.dash_pressed)
        z_after = zone_at_hitboxes(self._logic, zones)
        self._active_zone = z_after if z_after is not None else z_before

        self._apply_obstacle_hits(run)

        # Обновляем эффекты зон для СЛЕДУЮЩЕГО кадра (без 1-кадрового “залипания”).
        self._apply_zone_effects(z_after)
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

    def draw(self) -> None:
        cls(Color.BLACK)
        if self._variant == "topdown":
            self._draw_topdown()
        else:
            self._draw_placeholder()

    def _draw_placeholder(self) -> None:
        print("DRIVE", 104, 30, Color.WHITE)
        print("mode=" + self._mode, 86, 40, Color.WHITE)
        print("view=" + self._variant, 82, 50, Color.WHITE)
        run = self._state.run
        if run is not None:
            print("fuel=" + str(round(run.car_fuel, 1)), 88, 60, Color.WHITE)
            print("hp=" + str(round(run.car_hp, 1)), 94, 70, Color.WHITE)

        logic = self._logic
        road = self._road
        if logic is not None and road is not None:
            self._ui.draw_steer_wheel(logic)
            self._ui.draw_slip_bar(logic)
            print("s=" + str(int(logic.road_s)) + "/" + str(int(road.segment_total_length)),
                  70, 82, Color.WHITE)
            print("d=" + str(round(logic.road_d, 2)), 90, 92, Color.WHITE)
            print("spd=" + str(round(logic.speed, 1)), 84, 102, Color.WHITE)
            if logic.offroad:
                print("OFFROAD", 96, 112, Color.RED)
            if logic.finished():
                print("Z = CONTINUE", 70, 122, Color.WHITE)
            else:
                print("UP/DOWN/LEFT/RIGHT + X", 68, 122, Color.WHITE)

    def _draw_topdown(self) -> None:
        """Top-down рендер DRIVE: дорога, зоны, препятствия, машина, подсказки."""
        logic = self._logic
        road = self._road
        run = self._state.run
        objects = self._objects
        if logic is None or road is None or run is None or objects is None:
            self._draw_placeholder()
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
            self._drive_debug_lines(road, logic, run, objects))
        return

    def _apply_zone_effects(self, z: DriveZone | None) -> None:
        """Применяет эффекты зоны к DriveLogic на следующий кадр.

        Вынесено в отдельный метод, чтобы не дублировать “если в зоне / если вне зоны”
        в нескольких местах (до и после `DriveLogic.update`).
        """
        logic = self._logic
        if logic is None:
            return
        if z is None:
            logic.set_zone_grip_mult(1.0)
            logic.set_zone_boost(0.0, 0.0)
            logic.set_zone_antislip(0.0)
            logic.set_zone_grip_floor(0.0)
            return

        logic.set_zone_grip_mult(z.grip_mult)
        logic.set_zone_boost(
            TUNING.DRIVE.zone_boost_forward_accel,
            TUNING.DRIVE.zone_boost_center_accel
        )
        logic.set_zone_antislip(TUNING.DRIVE.zone_antislip)
        logic.set_zone_grip_floor(TUNING.DRIVE.zone_grip_floor)

    def _drive_debug_lines(
        self,
        road: RoadModel,
        logic: DriveLogic,
        run: RunState,
        objects: DriveObjects
    ) -> list[str]:
        """Строки для DebugOverlay, чтобы HUD не накладывался на оверлей."""
        def f2(v: float) -> str:
            return f"{v:.2f}"

        vmax_road = logic.estimated_vmax_road()
        vmax_off = logic.estimated_vmax_offroad()

        lines = [
            "drive seed=" + str(run.seed) + " obs=" +
            str(objects.obstacles_count())
            + " zones=" + str(objects.zones_count()),
            "drive s=" + str(int(logic.road_s)) + "/" +
            str(int(road.segment_total_length)),
            "drive d=" + f2(logic.road_d),
            "drive v=" + f2(logic.v_forward) + " side=" + f2(logic.v_side),
            "drive spd=" + f2(logic.speed) + " vmax=" +
            f2(vmax_road) + "/" + f2(vmax_off),
            "drive surf=" + ("OFF" if logic.offroad else "ROAD")
            + " sf=" + f2(logic.dbg_speed_factor)
            + " ss=" + f2(logic.dbg_steer_scale)
            + " hb=" + f2(logic.dbg_handbrake_decel),
            "drive grip=" + f2(logic.dbg_effective_grip) +
            " damp=" + f2(logic.dbg_side_damp)
            + " rec=" + f2(logic.dbg_side_recovery)
            + " fuel/s=" + f2(logic.dbg_fuel_per_sec),
            "drive boost fwd=" + f2(logic.dbg_zone_boost_forward)
            + " ctr=" + f2(logic.dbg_zone_boost_center)
            + " as=" + f2(logic.dbg_zone_antislip),
            "drive fuel=" + f2(run.car_fuel),
            "drive hp=" + f2(run.car_hp)
        ]
        if logic.offroad:
            lines.append("drive OFFROAD")
        return lines

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
