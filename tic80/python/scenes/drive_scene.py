from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import btn, btnp, circb, cls, line, print, trace

    from ..contracts import (
        DriveEnterParams,
        ResultEnterParams,
        SceneNavigator,
        Tuning
    )
    from ..core.input_buttons import Button
    from ..core.run_state import RunState
    from ..core.scene_ids import SceneId
    from ..core.sprites import NIVA_TOPDOWN
    from ..data.tuning import TUNING
    from ..systems.drive.drive_logic import DriveLogic
    from ..systems.drive.drive_objects import DriveHazardZone, DriveObjects
    from ..systems.drive.road_model import RoadModel


class DriveTelemetry:
    """Сборщик телеметрии DRIVE для тюнинга и отладки.

    Держим это отдельным классом, чтобы DriveScene не превращалась в комбайн
    из логики + рендера + логгинга.

    Примечание про PocketPy: избегаем keyword-аргументов в вызовах (иногда ведут себя
    нестабильно), поэтому API сделан позиционным.
    """

    def __init__(self, every_frames: int, max_lines: int) -> None:
        self._every = int(every_frames)
        self._max = int(max_lines)
        self._lines: list[str] = []
        self._t = 0.0
        self._frame = 0
        self._offroad = False

    def begin(self, seed: int, mode: str, variant: str, tuning: Tuning) -> None:
        """Начинает новый лог для сегмента."""
        self._lines = []
        self._t = 0.0
        self._frame = 0
        self._offroad = False

        self._add("drive telem begin seed=" + str(seed) +
                  " mode=" + mode + " view=" + variant)

        d = tuning.DRIVE
        self._add(
            "drive telem tuning max_speed="
            + str(d.max_speed)
            + " accel="
            + str(d.accel)
            + " brake="
            + str(d.brake)
            + " coast="
            + str(d.coast_decel)
        )
        self._add(
            "drive telem tuning steer_rate="
            + str(d.steer_rate)
            + " ss_min="
            + str(d.steer_scale_min)
            + " ss_max="
            + str(d.steer_scale_max)
            + " slip_mult="
            + str(d.side_slip_speed_mult)
        )
        self._add(
            "drive telem tuning hb_decel="
            + str(d.handbrake_decel)
            + " hb_steer_mult="
            + str(d.handbrake_steer_mult)
            + " hb_grip_mult="
            + str(d.handbrake_grip_mult)
        )
        self._add(
            "drive telem tuning dash_impulse="
            + str(d.dash_impulse)
            + " dash_cd="
            + str(d.dash_cooldown)
        )

    def after_update(
        self,
        dt: float,
        steer: int,
        throttle: bool,
        brake: bool,
        handbrake: bool,
        dash_pressed: bool,
        run,
        logic
    ) -> None:
        """Сэмплирует телеметрию не каждый кадр и отмечает важные события."""
        self._t += dt
        self._frame += 1

        if logic.offroad != self._offroad:
            self._offroad = logic.offroad
            self._add(
                "t="
                + "{:.2f}".format(self._t)
                + " EVENT surf="
                + ("OFF" if logic.offroad else "ROAD")
                + " s="
                + str(int(logic.road_s))
                + " d="
                + "{:.2f}".format(logic.road_d)
            )

        if self._every <= 0:
            return
        if (self._frame % self._every) != 0:
            return

        self._add(
            "t="
            + "{:.2f}".format(self._t)
            + " s="
            + str(int(logic.road_s))
            + " d="
            + "{:.2f}".format(logic.road_d)
            + " v="
            + "{:.2f}".format(logic.v_forward)
            + " side="
            + "{:.2f}".format(logic.v_side)
            + " spd="
            + "{:.2f}".format(logic.speed)
            + " steer="
            + str(steer)
            + " thr="
            + ("1" if throttle else "0")
            + " brk="
            + ("1" if brake else "0")
            + " hb="
            + ("1" if handbrake else "0")
            + " dash="
            + ("1" if dash_pressed else "0")
            + " ss="
            + "{:.2f}".format(logic.dbg_steer_scale)
            + " grip="
            + "{:.2f}".format(logic.dbg_effective_grip)
            + " damp="
            + "{:.2f}".format(logic.dbg_side_damp)
            + " surf="
            + ("OFF" if logic.offroad else "ROAD")
            + " fuel="
            + "{:.2f}".format(run.car_fuel)
            + " hp="
            + "{:.2f}".format(run.car_hp)
        )

    def dump(self, reason: str) -> None:
        """Печатает накопленный лог в консоль через `trace`."""
        trace("drive telem dump reason=" + reason +
              " lines=" + str(len(self._lines)))
        i = 0
        while i < len(self._lines):
            trace(self._lines[i])
            i += 1
        trace("drive telem end")
        self._lines = []

    def _add(self, line: str) -> None:
        if self._max > 0 and len(self._lines) >= self._max:
            return
        self._lines.append(line)


