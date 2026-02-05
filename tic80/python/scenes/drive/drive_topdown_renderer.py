from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import circb, line, rect, rectb, spr

    from ...core.palette import Color, ColorId
    from ...core.sprites import NIVA_TOPDOWN
    from ...data.tuning import TUNING
    from ...systems.drive.drive_logic import DriveLogic
    from ...systems.drive.drive_objects import (
        DriveObjects,
        DriveObstacle,
        DriveZone
    )
    from ...systems.drive.fx_particles import Particles2D
    from ...systems.drive.road_model import RoadModel


class DriveTopdownRenderer:
    """Рендер DRIVE в варианте A (top-down).

    Задача класса: только рисовать. Никаких изменений состояния RunState/DriveLogic.
    """

    def __init__(self) -> None:
        # Короткий буфер “следов” (skid marks), чтобы занос читался без поворота спрайта.
        self._skids: list[tuple[float, float, float, float, int]] = []
        self._fx = Particles2D(TUNING.DRIVE.fx_particles_max)
        self._prev_speed = 0.0
        self._start_dust_t = 0.0
        self._start_skid_t = 0.0
        self._damage_dust_t = 0.0
        self._fx_spawn_accum_start = 0.0
        self._fx_spawn_accum_off = 0.0
        self._fx_spawn_accum_damage = 0.0
        self._fx_spawn_accum_speed = 0.0
        self._fx_seed = 1

    def notify_damage(self) -> None:
        """Сообщает рендеру, что в этом кадре было столкновение (получили урон).

        Это чисто визуальная штука: мы хотим короткий “пух” пыли/грязи, чтобы урон читался
        без дебага и без текста.
        """
        self._damage_dust_t = float(TUNING.DRIVE.fx_damage_dust_seconds)

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
        self._update_and_draw_fx(logic, center_x, center_y)
        self._update_and_draw_skid_marks(logic, center_x, center_y)
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
                line(int(x0), int(y0), int(x1), int(y1), color)
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

    def _update_and_draw_fx(self, logic: DriveLogic, cx: int, cy: int) -> None:
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

        # Стартовая пыль: когда скорость “сдвинулась с нуля”.
        spd = logic.speed
        if self._prev_speed <= 0.5 and spd > 0.5:
            # Букс/дым на старте имеет смысл только на дороге.
            # На оффроуде пусть будет просто “постоянная пыль” (ниже), без старта как на асфальте.
            if not logic.offroad:
                self._start_dust_t = float(d.fx_start_dust_seconds)
                self._start_skid_t = float(d.start_skid_seconds)
        self._prev_speed = spd

        if self._start_dust_t > 0.0:
            self._start_dust_t -= dt
            if self._start_dust_t < 0.0:
                self._start_dust_t = 0.0
            self._fx_spawn_accum_start += d.fx_dust_rate_start * dt
            self._emit_dust(
                self._fx_spawn_accum_start,
                d.fx_start_dust_color_a,
                d.fx_start_dust_color_b,
                cx,
                cy
            )
            self._fx_spawn_accum_start -= int(self._fx_spawn_accum_start)

        # Оффроад пыль: постоянная, другой цвет (сигнал OFFROAD).
        if logic.offroad and spd > d.fx_dust_min_speed:
            self._fx_spawn_accum_off += d.fx_dust_rate_offroad * dt
            self._emit_dust(
                self._fx_spawn_accum_off,
                d.fx_offroad_dust_color_a,
                d.fx_offroad_dust_color_b,
                cx,
                cy
            )
            self._fx_spawn_accum_off -= int(self._fx_spawn_accum_off)

        # Пыль от урона: короткий “пух”, независимо от поверхности.
        if self._damage_dust_t > 0.0:
            self._damage_dust_t -= dt
            if self._damage_dust_t < 0.0:
                self._damage_dust_t = 0.0
            self._fx_spawn_accum_damage += d.fx_damage_dust_rate * dt
            # Цвет берём как у оффроуда: читается как “грязь/песок” и хорошо видна на дороге.
            self._emit_dust(
                self._fx_spawn_accum_damage,
                d.fx_offroad_dust_color_a,
                d.fx_offroad_dust_color_b,
                cx,
                cy
            )
            self._fx_spawn_accum_damage -= int(self._fx_spawn_accum_damage)

        # Speed-lines: при высокой скорости (выше max_speed).
        speed_factor = 0.0
        if d.max_speed > 0.0:
            speed_factor = spd / d.max_speed
        if speed_factor > d.fx_speedlines_min_speed_factor:
            self._fx_spawn_accum_speed += d.fx_speedlines_rate * dt
            self._emit_speedlines(self._fx_spawn_accum_speed, logic, cx, cy)
            self._fx_spawn_accum_speed -= int(self._fx_spawn_accum_speed)

        self._fx.draw()

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
