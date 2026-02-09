from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import circb, line, rect, rectb, spr

    from ...core.palette import Color, ColorId
    from ...core.sprites import NIVA_TOPDOWN
    from ...data.tuning import TUNING
    from ...systems.drive.drive_logic_core import DriveLogic
    from ...systems.drive.drive_objects import (
        DriveObjects,
        DriveObstacle,
        DriveZone
    )
    from ...systems.drive.fx_particles import Particles2D
    from ...systems.drive.drive_fx import DriveFx, TopdownProjector
    from ...systems.drive.road_model import RoadModel
    from ...systems.fx.vendor.vand_particles import VandParticles


class DriveTopdownRenderer:
    """Рендер DRIVE в варианте A (top-down).

    Задача класса: только рисовать. Никаких изменений состояния RunState/DriveLogic.
    """

    def __init__(self) -> None:
        # Короткий буфер “следов” (skid marks), чтобы занос читался без поворота спрайта.
        self._skids: list[tuple[float, float, float, float, int]] = []
        self._fx = Particles2D(TUNING.DRIVE.fx_particles_max)
        # Вспышки искр при переходе “дорога <-> оффроад” должны читаться поверх пыли.
        self._fx_transition = Particles2D(40)
        self._drive_fx = DriveFx(TUNING)
        self._offroad_smoke = VandParticles(1337)
        self._exhaust_smoke = VandParticles(2469)
        self._prev_fwd_x = 0.0
        self._prev_fwd_y = 1.0
        self._prev_speed = 0.0
        self._prev_offroad = False
        self._offroad_side_sign = 1
        self._offroad_transition_cooldown = 0.0
        self._start_skid_t = 0.0
        self._fx_spawn_accum_off = 0.0
        self._fx_spawn_accum_speed = 0.0
        self._fx_spawn_accum_off_smoke = 0.0
        self._fx_spawn_accum_exhaust = 0.0
        self._fx_seed = 1
        self._hit_events: list[tuple[float, float, float, float, float,
                                      float]] = []

    def notify_obstacle_hit(
        self,
        contact_wx: float,
        contact_wy: float,
        normal_x: float,
        normal_y: float,
        impact: float,
        damage: float,
        hitbox_radius: float
    ) -> None:
        # Ударные эффекты обрабатываем в draw(), когда у нас есть актуальная проекция world->screen.
        self._hit_events.append((contact_wx, contact_wy, normal_x, normal_y, impact, hitbox_radius))

    def draw(
        self,
        road: RoadModel,
        logic: DriveLogic,
        objects: DriveObjects,
        active_zone: DriveZone | None
    ) -> None:
        """Рисует дорогу, зоны/полосы, препятствия и машину в top-down.

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

        proj = TopdownProjector(car_x, car_y, fwd_x, fwd_y, center_x, center_y)

        start_idx, end_idx = self._visible_index_range(road, p_s)
        zones = objects.zones_items_view()
        self._draw_road_edges_and_zones(
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
                color = Color.GREEN
                if active_zone is not None and z is active_zone:
                    color = Color.WHITE
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

        obstacles = objects.obstacles_items_view()
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

        # FX/следы лучше рисовать ДО машины, чтобы кузов перекрывал их.
        #
        # Порядок важен: FX обновляет таймер “старта движения”, а skid marks могут
        # использовать этот таймер, чтобы кратко показать следы сразу при старте.
        self._update_and_draw_fx(road, logic, center_x, center_y, proj)
        self._update_and_draw_skid_marks(logic, center_x, center_y)
        # Следы шин должны быть ПОД пылью/дымом.
        self._fx.draw()
        self._offroad_smoke.draw()
        self._exhaust_smoke.draw()
        self._fx_transition.draw()
        # Стартовый дым/пыль рисуем ВЫШЕ skid marks, но НИЖЕ кузова.
        self._drive_fx.draw(0)
        self._draw_car_sprite(logic.steer_input, center_x, center_y)
        self._drive_fx.draw(1)
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
        color: ColorId
    ) -> None:
        """Рисует контур активной зоны (для дебага коллизии).

        Полоски зон рисуются “внутри” дороги (см. `_draw_zone_stripe_at`).
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

    def _draw_road_edges_and_zones(
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
        """Рисует границы дороги и “полоски” зон (boost pads) в top-down."""
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
                line(int(prev_lsx), int(prev_lsy), int(
                    lsx), int(lsy), Color.LIGHT_GREEN)
            if prev_rsx is not None and prev_rsy is not None:
                line(int(prev_rsx), int(prev_rsy), int(
                    rsx), int(rsy), Color.LIGHT_GREEN)

            self._draw_zone_stripe_at(
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

    def _draw_zone_stripe_at(
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
        """Рисует одну “полоску” зоны поперёк дороги, если она активна в этой точке."""
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
        line(int(zsx0), int(zsy0), int(zsx1), int(zsy1), Color.YELLOW)

    def _draw_car_sprite(self, steer_input: int, center_x: int, center_y: int) -> None:
        """Рисует спрайт машины в точке (center_x, center_y) с учётом anchor.

        В режиме top-down мы крутим “мир” под машиной, поэтому поворот корпуса
        спрайтом здесь часто только путает (кажется, что машина сама рулит).

        Поэтому мы всегда рисуем “прямой” кадр машины, а поворот/занос показываем
        HUD/эффектами (руль, slip-bar, следы, пыль и т.п.).
        """
        steer_input = 0
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
        steer_input = 0

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

        # Хитбоксы привязаны к “прямому” спрайту (см. _draw_car_sprite).

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
            circb(int(rear_x), int(rear_y), int(rear_r), Color.CYAN)
        if front_r > 0.0:
            circb(int(front_x), int(front_y), int(front_r), Color.WHITE)

    def _zone_span_at_s(self, s: float, zones: list[DriveZone]) -> tuple[float, float] | None:
        """Возвращает (d0, d1) для подсветки зоны на прогрессе `s`."""
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
            circb(int(sx), int(sy), int(o.radius), Color.RED)
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

        line(cx, cy, cx, int(cy - h), Color.WHITE)

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
        line(cx, cy, int(cx + vx), int(cy + vy), Color.CYAN)

        ax = logic.dbg_side_accel * accel_scale
        if ax > 60.0:
            ax = 60.0
        if ax < -60.0:
            ax = -60.0
        line(cx, cy, int(cx + ax), cy, Color.GREY)

    def _update_and_draw_skid_marks(self, logic: DriveLogic, cx: int, cy: int) -> None:
        """Рисует следы шин позади машины, когда есть заметный занос или зажат ручник.

        Поскольку машина в top-down стоит на месте, а мир крутится под неё, мы можем рисовать
        следы прямо в экранных координатах (в системе “машины”):
        - вперёд: -Y
        - вправо: +X

        Следы намеренно очень простые: 2 короткие линии от задних колёс.
        Это даёт игроку сигнал “машину несёт”, даже если спрайт не поворачивается.
        """
        # slip = abs(v_side) / (abs(v_forward) + eps)
        denom = abs(logic.v_forward) + TUNING.DRIVE.slip_eps_speed
        slip = abs(logic.v_side) / denom
        if slip > 1.0:
            slip = 1.0

        # Порог чуть выше нуля, чтобы не рисовать “дрожь” на прямой.
        active = slip > TUNING.DRIVE.skid_slip_threshold
        if not active:
            # Ручник сам по себе тоже должен оставлять следы, если мы реально движемся.
            if logic.speed > TUNING.DRIVE.skid_min_speed and logic.dbg_handbrake_decel > 0.0:
                active = True

        dt = TUNING.CORE.dt
        if self._start_skid_t > 0.0:
            self._start_skid_t -= dt
            if self._start_skid_t < 0.0:
                self._start_skid_t = 0.0
            if not active and logic.speed > TUNING.DRIVE.skid_min_speed:
                active = True

        # Важно: следы “живут” в мире, а камера привязана к машине.
        # Поэтому каждый кадр сдвигаем уже нарисованные сегменты на величину “движения мира”
        # в экранных координатах:
        # - если машина едет вперёд, мир уходит вниз (dy>0)
        # - если есть боковая скорость, мир уходит в противоположную сторону (dx=-v_side*dt)
        #
        # Для screen-space следов нам нужен dt в секундах. Берём из tuning (CORE.dt).
        dx = -logic.v_side * dt
        dy = logic.v_forward * dt

        # Сначала затухание: каждый кадр уменьшаем "жизнь" и рисуем оставшиеся сегменты.
        # (x0,y0,x1,y1,life)
        i = 0
        while i < len(self._skids):
            x0, y0, x1, y1, life = self._skids[i]
            if life > 0:
                # Нейтральные “следы”: без зелёного (зелёный уже используется дорогой).
                # Палитра TIC-80 у нас общая, поэтому берём серые тона.
                color = Color.DARK_GREY
                if life < TUNING.DRIVE.skid_light_after_frames:
                    color = Color.GREY
                # Сдвигаем сегмент “вместе с миром”, чтобы был хвост, а не мигание в одной точке.
                x0 += dx
                y0 += dy
                x1 += dx
                y1 += dy
                x0i = int(x0)
                y0i = int(y0)
                x1i = int(x1)
                y1i = int(y1)
                # Делаем след шириной 2 пикселя: две параллельные линии.
                if x0 < cx:
                    line(x0i, y0i, x1i, y1i, color)
                    line(x0i + 1, y0i, x1i + 1, y1i, color)
                else:
                    line(x0i - 1, y0i, x1i - 1, y1i, color)
                    line(x0i, y0i, x1i, y1i, color)
                life -= 1
                self._skids[i] = (x0, y0, x1, y1, life)
                i += 1
            else:
                self._skids.pop(i)

        if not active:
            return

        # Добавляем новые следы.
        back = int(TUNING.DRIVE.skid_back_px)
        wheel_dx = int(TUNING.DRIVE.skid_wheel_dx_px)
        seg = int(TUNING.DRIVE.skid_seg_len_px)
        # Небольшое смещение в сторону заноса, чтобы след “наклонялся”.
        # Важно: мир в top-down двигается "против" движения машины. Поэтому наклон
        # должен быть противоположен знаку v_side.
        slant = -int(TUNING.DRIVE.skid_slant_scale * (logic.v_side / denom))
        slant_max = int(TUNING.DRIVE.skid_slant_max)
        if slant > slant_max:
            slant = slant_max
        if slant < -slant_max:
            slant = -slant_max

        left_x = cx - wheel_dx
        right_x = cx + wheel_dx
        y0 = cy + back
        y1 = y0 + seg

        life = int(TUNING.DRIVE.skid_life_frames)
        self._skids.append((left_x, y0, left_x + slant, y1, life))
        self._skids.append((right_x, y0, right_x + slant, y1, life))

    def _update_and_draw_fx(self, road: RoadModel, logic: DriveLogic, cx: int, cy: int, proj: TopdownProjector) -> None:
        """Общий слой частиц DRIVE (пыль/скоростные линии).

        Держим это рядом с рендером, потому что эффекты завязаны на screen-space и не должны
        раздувать DriveLogic.
        """
        d = TUNING.DRIVE
        dt = TUNING.CORE.dt

        # Сдвиг мира в screen-space (как в skid marks).
        world_dx = -logic.v_side * dt
        world_dy = logic.v_forward * dt

        self._fx.update(dt, world_dx, world_dy)
        # Искры перехода должны читаться как “локальный” эффект у колёс,
        # а не как частицы, остающиеся в мире. Поэтому не применяем world-shift,
        # иначе при сильном боковом движении машины направление визуально “едет”.
        self._fx_transition.update(dt, 0.0, 0.0)
        self._drive_fx.update(dt, world_dx, world_dy)
        self._offroad_smoke.update(dt, world_dx, world_dy)
        # Выхлоп хотим как "хвост" в мире, а не в кадре машины: компенсируем вращение камеры.
        # Камера в top-down использует fwd машины как ось Y, поэтому при поворотах весь мир
        # (и screen-space) “крутится”. Частицы в screen-space без компенсации крутятся вместе с машиной.
        pfx = float(self._prev_fwd_x)
        pfy = float(self._prev_fwd_y)
        pl2 = pfx * pfx + pfy * pfy
        if pl2 > 0.0001:
            inv = 1.0 / (pl2 ** 0.5)
            pfx *= inv
            pfy *= inv
        else:
            pfx = 0.0
            pfy = 1.0

        cur_fx = float(logic.fwd_x)
        cur_fy = float(logic.fwd_y)
        cl2 = cur_fx * cur_fx + cur_fy * cur_fy
        if cl2 > 0.0001:
            inv = 1.0 / (cl2 ** 0.5)
            cur_fx *= inv
            cur_fy *= inv
        else:
            cur_fx = 0.0
            cur_fy = 1.0

        dot = pfx * cur_fx + pfy * cur_fy
        if dot > 1.0:
            dot = 1.0
        if dot < -1.0:
            dot = -1.0
        cross = pfx * cur_fy - pfy * cur_fx
        if abs(cross) > 0.0001 or abs(dot - 1.0) > 0.0001:
            # Поворот на -dtheta: cos = dot, sin = -cross.
            self._exhaust_smoke.rotate_around(float(cx), float(cy), dot, -cross)
        self._prev_fwd_x = cur_fx
        self._prev_fwd_y = cur_fy
        self._exhaust_smoke.update(dt, world_dx, world_dy)

        if self._offroad_transition_cooldown > 0.0:
            self._offroad_transition_cooldown -= dt
            if self._offroad_transition_cooldown < 0.0:
                self._offroad_transition_cooldown = 0.0

        # События удара: обрабатываем один раз (burst) и очищаем.
        if len(self._hit_events) > 0:
            i = 0
            while i < len(self._hit_events):
                wx, wy, nx, ny, impact, hit_r = self._hit_events[i]
                seed = self._next_fx_seed()
                self._drive_fx.obstacle_hit(wx, wy, nx, ny, impact, seed, hit_r, proj)
                i += 1
            self._hit_events = []

        # Стартовая пыль: когда скорость “сдвинулась с нуля”.
        spd = logic.speed
        if self._prev_speed <= 0.5 and spd > 0.5:
            # Букс/дым на старте имеет смысл только на дороге.
            # На оффроуде пусть будет просто “постоянная пыль” (ниже), без старта как на асфальте.
            if not logic.offroad:
                self._start_skid_t = float(d.start_skid_seconds)
                self._drive_fx.start_move(cx, cy, self._next_fx_seed())
        self._prev_speed = spd

        # Оффроад пыль: постоянная, другой цвет (сигнал OFFROAD).
        offroad = logic.offroad
        if offroad:
            rd = logic.road_d
            if rd > 0.0:
                self._offroad_side_sign = 1
            elif rd < 0.0:
                self._offroad_side_sign = -1

        if offroad != self._prev_offroad:
            if spd > d.fx_dust_min_speed and self._offroad_transition_cooldown <= 0.0:
                self._emit_offroad_transition_sparks(offroad, road, logic, cx, cy)
                self._offroad_transition_cooldown = 0.20
            self._prev_offroad = offroad

        if offroad and spd > d.fx_dust_min_speed:
            # Небольшой жёлто-оранжевый "дым" (vand dust) из-под колёс.
            # Только пыль на оффроуде (искры — только при переходе туда/обратно).
            self._fx_spawn_accum_off_smoke += (d.fx_dust_rate_offroad * 0.65) * dt
            self._emit_offroad_smoke_vand(self._fx_spawn_accum_off_smoke, cx, cy)
            self._fx_spawn_accum_off_smoke -= int(self._fx_spawn_accum_off_smoke)

        # Speed-lines: при высокой скорости (выше max_speed).
        speed_factor = 0.0
        if d.max_speed > 0.0:
            speed_factor = spd / d.max_speed
        if d.fx_exhaust_rate > 0.0:
            over = speed_factor - d.fx_exhaust_min_speed_factor
            ramp = float(d.fx_exhaust_ramp_speed_factor)
            if ramp < 0.01:
                ramp = 0.01
            strength = over / ramp
            if strength < 0.0:
                strength = 0.0
            if strength > 1.0:
                strength = 1.0
            # Более плавное нарастание, чтобы не было "рубильника".
            strength = strength * strength
            if strength > 0.0:
                rate = d.fx_exhaust_rate * strength
                self._fx_spawn_accum_exhaust += rate * dt
                self._emit_exhaust_smoke_vand(self._fx_spawn_accum_exhaust, cx, cy, strength)
                self._fx_spawn_accum_exhaust -= int(self._fx_spawn_accum_exhaust)

        if d.fx_speedlines_rate > 0.0 and speed_factor > d.fx_speedlines_min_speed_factor:
            self._fx_spawn_accum_speed += d.fx_speedlines_rate * dt
            self._emit_speedlines(self._fx_spawn_accum_speed, logic, cx, cy)
            self._fx_spawn_accum_speed -= int(self._fx_spawn_accum_speed)

        # Рисование делаем в draw(), чтобы следы шин были под пылью/дымом.

    def _next_fx_seed(self) -> int:
        self._fx_seed = (self._fx_seed * 1103515245 + 12345) & 0x7fffffff
        return self._fx_seed

    def _emit_dust(self, count_accum: float, c0: ColorId, c1: ColorId, cx: int, cy: int) -> None:
        """Спавнит часть пыли, используя накопитель count_accum."""
        d = TUNING.DRIVE
        n = int(count_accum)
        if n <= 0:
            return

        wheel_dx = float(d.fx_dust_wheel_dx_px)
        back = float(d.fx_dust_back_px)
        jitter_x = float(d.fx_dust_jitter_x_px)
        jitter_y = float(d.fx_dust_jitter_y_px)
        seg = float(d.fx_dust_len_px)
        seg_dx = 0.0
        seg_dy = 0.0
        if seg > 0.0:
            # Если хотим “палочки”, пусть они будут короткими. seg=0 => точки.
            seg_dy = seg

        i = 0
        while i < n:
            self._fx_seed = (self._fx_seed * 1103515245 + 12345) & 0x7fffffff
            r0 = self._fx_seed
            self._fx_seed = (self._fx_seed * 1103515245 + 12345) & 0x7fffffff
            r1 = self._fx_seed

            # Пыль идёт из-под ОБОИХ колёс (2 точки на задней оси), а не из центра машины.
            # Важно: если пыль будет только с одного колеса, это читается как баг.
            #
            # Цвета выбираем случайно для каждой частицы: так нет “левое колесо всегда серое,
            # правое всегда белое”, и эффект выглядит естественнее.
            vx0 = ((r1 % 1000) / 1000.0 - 0.5) * d.fx_dust_spread_vx
            vy0 = ((r0 % 1000) / 1000.0) * d.fx_dust_spread_vy

            jx = ((r1 % 1000) / 1000.0 - 0.5) * jitter_x
            jy = ((r0 % 1000) / 1000.0) * jitter_y

            x_l = (cx - wheel_dx) + jx
            y_l = (cy + back) + jy
            x_r = (cx + wheel_dx) - jx
            y_r = (cy + back) + jy
            # Выбор двух цветов делаем “по частице”, а не “левое/правое колесо навсегда”.
            # Так эффект выглядит как смесь пыли/дыма, а не как 2 фиксированных источника.
            color_l = c0
            if (r0 % 1000) >= 500:
                color_l = c1
            color_r = c0
            if (r1 % 1000) >= 500:
                color_r = c1

            self._fx.spawn(x_l, y_l, seg_dx, seg_dy, vx0, vy0,
                           d.fx_dust_life_frames, color_l)
            self._fx.spawn(x_r, y_r, seg_dx, seg_dy, -vx0,
                           vy0, d.fx_dust_life_frames, color_r)
            i += 1

    def _emit_offroad_smoke_vand(self, count_accum: float, cx: int, cy: int) -> None:
        n = int(count_accum)
        if n <= 0:
            return

        d = TUNING.DRIVE
        wheel_dx = float(d.fx_dust_wheel_dx_px)
        back = float(d.fx_dust_back_px)
        jitter_x = float(d.fx_dust_jitter_x_px)
        jitter_y = float(d.fx_dust_jitter_y_px)

        i = 0
        while i < n:
            self._fx_seed = (self._fx_seed * 1103515245 + 12345) & 0x7fffffff
            r0 = self._fx_seed
            self._fx_seed = (self._fx_seed * 1103515245 + 12345) & 0x7fffffff
            r1 = self._fx_seed

            jx = ((r1 % 1000) / 1000.0 - 0.5) * jitter_x
            jy = ((r0 % 1000) / 1000.0) * jitter_y

            x_l = (cx - wheel_dx) + jx
            y_l = (cy + back) + jy
            x_r = (cx + wheel_dx) - jx
            y_r = (cy + back) + jy

            # Мелкие частые пуфы читаются как "пыль/туман", а не как редкие круги.
            t = (r0 % 1000) / 1000.0
            r = 1.0 + t * 2.0
            c = Color.YELLOW
            if (r1 % 1000) >= 500:
                c = Color.ORANGE

            self._offroad_smoke.spawn_dust_down_color(float(x_l), float(y_l), float(r), int(c))
            self._offroad_smoke.spawn_dust_down_color(float(x_r), float(y_r), float(r), int(c))

            # Второй пуф чуть поменьше/побольше, чтобы объём был живее.
            r2 = 0.75 + ((r1 % 1000) / 1000.0) * 1.75
            c2 = Color.ORANGE if c == Color.YELLOW else Color.YELLOW
            # Немного "по бокам" из-под колёс: разнос влево/вправо, чтобы пыль не была строго за машиной.
            side = 2.0 + ((r1 % 1000) / 1000.0) * 4.0
            self._offroad_smoke.spawn_dust_down_color(float(x_l - side), float(y_l), float(r2), int(c2))
            self._offroad_smoke.spawn_dust_down_color(float(x_r + side), float(y_r), float(r2), int(c2))
            i += 1

    def _emit_exhaust_smoke_vand(self, count_accum: float, cx: int, cy: int, strength: float) -> None:
        n = int(count_accum)
        if n <= 0:
            return

        d = TUNING.DRIVE
        s = float(strength)
        if s < 0.0:
            s = 0.0
        if s > 1.0:
            s = 1.0
        x0 = float(cx) + float(d.fx_exhaust_dx_px)
        y0 = float(cy) + float(d.fx_exhaust_dy_px)
        r0 = float(d.fx_exhaust_r_min)
        r1 = float(d.fx_exhaust_r_max)
        if r1 < r0:
            t = r0
            r0 = r1
            r1 = t

        # 2 цвета из тюнинга: светлый/тёмный.
        c0 = int(d.fx_exhaust_color_a)
        c1 = int(d.fx_exhaust_color_b)

        i = 0
        while i < n:
            self._fx_seed = (self._fx_seed * 1103515245 + 12345) & 0x7fffffff
            r = self._fx_seed
            t = (r % 1000) / 1000.0
            u = ((r // 1000) % 1000) / 1000.0

            # Выхлоп пробуем тем же типом частиц, что и стартовый "дым из-под колёс":
            # vand `dust_down` (кружки, которые “стелются” в +Y и постепенно темнеют).
            #
            # Схема:
            # - у трубы: тонкая струйка из маленьких кружков
            # - ближе к хвосту: больше размер и больше плотность, чтобы читалось как клубы

            # Струйка (2 маленьких кружка).
            s_jx = (t - 0.5) * 0.8
            s_jy = (u - 0.5) * 0.35
            sr = r0 * (0.70 + t * 0.40) * (0.85 + 0.35 * s)
            if sr < 1.2:
                sr = 1.2
            self._exhaust_smoke.spawn_dust_down_two_tone_life(x0 + s_jx, y0 + s_jy, sr, c0, c1, 18)
            self._exhaust_smoke.spawn_dust_down_two_tone_life(x0 - s_jx * 0.55, y0 + s_jy * 0.55, sr * 0.85, c0, c1, 16)

            # Средний слой (2 штуки).
            my = y0 + 3.0 + u * 4.0
            mr = (r0 + (r1 - r0) * (0.25 + t * 0.20)) * (0.80 + 0.55 * s)
            if mr < sr:
                mr = sr
            mid_life = 26 + int(s * 18.0)
            self._exhaust_smoke.spawn_dust_down_two_tone_life(x0 + (u - 0.5) * 1.6, my, mr, c0, c1, mid_life)
            self._exhaust_smoke.spawn_dust_down_two_tone_life(x0 - (u - 0.5) * 1.2, my + 1.2, mr * 0.95, c0, c1, mid_life - 2)

            # Хвост (клубы): плотный кластер ближе к машине.
            tail_y = y0 + 5.0 + u * 6.0
            if tail_y > 128.0:
                tail_y = 128.0
            tail_r = r1 * (0.85 + t * 0.35) * (0.70 + 0.70 * s)
            if tail_r < mr:
                tail_r = mr
            tail_life = 34 + int(s * 26.0)
            self._exhaust_smoke.spawn_dust_down_two_tone_life(x0 + (t - 0.5) * 2.8, tail_y, tail_r, c0, c1, tail_life)
            self._exhaust_smoke.spawn_dust_down_two_tone_life(x0 + (u - 0.5) * 2.2 + 1.2, tail_y + 1.6, tail_r * 0.92, c0, c1, tail_life - 2)
            self._exhaust_smoke.spawn_dust_down_two_tone_life(x0 - (u - 0.5) * 2.0 - 1.0, tail_y + 2.6, tail_r * 0.88, c0, c1, tail_life - 4)
            self._exhaust_smoke.spawn_dust_down_two_tone_life(x0 + (t - 0.5) * 2.0 - 1.4, tail_y + 3.6, tail_r * 0.84, c0, c1, tail_life - 6)
            self._exhaust_smoke.spawn_dust_down_two_tone_life(x0 + (t - 0.5) * 2.4 + 0.8, tail_y + 4.6, tail_r * 0.78, c0, c1, tail_life - 8)
            if (r & 1) == 0:
                self._exhaust_smoke.spawn_dust_down_two_tone_life(x0 + (u - 0.5) * 2.8, tail_y + 5.4, tail_r * 0.72, c0, c1, tail_life - 10)
            i += 1

    def _emit_offroad_transition_sparks(
        self,
        entering_offroad: bool,
        road: RoadModel,
        logic: DriveLogic,
        cx: int,
        cy: int
    ) -> None:
        d = TUNING.DRIVE

        boundary_sign = self._offroad_side_sign
        spawn_sign = -boundary_sign
        dir_sign = -boundary_sign
        if not entering_offroad:
            spawn_sign = boundary_sign
            dir_sign = boundary_sign

        dir_x, dir_y, cross = self._edge_spark_dir(road, logic, dir_sign, entering_offroad)

        spd = logic.speed
        n = 5 + int(spd * 0.05)
        if not entering_offroad:
            n = int(n * 1.7)
        if n < 6:
            n = 6
        if n > 26:
            n = 26

        speed = 160.0 + spd * 2.6
        if speed > 320.0:
            speed = 320.0

        life = 9 + int(spd * 0.01)
        if not entering_offroad:
            life += 4
        if life > 20:
            life = 20

        wheel_dx = float(d.fx_transition_sparks_wheel_dx_px)
        back = float(d.fx_transition_sparks_back_px)
        wheelbase = float(d.fx_transition_sparks_wheelbase_px)

        rear_x = float(cx) + float(spawn_sign) * wheel_dx
        rear_y = float(cy) + back
        front_x = float(cx) + float(spawn_sign) * (wheel_dx * 0.72)
        front_y = rear_y - wheelbase + 3.0

        n_front = int(n * 0.6)
        if n_front < 3:
            n_front = 3
        if n_front > n:
            n_front = n

        self._edge_spark_burst(rear_x, rear_y, dir_x, dir_y, cross, speed, n, life, entering_offroad, 1.0)
        self._edge_spark_burst(front_x, front_y, dir_x, dir_y, cross, speed, n_front, life, entering_offroad, 0.85)

    def _edge_spark_dir(
        self,
        road: RoadModel,
        logic: DriveLogic,
        dir_sign: int,
        entering_offroad: bool
    ) -> tuple[float, float, float]:
        dx, dy = road.direction_at(logic.road_s)
        rx = -dy
        ry = dx

        fx = logic.fwd_x
        fy = logic.fwd_y
        crx = -fy
        cry = fx

        sx = rx * crx + ry * cry
        sy = -(rx * fx + ry * fy)
        d0 = abs(sx) + abs(sy)
        if d0 < 0.001:
            sx = 1.0
            sy = 0.0
            d0 = 1.0
        sx = (sx / d0) * float(dir_sign)
        sy = (sy / d0) * float(dir_sign)

        mx = -logic.v_side
        my = logic.v_forward
        d1 = abs(mx) + abs(my)
        if d1 < 0.001:
            d1 = 1.0
        mx /= d1
        my /= d1
        cross = abs(mx * sx + my * sy)
        if cross > 1.0:
            cross = 1.0

        wn = 0.45 + 1.10 * cross
        wt = 1.10
        if not entering_offroad:
            wt = 1.35

        dx = sx * wn
        dy = sy * wn + wt
        d2 = abs(dx) + abs(dy)
        if d2 < 0.001:
            d2 = 1.0
        dx /= d2
        dy /= d2
        return dx, dy, cross

    def _edge_spark_burst(
        self,
        base_x: float,
        base_y: float,
        dir_x: float,
        dir_y: float,
        cross: float,
        speed: float,
        count: int,
        life: int,
        entering_offroad: bool,
        scale: float
    ) -> None:
        px = -dir_y
        py = dir_x

        i = 0
        while i < count:
            self._fx_seed = (self._fx_seed * 1103515245 + 12345) & 0x7fffffff
            r0 = self._fx_seed
            self._fx_seed = (self._fx_seed * 1103515245 + 12345) & 0x7fffffff
            r1 = self._fx_seed

            t = (r0 % 1000) / 1000.0
            u = (r1 % 1000) / 1000.0

            # Меньше промежуточных переменных: в PocketPy есть лимит на число locals.
            spread = (0.28 + u * 0.26) * (0.75 + 0.70 * cross)
            if not entering_offroad:
                spread += 0.12
            spread *= (0.80 + 0.20 * scale)

            vx = dir_x + px * ((t - 0.5) * 2.0 * spread)
            vy = dir_y + py * ((t - 0.5) * 2.0 * spread)
            den = abs(vx) + abs(vy)
            if den < 0.001:
                den = 1.0
            vx /= den
            vy /= den

            seg = (3.0 + t * 6.0) * scale
            if not entering_offroad:
                seg *= 1.15

            pvx = vx * speed * (0.80 + t * 0.40) * scale
            pvy = vy * speed * (0.80 + u * 0.40) * scale

            color = Color.WHITE
            m = int(r0 % 3)
            if m == 1:
                color = Color.YELLOW
            elif m == 2:
                color = Color.ORANGE

            self._fx_transition.spawn(
                base_x + (t - 0.5) * 2.5 * scale,
                base_y + (u - 0.5) * 2.0 * scale,
                vx * seg,
                vy * seg,
                pvx,
                pvy,
                life,
                color
            )
            i += 1

    def _emit_speedlines(self, count_accum: float, logic: DriveLogic, cx: int, cy: int) -> None:
        """Спавнит speed-lines при высокой скорости."""
        d = TUNING.DRIVE
        n = int(count_accum)
        if n <= 0:
            return

        # В screen-space “траектория” задаётся скоростью машины:
        # world_dx/world_dy (в update) основаны на:
        #   dx = -v_side * dt
        #   dy =  v_forward * dt
        # Чтобы speed-lines выглядели согласованно с дымом, рисуем их вдоль этого же направления.
        dir_x = -logic.v_side
        dir_y = logic.v_forward
        denom = abs(dir_x) + abs(dir_y)
        if denom < 0.001:
            denom = 1.0
            dir_x = 0.0
            dir_y = 1.0
        nx = dir_x / denom
        ny = dir_y / denom

        i = 0
        while i < n:
            self._fx_seed = (self._fx_seed * 1103515245 + 12345) & 0x7fffffff
            r0 = self._fx_seed
            self._fx_seed = (self._fx_seed * 1103515245 + 12345) & 0x7fffffff
            r1 = self._fx_seed

            x = cx + ((r0 % 1000) / 1000.0 - 0.5) * d.fx_speedlines_x_spread
            # Speed-lines должны быть ПОЗАДИ машины (ниже по Y), иначе они выглядят как “из центра”.
            y0 = cy + d.fx_speedlines_back_y0
            y1 = cy + d.fx_speedlines_back_y1
            # Рендер — screen-space (240x136). Подстрахуемся, чтобы не спавнить “в пустоту”.
            if y0 < 0.0:
                y0 = 0.0
            if y0 > 136.0:
                y0 = 136.0
            if y1 < 0.0:
                y1 = 0.0
            if y1 > 136.0:
                y1 = 136.0
            if y1 < y0:
                t = y0
                y0 = y1
                y1 = t
            y = y0 + ((r1 % 1000) / 1000.0) * (y1 - y0)
            ln = d.fx_speedlines_len_px
            color = d.fx_speedlines_color_a
            if (r1 % 1000) >= 500:
                color = d.fx_speedlines_color_b
            # В отличие от “палок” по оси Y, тут отрезок поворачиваем по траектории.
            dx = nx * ln
            dy = ny * ln
            vx = nx * d.fx_speedlines_vy
            vy = ny * d.fx_speedlines_vy
            self._fx.spawn(x, y, dx, dy, vx, vy,
                           d.fx_speedlines_life_frames, color)
            i += 1
