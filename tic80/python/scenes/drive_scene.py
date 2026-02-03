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
    from ..systems.drive.drive_objects import DriveObjects, DriveObstacle, DriveZone
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
        run: RunState,
        logic: DriveLogic
    ) -> None:
        """Сэмплирует телеметрию не каждый кадр и отмечает важные события."""
        self._t += dt
        self._frame += 1

        if logic.offroad != self._offroad:
            self._offroad = logic.offroad
            self._add(
                "t="
                + f"{self._t:.2f}"
                + " EVENT surf="
                + ("OFF" if logic.offroad else "ROAD")
                + " s="
                + str(int(logic.road_s))
                + " d="
                + f"{logic.road_d:.2f}"
            )

        if self._every <= 0:
            return
        if (self._frame % self._every) != 0:
            return

        self._add(
            "t="
            + f"{self._t:.2f}"
            + " s="
            + str(int(logic.road_s))
            + " d="
            + f"{logic.road_d:.2f}"
            + " v="
            + f"{logic.v_forward:.2f}"
            + " side="
            + f"{logic.v_side:.2f}"
            + " spd="
            + f"{logic.speed:.2f}"
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
            + f"{logic.dbg_steer_scale:.2f}"
            + " grip="
            + f"{logic.dbg_effective_grip:.2f}"
            + " damp="
            + f"{logic.dbg_side_damp:.2f}"
            + " surf="
            + ("OFF" if logic.offroad else "ROAD")
            + " fuel="
            + f"{run.car_fuel:.2f}"
            + " hp="
            + f"{run.car_hp:.2f}"
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

    def draw(
        self,
        road: RoadModel,
        logic: DriveLogic,
        objects: DriveObjects,
        active_zone: DriveZone | None
    ) -> None:
        """Рисует дорогу, опасные зоны, препятствия и машину в top-down.

        Этот метод намеренно короткий: “скелет” кадра.
        Детали вынесены в приватные методы, чтобы было легче дорабатывать и ревьюить.
        """
        center_x = 120
        center_y = self._clamp_center_y(int(TUNING.DRIVE.view_center_y))

        p_s = logic.road_s
        car_x = logic.x
        car_y = logic.y
        fwd_x = logic.fwd_x
        fwd_y = logic.fwd_y
        right_x = -fwd_y
        right_y = fwd_x

        start_idx, end_idx = self._visible_index_range(road, p_s)
        zones = objects.zones_items()
        self._draw_road_edges_and_hazards(
            road,
            zones,
            start_idx,
            end_idx,
            car_x,
            car_y,
            fwd_x,
            fwd_y,
            right_x,
            right_y,
            center_x,
            center_y
        )
        if TUNING.DRIVE.debug_zones_enabled:
            i = 0
            while i < len(zones):
                z = zones[i]
                color = 6
                if active_zone is not None and z is active_zone:
                    color = 12
                self._draw_zone_outline(
                    road,
                    z,
                    start_idx,
                    end_idx,
                    car_x,
                    car_y,
                    fwd_x,
                    fwd_y,
                    right_x,
                    right_y,
                    center_x,
                    center_y,
                    color
                )
                i += 1

        obstacles = objects.obstacles_items()
        self._draw_obstacles(
            obstacles,
            road,
            p_s,
            car_x,
            car_y,
            fwd_x,
            fwd_y,
            right_x,
            right_y,
            center_x,
            center_y
        )

        self._draw_car_sprite(logic.steer_input, center_x, center_y)
        if TUNING.DRIVE.debug_vectors_enabled:
            self._draw_debug_vectors(logic, center_x, center_y)
        if TUNING.DRIVE.debug_hitboxes_enabled:
            self._draw_hitboxes(logic.steer_input, center_x, center_y)

    def _draw_zone_outline(
        self,
        road: RoadModel,
        z: DriveZone,
        start_idx: int,
        end_idx: int,
        car_x: float,
        car_y: float,
        fwd_x: float,
        fwd_y: float,
        right_x: float,
        right_y: float,
        center_x: int,
        center_y: int,
        color: int
    ) -> None:
        """Рисует контур активной зоны (для дебага коллизии).

        Полоски зон рисуются “внутри” дороги (см. `_draw_hazard_stripe_at`).
        Этот контур показывает именно геометрию зоны в road-space:
        - s в [s_start..s_end]
        - d в [d_center-radius .. d_center+radius]

        Если контур не совпадает с ощущением коллизии — значит проблема в проекции
        world -> (s,d) или в настройке хитбоксов.
        """
        s_vis0 = start_idx * road.ds
        s_vis1 = end_idx * road.ds
        s0 = z.s_start
        s1 = z.s_end
        if s0 < s_vis0:
            s0 = s_vis0
        if s1 > s_vis1:
            s1 = s_vis1
        if s1 <= s0:
            return

        d0 = z.d_center - z.radius
        d1 = z.d_center + z.radius

        step = road.ds * 2.0
        if step < road.ds:
            step = road.ds

        prev0x = None
        prev0y = None
        prev1x = None
        prev1y = None

        s = s0
        while s <= s1:
            cx, cy = road.sample_centerline(s)
            dx, dy = road.direction_at(s)
            nrm_x = -dy
            nrm_y = dx

            wx0 = cx + nrm_x * d0
            wy0 = cy + nrm_y * d0
            wx1 = cx + nrm_x * d1
            wy1 = cy + nrm_y * d1

            sx0, sy0 = self._world_to_screen(
                wx0, wy0, car_x, car_y, fwd_x, fwd_y, right_x, right_y, center_x, center_y
            )
            sx1, sy1 = self._world_to_screen(
                wx1, wy1, car_x, car_y, fwd_x, fwd_y, right_x, right_y, center_x, center_y
            )

            if prev0x is not None and prev0y is not None:
                line(int(prev0x), int(prev0y), int(sx0), int(sy0), color)
            if prev1x is not None and prev1y is not None:
                line(int(prev1x), int(prev1y), int(sx1), int(sy1), color)

            prev0x = sx0
            prev0y = sy0
            prev1x = sx1
            prev1y = sy1
            s += step

        # “Заглушки” на концах (перемычки), чтобы визуально получался прямоугольник.
        if prev0x is not None and prev0y is not None and prev1x is not None and prev1y is not None:
            line(int(prev0x), int(prev0y), int(prev1x), int(prev1y), color)
        cx0, cy0 = road.sample_centerline(s0)
        dx0, dy0 = road.direction_at(s0)
        nrm0x = -dy0
        nrm0y = dx0
        wx0a = cx0 + nrm0x * d0
        wy0a = cy0 + nrm0y * d0
        wx1a = cx0 + nrm0x * d1
        wy1a = cy0 + nrm0y * d1
        sx0a, sy0a = self._world_to_screen(
            wx0a, wy0a, car_x, car_y, fwd_x, fwd_y, right_x, right_y, center_x, center_y
        )
        sx1a, sy1a = self._world_to_screen(
            wx1a, wy1a, car_x, car_y, fwd_x, fwd_y, right_x, right_y, center_x, center_y
        )
        line(int(sx0a), int(sy0a), int(sx1a), int(sy1a), color)

    def _clamp_center_y(self, y: int) -> int:
        """Ограничивает вертикальную позицию “центра камеры” в top-down.

        Зачем clamp:
        - не даём машине уехать слишком вниз (спрайт начнёт обрезаться);
        - не даём поставить камеру слишком вверх (мало дороги впереди).

        Всё это вынесено в tuning, чтобы легко подбирать ощущение кадра.
        """
        d = TUNING.DRIVE
        y_min = int(d.view_center_y_min)
        y_max = int(d.view_center_y_max)
        if y < y_min:
            return y_min
        if y > y_max:
            return y_max
        return y

    def _visible_index_range(self, road: RoadModel, p_s: float) -> tuple[int, int]:
        """Возвращает диапазон индексов centerline для отрисовки вокруг `p_s`."""
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
        return start, end

    def _draw_road_edges_and_hazards(
        self,
        road: RoadModel,
        zones: list[DriveZone],
        start_idx: int,
        end_idx: int,
        car_x: float,
        car_y: float,
        fwd_x: float,
        fwd_y: float,
        right_x: float,
        right_y: float,
        center_x: int,
        center_y: int
    ) -> None:
        """Рисует границы дороги и “полоски” HazardZone в top-down."""
        prev_lsx = None
        prev_lsy = None
        prev_rsx = None
        prev_rsy = None

        i = start_idx
        while i <= end_idx:
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

            self._draw_hazard_stripe_at(
                road,
                zones,
                i,
                cx,
                cy,
                nrm_x,
                nrm_y,
                half,
                car_x,
                car_y,
                fwd_x,
                fwd_y,
                right_x,
                right_y,
                center_x,
                center_y
            )

            prev_lsx = lsx
            prev_lsy = lsy
            prev_rsx = rsx
            prev_rsy = rsy
            i += 1

    def _draw_hazard_stripe_at(
        self,
        road: RoadModel,
        zones: list[DriveZone],
        idx: int,
        cx: float,
        cy: float,
        nrm_x: float,
        nrm_y: float,
        half: float,
        car_x: float,
        car_y: float,
        fwd_x: float,
        fwd_y: float,
        right_x: float,
        right_y: float,
        center_x: int,
        center_y: int
    ) -> None:
        """Рисует одну “полоску” опасной зоны поперёк дороги, если она активна в этой точке."""
        span = self._zone_span_at_s(idx * road.ds, zones)
        if span is None:
            return

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

    def _draw_car_sprite(self, steer_input: int, center_x: int, center_y: int) -> None:
        """Рисует спрайт машины в точке (center_x, center_y) с учётом anchor."""
        ax = int(TUNING.DRIVE.car_sprite_anchor_x)
        ay = int(TUNING.DRIVE.car_sprite_anchor_y)
        NIVA_TOPDOWN.draw(steer_input, center_x - ax, center_y - ay)

    def _draw_hitboxes(self, steer_input: int, center_x: int, center_y: int) -> None:
        """Рисует 2 круговых хитбокса машины (передняя/задняя ось) в top-down.

        Важно: в top-down камера “крутит мир” под машиной, поэтому в экранных
        координатах ось fwd всегда направлена вверх, а right — вправо.

        Это значит, что локальные оффсеты по fwd/right можно рисовать напрямую,
        без пересчёта в world-space.
        """
        d = TUNING.DRIVE

        # Координаты хитбоксов задаются в пикселях спрайта и “приклеиваются” к нему
        # через car_sprite_anchor_*.
        #
        # Экранные центры кругов = (центр машины на экране) + (hitbox_px - anchor_x),
        # аналогично по Y.
        ax = d.car_sprite_anchor_x
        ay = d.car_sprite_anchor_y

        steer_sign = 0.0
        steer_abs = 0.0
        if steer_input < 0:
            steer_sign = -1.0
            steer_abs = 1.0
        elif steer_input > 0:
            steer_sign = 1.0
            steer_abs = 1.0

        rear_px = d.hitbox_rear_px
        rear_py = d.hitbox_rear_py
        front_px = d.hitbox_front_px
        front_py = d.hitbox_front_py

        # Для поворотного кадра добавляем сдвиг. Влево/вправо — зеркалим по X.
        if steer_abs > 0.0:
            rear_px += steer_sign * d.hitbox_turn_rear_dx
            rear_py += steer_abs * d.hitbox_turn_rear_dy
            front_px += steer_sign * d.hitbox_turn_front_dx
            front_py += steer_abs * d.hitbox_turn_front_dy

        rear_r = d.hitbox_rear_radius
        front_r = d.hitbox_front_radius
        if rear_r < 0.0:
            rear_r = 0.0
        if front_r < 0.0:
            front_r = 0.0

        rear_x = center_x + (rear_px - ax)
        rear_y = center_y + (rear_py - ay)
        front_x = center_x + (front_px - ax)
        front_y = center_y + (front_py - ay)

        # Цвета: задняя ось — голубой (11), передняя — белый (12).
        if rear_r > 0.0:
            circb(int(rear_x), int(rear_y), int(rear_r), 11)
        if front_r > 0.0:
            circb(int(front_x), int(front_y), int(front_r), 12)

    def _zone_span_at_s(self, s: float, zones: list[DriveZone]) -> tuple[float, float] | None:
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
        obstacles: list[DriveObstacle],
        road: RoadModel,
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
        d = TUNING.DRIVE
        max_ds = d.obstacle_render_range_s
        if max_ds < 0.0:
            max_ds = 0.0
        i = 0
        while i < len(obstacles):
            o = obstacles[i]
            if o.hit:
                i += 1
                continue
            if abs(o.s - p_s) > max_ds:
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

    def _draw_debug_vectors(self, logic: DriveLogic, cx: int, cy: int) -> None:
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
        self._active_zone: DriveZone | None = None
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
        self._active_zone = None

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
        if self._road is None:
            return
        if self._objects is None:
            return

        zones = self._objects.zones_items()
        z_before = self._zone_at_hitboxes(self._logic, zones)
        self._apply_zone_effects(z_before)

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
        z_after = self._zone_at_hitboxes(self._logic, zones)
        self._active_zone = z_after if z_after is not None else z_before

        self._apply_obstacle_hits(run)

        # Обновляем эффекты зон для СЛЕДУЮЩЕГО кадра (без 1-кадрового “залипания”).
        self._apply_zone_effects(z_after)
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

    def _apply_obstacle_hits(self, run: RunState) -> None:
        """Проверяет столкновения с препятствиями и применяет урон.

        Коллизия:
        - препятствие = круг (radius) в world-space,
        - машина = 2 круга (задняя/передняя ось), позиции берём из DriveLogic.
        """
        road = self._road
        logic = self._logic
        objects = self._objects
        if road is None or logic is None or objects is None:
            return

        dmg = TUNING.DRIVE.obstacle_hit_damage
        if dmg <= 0.0:
            return

        rear_x, rear_y, rear_r, front_x, front_y, front_r = logic.hitbox_world_circles()

        # Небольшая оптимизация: проверяем только препятствия рядом по s.
        max_ds = TUNING.DRIVE.obstacle_render_range_s
        if max_ds < 0.0:
            max_ds = 0.0
        p_s = logic.road_s

        obstacles = objects.obstacles_items()
        i = 0
        while i < len(obstacles):
            o = obstacles[i]
            if o.hit:
                i += 1
                continue
            if abs(o.s - p_s) > max_ds:
                i += 1
                continue

            cx, cy = road.sample_centerline(o.s)
            dx, dy = road.direction_at(o.s)
            nrm_x = -dy
            nrm_y = dx
            ox = cx + nrm_x * o.d
            oy = cy + nrm_y * o.d

            r0 = o.radius + rear_r
            r1 = o.radius + front_r
            hit = False

            if r0 > 0.0:
                vx = ox - rear_x
                vy = oy - rear_y
                if (vx * vx + vy * vy) <= (r0 * r0):
                    hit = True
            if not hit and r1 > 0.0:
                vx = ox - front_x
                vy = oy - front_y
                if (vx * vx + vy * vy) <= (r1 * r1):
                    hit = True

            if hit:
                o.hit = True
                run.apply_damage(dmg)

            i += 1

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
        self._renderer.draw(road, logic, objects, self._active_zone)
        if logic.finished():
            print("A = CONTINUE", 2, 128, 12)
        else:
            print("UP/DN/LR + B", 2, 128, 12)
        self._state.set_debug_lines(
            self._drive_debug_lines(road, logic, run, objects))
        return

    def _zone_at_hitboxes(self, logic: DriveLogic, zones: list[DriveZone]) -> DriveZone | None:
        """Возвращает зону, которая пересекается с хитбоксом машины (если есть).

        Почему так:
        - игрок ориентируется по спрайту;
        - у машины уже есть 2 круговых хитбокса (перед/зад), настроенные под спрайт;
        - если проверять зону только по “центральной точке физики”, игрок будет видеть
          “я на полосках, но эффекта нет”.

        Реализация:
        - берём 2 круга машины в road-space (`DriveLogic.hitbox_road_circles`);
        - каждая зона — прямоугольник в (s,d):
            s in [s_start..s_end]
            d in [d_center-radius .. d_center+radius]
        - проверяем пересечение круга и прямоугольника (circle-vs-AABB в road-space).
        """
        def clamp(v: float, lo: float, hi: float) -> float:
            if v < lo:
                return lo
            if v > hi:
                return hi
            return v

        rear_s, rear_d, rear_r, front_s, front_d, front_r = logic.hitbox_road_circles()
        circles = [
            (rear_s, rear_d, rear_r),
            (front_s, front_d, front_r)
        ]

        j = 0
        while j < len(circles):
            ps, pd, pr = circles[j]
            if pr <= 0.0:
                j += 1
                continue

            i = 0
            while i < len(zones):
                z = zones[i]
                zs0 = z.s_start
                zs1 = z.s_end
                zd0 = z.d_center - z.radius
                zd1 = z.d_center + z.radius

                cs = clamp(ps, zs0, zs1)
                cd = clamp(pd, zd0, zd1)
                ds = ps - cs
                dd = pd - cd
                if (ds * ds + dd * dd) <= (pr * pr):
                    return z
                i += 1

            j += 1

        return None

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
            + " ss=" + f2(logic.dbg_steer_scale),
            "drive grip=" + f2(logic.dbg_effective_grip) +
            " damp=" + f2(logic.dbg_side_damp)
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
