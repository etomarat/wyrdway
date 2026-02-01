from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import btn, btnp, circb, cls, line, print

    from ..contracts import DriveEnterParams, ResultEnterParams, SceneNavigator
    from ..core.input_buttons import Button
    from ..core.sprites import NIVA_TOPDOWN
    from ..core.run_state import RunState
    from ..core.scene_ids import SceneId
    from ..data.tuning import TUNING
    from ..systems.drive.drive_logic import DriveLogic
    from ..systems.drive.drive_objects import (
        DriveHazardZone,
        DriveObjects,
        DriveObstacle
    )
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
        self._objects: DriveObjects | None = None
        self._evacuated = False

    def enter(self, params: object | None = None) -> None:
        if not isinstance(params, DriveEnterParams):
            raise TypeError("DriveScene.enter expects DriveEnterParams")
        self._mode = params.mode
        self._variant = params.variant
        self._evacuated = False
        self._road = None
        self._logic = None
        self._objects = None

        run = self._state.require_run()
        seed = run.seed
        self._road = RoadModel.from_tuning(seed, TUNING)
        self._logic = DriveLogic(run, self._road, TUNING)
        self._objects = DriveObjects.from_road_and_tuning(
            seed, self._road, TUNING)

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
        if self._variant == "topdown":
            self._draw_topdown()
        else:
            self._draw_placeholder()

    def _draw_placeholder(self) -> None:
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

    def _draw_topdown(self) -> None:
        """Top-down рендер DRIVE: дорога, зоны, препятствия, машина, подсказки."""
        logic = self._logic
        road = self._road
        run = self._state.run
        objects = self._objects
        if logic is None or road is None or run is None or objects is None:
            self._draw_placeholder()
            return

        center_x = 120
        center_y = 68

        p_s = logic.s
        p_x, p_y = road.sample_centerline(p_s)
        fwd_x, fwd_y = road.direction_at(p_s)
        right_x = -fwd_y
        right_y = fwd_x
        car_x = p_x + right_x * logic.d
        car_y = p_y + right_y * logic.d

        n = road.center_points_len()
        idx = int(p_s / road.ds)
        start = idx - 20
        end = idx + 60
        if start < 0:
            start = 0
        if end > n - 1:
            end = n - 1

        i = start
        prev_lsx = None
        prev_lsy = None
        prev_rsx = None
        prev_rsy = None
        zones = objects.hazard_zones_items()
        while i <= end:
            cx, cy, dir_x, dir_y = road.center_point_at_index(i)
            half = road.width_at(i * road.ds) * 0.5
            nrm_x = -dir_y
            nrm_y = dir_x

            lx = cx + nrm_x * half
            ly = cy + nrm_y * half
            rx = cx - nrm_x * half
            ry = cy - nrm_y * half

            lsx, lsy = self._world_to_screen(
                lx, ly, car_x, car_y, fwd_x, fwd_y, right_x, right_y, center_x, center_y
            )
            rsx, rsy = self._world_to_screen(
                rx, ry, car_x, car_y, fwd_x, fwd_y, right_x, right_y, center_x, center_y
            )

            in_zone = self._in_any_zone(i * road.ds, zones)

            if prev_lsx is not None and prev_lsy is not None:
                col = 5
                if in_zone:
                    col = 4
                line(int(prev_lsx), int(prev_lsy), int(lsx), int(lsy), col)
            if prev_rsx is not None and prev_rsy is not None:
                col = 5
                if in_zone:
                    col = 4
                line(int(prev_rsx), int(prev_rsy), int(rsx), int(rsy), col)

            if in_zone:
                line(int(lsx), int(lsy), int(rsx), int(rsy), 4)

            prev_lsx = lsx
            prev_lsy = lsy
            prev_rsx = rsx
            prev_rsy = rsy
            i += 1

        obstacles = objects.obstacles_items()
        self._draw_obstacles(obstacles, road, p_s, car_x, car_y, fwd_x, fwd_y,
                              right_x, right_y, center_x, center_y)

        NIVA_TOPDOWN.draw(logic.steer_input, center_x - 16, center_y - 16)

        if logic.finished():
            print("A = CONTINUE", 2, 124, 12)
        else:
            print("UP/DN/LR + B", 2, 124, 12)
        self._state.set_debug_lines(self._drive_debug_lines(road, logic, run, objects))

    def _in_any_zone(self, s: float, zones: list["DriveHazardZone"]) -> bool:
        """True, если прогресс `s` попадает в любую HazardZone."""
        i = 0
        while i < len(zones):
            z = zones[i]
            if s >= z.s_start and s <= z.s_end:
                return True
            i += 1
        return False

    def _draw_obstacles(
        self,
        obstacles: list["DriveObstacle"],
        road: "RoadModel",
        p_s: float,
        p_x: float,
        p_y: float,
        fwd_x: float,
        fwd_y: float,
        right_x: float,
        right_y: float,
        center_x: int,
        center_y: int
    ) -> None:
        """Рисует препятствия (пока как кружки) в top-down проекции."""
        i = 0
        while i < len(obstacles):
            o = obstacles[i]
            if o.hit:
                i += 1
                continue

            if abs(o.s - p_s) > 140.0:
                i += 1
                continue

            cx, cy = road.sample_centerline(o.s)
            dx, dy = road.direction_at(o.s)
            nrm_x = -dy
            nrm_y = dx

            wx = cx + nrm_x * o.d
            wy = cy + nrm_y * o.d
            sx, sy = self._world_to_screen(
                wx, wy, p_x, p_y, fwd_x, fwd_y, right_x, right_y, center_x, center_y
            )
            circb(int(sx), int(sy), int(o.radius), 2)
            i += 1

    def _drive_debug_lines(
        self,
        road: RoadModel,
        logic: DriveLogic,
        run: RunState,
        objects: DriveObjects
    ) -> list[str]:
        """Строки для DebugOverlay, чтобы HUD не накладывался на оверлей."""
        lines = [
            "drive seed=" + str(run.seed) + " obs=" + str(objects.obstacles_count())
            + " zones=" + str(objects.hazard_zones_count()),
            "drive s=" + str(int(logic.s)) + "/" + str(int(road.segment_total_length)),
            "drive d=" + str(round(logic.d, 2)),
            "drive spd=" + str(round(logic.speed, 1)),
            "drive fuel=" + str(round(run.car_fuel, 1)),
            "drive hp=" + str(round(run.car_hp, 1))
        ]
        if logic.offroad:
            lines.append("drive OFFROAD")
        return lines

    def _world_to_screen(
        self,
        wx: float,
        wy: float,
        px: float,
        py: float,
        fwd_x: float,
        fwd_y: float,
        right_x: float,
        right_y: float,
        sx0: int,
        sy0: int
    ) -> tuple[float, float]:
        """Проецирует (wx, wy) в экран в системе игрока (px, py, fwd/right)."""
        vx = wx - px
        vy = wy - py
        local_fwd = vx * fwd_x + vy * fwd_y
        local_right = vx * right_x + vy * right_y
        sx = sx0 + local_right
        sy = sy0 - local_fwd
        return sx, sy

    def exit(self) -> None:
        pass

    def _evacuate(self, run: RunState, reason: str) -> None:
        delta = run.ensure_delta(run.node_id)
        delta.set_escape_outcome("fail")
        self._evacuated = True
        self._nav.go(SceneId.RESULT, ResultEnterParams(reason))


def make_drive_scene(nav: SceneNavigator) -> DriveScene:
    return DriveScene(nav)