class DriveTopdownRenderer:
    """Рендер DRIVE в варианте A (top-down).

    Задача класса: только рисовать. Никаких изменений состояния RunState/DriveLogic.
    """

    def draw(self, road, logic, objects) -> None:
        """Рисует дорогу, опасные зоны, препятствия и машину в top-down."""
        center_x = 120
        center_y = int(TUNING.DRIVE.view_center_y)
        if center_y < 40:
            center_y = 40
        if center_y > 120:
            center_y = 120

        p_s = logic.road_s
        car_x = logic.x
        car_y = logic.y
        fwd_x = logic.fwd_x
        fwd_y = logic.fwd_y
        right_x = -fwd_y
        right_y = fwd_x

        n = road.center_points_len()
        d = TUNING.DRIVE
        start_s = p_s - d.render_back_s
        end_s = p_s + d.render_forward_s
        start = int(start_s / road.ds)
        end = int(end_s / road.ds)
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

            lx = cx - nrm_x * half
            ly = cy - nrm_y * half
            rx = cx + nrm_x * half
            ry = cy + nrm_y * half

            lsx, lsy = self._world_to_screen(
                lx, ly, car_x, car_y, fwd_x, fwd_y, right_x, right_y, center_x, center_y
            )
            rsx, rsy = self._world_to_screen(
                rx, ry, car_x, car_y, fwd_x, fwd_y, right_x, right_y, center_x, center_y
            )

            if prev_lsx is not None and prev_lsy is not None:
                line(int(prev_lsx), int(prev_lsy), int(lsx), int(lsy), 5)
            if prev_rsx is not None and prev_rsy is not None:
                line(int(prev_rsx), int(prev_rsy), int(rsx), int(rsy), 5)

            span = self._zone_span_at_s(i * road.ds, zones)
            if span is not None:
                d0, d1 = span
                if d0 < -half:
                    d0 = -half
                if d0 > half:
                    d0 = half
                if d1 < -half:
                    d1 = -half
                if d1 > half:
                    d1 = half
                zx0 = cx + nrm_x * d0
                zy0 = cy + nrm_y * d0
                zx1 = cx + nrm_x * d1
                zy1 = cy + nrm_y * d1
                zsx0, zsy0 = self._world_to_screen(
                    zx0, zy0, car_x, car_y, fwd_x, fwd_y, right_x, right_y, center_x, center_y
                )
                zsx1, zsy1 = self._world_to_screen(
                    zx1, zy1, car_x, car_y, fwd_x, fwd_y, right_x, right_y, center_x, center_y
                )
                line(int(zsx0), int(zsy0), int(zsx1), int(zsy1), 4)

            prev_lsx = lsx
            prev_lsy = lsy
            prev_rsx = rsx
            prev_rsy = rsy
            i += 1

        obstacles = objects.obstacles_items()
        self._draw_obstacles(obstacles, road, p_s, car_x, car_y, fwd_x, fwd_y,
                             right_x, right_y, center_x, center_y)

        ax = int(TUNING.DRIVE.car_sprite_anchor_x)
        ay = int(TUNING.DRIVE.car_sprite_anchor_y)
        NIVA_TOPDOWN.draw(logic.steer_input, center_x - ax, center_y - ay)
        if TUNING.DRIVE.debug_vectors_enabled:
            self._draw_debug_vectors(logic, center_x, center_y)

    def _zone_span_at_s(self, s: float, zones) -> tuple[float, float] | None:
        """Возвращает (d0, d1) для подсветки HazardZone на прогрессе `s`."""
        i = 0
        while i < len(zones):
            z = zones[i]
            if s >= z.s_start and s <= z.s_end:
                return (z.d_center - z.radius, z.d_center + z.radius)
            i += 1
        return None

    def _draw_obstacles(
        self,
        obstacles,
        road,
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

    def _draw_debug_vectors(self, logic, cx: int, cy: int) -> None:
        """Рисует диагностические векторы из центра машины (heading/velocity/side accel)."""
        d = TUNING.DRIVE
        h = d.debug_vectors_heading_len
        if h < 0.0:
            h = 0.0
        if h > 60.0:
            h = 60.0

        vel_scale = d.debug_vectors_vel_scale
        accel_scale = d.debug_vectors_accel_scale

        line(cx, cy, cx, int(cy - h), 12)

        vx = logic.v_side * vel_scale
        vy = -logic.v_forward * vel_scale
        if vx > 60.0:
            vx = 60.0
        if vx < -60.0:
            vx = -60.0
        if vy > 60.0:
            vy = 60.0
        if vy < -60.0:
            vy = -60.0
        line(cx, cy, int(cx + vx), int(cy + vy), 11)

        ax = logic.dbg_side_accel * accel_scale
        if ax > 60.0:
            ax = 60.0
        if ax < -60.0:
            ax = -60.0
        line(cx, cy, int(cx + ax), cy, 14)


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
        self._telemetry: DriveTelemetry | None = None
        self._renderer = DriveTopdownRenderer()

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
        if self._objects is None:
            return

        zones = self._objects.hazard_zones_items()
        z_before = self._zone_at(self._logic.road_s, self._logic.road_d, zones)
        if z_before is None:
            self._logic.set_hazard_grip_mult(1.0)
        else:
            self._logic.set_hazard_grip_mult(z_before.grip_mult)

        steer = 0
        if btn(Button.LEFT):
            steer -= 1
        if btn(Button.RIGHT):
            steer += 1

        throttle = btn(Button.UP)
        brake = btn(Button.DOWN)
        handbrake = btn(Button.B)
        a_pressed = btnp(Button.A)

        dash_pressed = a_pressed and not self._logic.finished()
        self._logic.update(dt, steer, throttle, brake, handbrake, dash_pressed)
        z_after = self._zone_at(self._logic.road_s, self._logic.road_d, zones)

        z_damage = z_before if z_before is not None else z_after
        if z_damage is not None and z_damage.tick_damage > 0.0:
            run.apply_damage(z_damage.tick_damage * dt)

        if z_after is None:
            self._logic.set_hazard_grip_mult(1.0)
        else:
            self._logic.set_hazard_grip_mult(z_after.grip_mult)
        if self._telemetry is not None:
            self._telemetry.after_update(
                dt, steer, throttle, brake, handbrake, dash_pressed, run, self._logic
            )

        if not self._evacuated:
            if run.car_fuel <= 0:
                self._evacuate(run, "OUT OF FUEL")
                return
            if run.car_hp <= 0:
                self._evacuate(run, "CAR DESTROYED")
                return

        if self._logic.finished() and a_pressed:
            if self._telemetry is not None:
                self._telemetry.dump("finish")
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
            print("s=" + str(int(logic.road_s)) + "/" + str(int(road.segment_total_length)),
                  70, 82, 12)
            print("d=" + str(round(logic.road_d, 2)), 90, 92, 12)
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

        # Рендер держим отдельно от сцены, чтобы позже легко подключить второй вид (cockpit)
        # и не раздувать DriveScene.
        self._renderer.draw(road, logic, objects)
        if logic.finished():
            print("A = CONTINUE", 2, 128, 12)
        else:
            print("UP/DN/LR + B", 2, 128, 12)
        self._state.set_debug_lines(
            self._drive_debug_lines(road, logic, run, objects))
        return

    def _zone_at(
        self,
        logic_s: float,
        logic_d: float,
        zones: list["DriveHazardZone"]
    ):
        """Возвращает HazardZone, в которой находится машина (если есть).

        Здесь используем и s, и d: если мы попали в диапазон по s И достаточно близко
        к центру зоны по d, тогда считается, что эффект активен.
        """
        i = 0
        while i < len(zones):
            z = zones[i]
            if logic_s >= z.s_start and logic_s <= z.s_end:
                if abs(logic_d - z.d_center) <= z.radius:
                    return z
            i += 1
        return None

    def _drive_debug_lines(
        self,
        road: RoadModel,
        logic: DriveLogic,
        run: RunState,
        objects: DriveObjects
    ) -> list[str]:
        """Строки для DebugOverlay, чтобы HUD не накладывался на оверлей."""
        def f2(v: float) -> str:
            return "{:.2f}".format(v)

        vmax_road = logic.estimated_vmax_road()
        vmax_off = logic.estimated_vmax_offroad()

        lines = [
            "drive seed=" + str(run.seed) + " obs=" +
            str(objects.obstacles_count())
            + " zones=" + str(objects.hazard_zones_count()),
            "drive s=" + str(int(logic.road_s)) + "/" +
            str(int(road.segment_total_length)),
            "drive d=" + f2(logic.road_d),
            "drive v=" + f2(logic.v_forward) + " side=" + f2(logic.v_side),
            "drive spd=" + f2(logic.speed) + " vmax=" +
            f2(vmax_road) + "/" + f2(vmax_off),
            "drive surf=" + ("OFF" if logic.offroad else "ROAD")
            + " sf=" + f2(logic.dbg_speed_factor)
            + " ss=" + f2(logic.dbg_steer_scale),
            "drive grip=" + f2(logic.dbg_effective_grip) +
            " damp=" + f2(logic.dbg_side_damp)
            + " fuel/s=" + f2(logic.dbg_fuel_per_sec),
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
