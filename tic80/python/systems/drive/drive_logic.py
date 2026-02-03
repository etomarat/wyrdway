from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...contracts import Tuning
    from ...core.run_state import RunState

    from .road_model import RoadModel


class DriveLogic:
    """Единая логика DRIVE (m1.5), независимая от варианта рендера.

    Важно: это world-space модель.
    Машина имеет:
    - позицию (x, y) в мире,
    - направление (fwd_x, fwd_y) как unit-вектор,
    - скорость (vx, vy) как вектор, который может быть не сонаправлен направлению.

    Это даёт “тяжесть” и занос: машина может смотреть в одну сторону, а ехать
    чуть боком, пока сцепление не “вытянет” скорость обратно вдоль направления.

    RoadModel используется только для:
    - вычисления прогресса `road_s` и смещения `road_d` через проекцию на дорогу,
    - определения оффроуда,
    - условий успеха (доехал по дороге до конца сегмента),
    - спавна/рендера объектов в (s, d).
    """

    def __init__(self, run: RunState, road: RoadModel, tuning: Tuning) -> None:
        self._run = run
        self._road = road
        self._tuning = tuning

        self._x = 0.0
        self._y = 0.0
        self._fwd_x = 1.0
        self._fwd_y = 0.0
        self._vx = 0.0
        self._vy = 0.0

        self._road_idx = 0
        self._road_s = 0.0
        self._road_d = 0.0
        self._offroad = False
        self._steer_input = 0
        self._dbg_speed_factor = 0.0
        self._dbg_steer_scale = 0.0
        self._dbg_effective_grip = 0.0
        self._dbg_side_damp = 0.0
        self._dbg_side_accel = 0.0
        self._dbg_fuel_per_sec = 0.0
        self._dash_cd = 0.0
        self._zone_grip_mult = 1.0
        self._zone_boost_forward = 0.0
        self._zone_boost_center = 0.0
        self._dbg_zone_boost_forward = 0.0
        self._dbg_zone_boost_center = 0.0
        self._zone_antislip = 0.0
        self._dbg_zone_antislip = 0.0
        self._zone_grip_floor = 0.0

        self._init_on_road_start()

    def set_zone_grip_mult(self, mult: float) -> None:
        """Задаёт множитель сцепления от дорожной зоны (ускорялки) для следующего кадра.

        Мы храним это в логике, чтобы эффект влиял на тот же `effective_grip`, который уже
        участвует в заносе/боковом трении.

        Важно: сама проверка "в зоне ли игрок" делается снаружи (в сцене), потому что
        зоны живут в системе объектов дороги.
        """
        if mult < 0.0:
            mult = 0.0
        self._zone_grip_mult = mult

    def set_zone_boost(self, forward_accel: float, center_accel: float) -> None:
        """Задаёт параметры ускорялки (boost-zone) для следующего кадра.

        Параметры задаются в world-space, но в “координатах дороги”:
        - forward_accel применяется вдоль направления дороги (road_dir),
        - center_accel применяется по нормали к дороге в сторону центра трассы (d -> 0).

        Это важно: бустер должен толкать “по полосе”, даже если машина едет боком.
        """
        if forward_accel < 0.0:
            forward_accel = 0.0
        if center_accel < 0.0:
            center_accel = 0.0
        self._zone_boost_forward = forward_accel
        self._zone_boost_center = center_accel
        self._dbg_zone_boost_forward = forward_accel
        self._dbg_zone_boost_center = center_accel

    def set_zone_antislip(self, strength: float) -> None:
        """Задаёт силу “анти-заноса” от зоны (ускорялки) для следующего кадра.

        Это отдельная стабилизация боковой скорости (v_side), чтобы ускорялка
        ощущалась как “безопасная полоса” на сложном повороте.
        """
        if strength < 0.0:
            strength = 0.0
        self._zone_antislip = strength
        self._dbg_zone_antislip = strength

    def set_zone_grip_floor(self, value: float) -> None:
        """Задаёт минимальный effective_grip внутри зоны (ускорялки) на следующий кадр.

        Это “страховка” против ручника: даже если `handbrake_grip_mult` сильно режет
        сцепление, внутри бустера мы не даём effective_grip падать ниже порога.
        """
        if value < 0.0:
            value = 0.0
        self._zone_grip_floor = value

    @property
    def dbg_zone_boost_forward(self) -> float:
        """Текущее ускорение ускорялки вдоль дороги (units/sec^2), для дебага."""
        return self._dbg_zone_boost_forward

    @property
    def dbg_zone_boost_center(self) -> float:
        """Текущее ускорение ускорялки к центру дороги (units/sec^2), для дебага."""
        return self._dbg_zone_boost_center

    @property
    def dbg_zone_antislip(self) -> float:
        """Сила анти-заноса от зоны (1/sec), для дебага."""
        return self._dbg_zone_antislip

    def _init_on_road_start(self) -> None:
        """Ставит машину в начало дороги и выравнивает по направлению дороги."""
        cx, cy = self._road.sample_centerline(0.0)
        dx, dy = self._road.direction_at(0.0)
        self._x = cx
        self._y = cy
        self._fwd_x = dx
        self._fwd_y = dy
        self._vx = 0.0
        self._vy = 0.0
        self._road_idx = 0
        self._update_road_projection()

    @property
    def x(self) -> float:
        return self._x

    @property
    def y(self) -> float:
        return self._y

    @property
    def fwd_x(self) -> float:
        return self._fwd_x

    @property
    def fwd_y(self) -> float:
        return self._fwd_y

    @property
    def speed(self) -> float:
        v2 = self._vx * self._vx + self._vy * self._vy
        return v2 ** 0.5

    @property
    def v_forward(self) -> float:
        """Скорость вдоль направления машины (может быть отрицательной при реверсе)."""
        fwd_x = self._fwd_x
        fwd_y = self._fwd_y
        return self._vx * fwd_x + self._vy * fwd_y

    @property
    def v_side(self) -> float:
        """Боковая скорость (как сильно “несёт боком” относительно направления)."""
        right_x = -self._fwd_y
        right_y = self._fwd_x
        return self._vx * right_x + self._vy * right_y

    def estimated_vmax_road(self) -> float:
        """Оценивает "крейсерскую максималку" (плато) на дороге.

        Это не жёсткий лимит: реальная скорость ниже на поворотах и при заносе, потому что
        часть энергии уходит в боковую скорость. Но оценка полезна, чтобы понимать,
        почему при текущих `accel/drag_*` машина стабилизируется примерно на X.
        """
        return self._estimated_vmax(False)

    def estimated_vmax_offroad(self) -> float:
        """Оценивает "крейсерскую максималку" (плато) на оффроуде."""
        return self._estimated_vmax(True)

    def _estimated_vmax(self, offroad: bool) -> float:
        """Внутренняя оценка плато скорости при постоянном газе.

        Упрощённая модель как в коде:
          dv/dt = +accel - (drag_lin + drag_quad*|v|) * v

        Равновесие:
          accel ≈ (drag_lin + drag_quad*v) * v
          => drag_quad*v^2 + drag_lin*v - accel ≈ 0
        """
        d = self._tuning.DRIVE
        accel = d.accel
        if accel <= 0.0:
            return 0.0

        drag_lin = d.drag_lin
        drag_quad = d.drag_quad
        if offroad:
            drag_lin += d.offroad_drag_lin
            drag_quad += d.offroad_drag_quad

        speed_cap = d.speed_cap

        v = 0.0
        if drag_lin <= 0.0 and drag_quad <= 0.0:
            v = speed_cap if speed_cap > 0.0 else 9999.0
        elif drag_quad <= 0.0:
            if drag_lin <= 0.0:
                v = speed_cap if speed_cap > 0.0 else 9999.0
            else:
                v = accel / drag_lin
        else:
            disc = drag_lin * drag_lin + 4.0 * drag_quad * accel
            if disc < 0.0:
                disc = 0.0
            v = (-drag_lin + (disc ** 0.5)) / (2.0 * drag_quad)

        if speed_cap > 0.0 and v > speed_cap:
            v = speed_cap
        if v < 0.0:
            v = 0.0
        return v

    @property
    def road_s(self) -> float:
        """Прогресс вдоль дороги (проекция world position на centerline)."""
        return self._road_s

    @property
    def road_d(self) -> float:
        """Смещение от центра дороги (проекция на road-right нормаль)."""
        return self._road_d

    @property
    def offroad(self) -> bool:
        return self._offroad

    @property
    def steer_input(self) -> int:
        return self._steer_input

    @property
    def dbg_speed_factor(self) -> float:
        """Нормализованная скорость (0..1) для тюнинга управления."""
        return self._dbg_speed_factor

    @property
    def dbg_steer_scale(self) -> float:
        """Итоговый множитель руления в этом кадре."""
        return self._dbg_steer_scale

    @property
    def dbg_effective_grip(self) -> float:
        """effective_grip в этом кадре (с учётом ручника/оффроуда)."""
        return self._dbg_effective_grip

    @property
    def dbg_side_damp(self) -> float:
        """Итоговый коэффициент гашения боковой скорости (0..1) за кадр."""
        return self._dbg_side_damp

    @property
    def dbg_side_accel(self) -> float:
        """Боковое ускорение (units/sec^2), которое даёт “трение” заноса в этом кадре.

        Это производная по времени от боковой скорости:
        `a_side = (v_side_after - v_side_before) / dt`.

        Обычно знак противоположен `v_side` (трение гасит занос).
        """
        return self._dbg_side_accel

    @property
    def dbg_fuel_per_sec(self) -> float:
        """Текущий расход топлива в секунду (оценка для дебага)."""
        return self._dbg_fuel_per_sec

    def update(
        self,
        dt: float,
        steer_input: int,
        throttle: bool,
        brake: bool,
        handbrake: bool,
        dash_pressed: bool
    ) -> None:
        """Обновляет физику машины на один шаг `dt`.

        Управление:
        - throttle (UP): разгон вперёд
        - brake (DOWN): тормоз, а при почти нулевой скорости — задний ход
        - steer_input (LEFT/RIGHT): поворот направления машины
        - handbrake (B): снижает сцепление => больше заноса, чуть резче поворот
        - dash (A): рывок вперёд (по умолчанию выключен, включается апгрейдом)

        Важно: если вообще не рулить, машина едет “как направлена”, а дорога
        уходит в сторону на поворотах. То есть “автопилота” нет.
        """
        d = self._tuning.DRIVE
        self._steer_input = steer_input

        offroad_before = self._offroad

        self._step_update_dash_cooldown(dt)

        speed = self.speed
        speed_factor = self._step_speed_factor(speed, d.max_speed)
        self._dbg_speed_factor = speed_factor

        self._step_apply_steering(
            dt,
            steer_input,
            throttle,
            handbrake,
            offroad_before,
            speed,
            speed_factor
        )

        fwd_x = self._fwd_x
        fwd_y = self._fwd_y
        right_x = -fwd_y
        right_y = fwd_x

        v_fwd = self._vx * fwd_x + self._vy * fwd_y
        v_side = self._vx * right_x + self._vy * right_y

        v_fwd = self._step_apply_dash(v_fwd, dash_pressed)
        v_fwd = self._step_apply_longitudinal(
            dt,
            v_fwd,
            throttle,
            brake,
            handbrake,
            speed_factor
        )
        v_fwd = self._step_clamp_v_fwd(v_fwd)

        effective_grip = self._step_effective_grip(handbrake, offroad_before)
        v_side_before = v_side
        v_side = self._step_apply_lateral_damping(
            dt,
            v_side,
            effective_grip,
            speed_factor
        )
        v_side = self._step_apply_zone_antislip(dt, v_side)
        if dt > 0.0:
            # dbg_side_accel должен отражать итоговое гашение заноса,
            # включая дополнительный анти-занос от зоны.
            self._dbg_side_accel = (v_side - v_side_before) / dt
        else:
            self._dbg_side_accel = 0.0

        self._vx = fwd_x * v_fwd + right_x * v_side
        self._vy = fwd_y * v_fwd + right_y * v_side

        self._apply_zone_boost(dt)

        self._x += self._vx * dt
        self._y += self._vy * dt

        self._update_road_projection()

        self._step_apply_drag(dt)
        self._step_apply_fuel(dt, throttle)

    def _step_update_dash_cooldown(self, dt: float) -> None:
        """Обновляет внутренний таймер кулдауна рывка (dash)."""
        if self._dash_cd > 0.0:
            self._dash_cd -= dt
            if self._dash_cd < 0.0:
                self._dash_cd = 0.0

    @staticmethod
    def _step_speed_factor(speed: float, max_speed: float) -> float:
        """Нормализует скорость в диапазон 0..1 (для тюнинга рулёжки/заноса)."""
        if max_speed <= 0.0:
            return 0.0
        sf = speed / max_speed
        if sf > 1.0:
            sf = 1.0
        if sf < 0.0:
            sf = 0.0
        return sf

    def _step_apply_steering(
        self,
        dt: float,
        steer_input: int,
        throttle: bool,
        handbrake: bool,
        offroad_before: bool,
        speed: float,
        speed_factor: float
    ) -> None:
        """Поворачивает heading по вводу руля и условиям (скорость, ручник, оффроуд)."""
        d = self._tuning.DRIVE

        steer_scale = d.steer_scale_max + (d.steer_scale_min - d.steer_scale_max) * speed_factor
        if steer_scale < 0.0:
            steer_scale = 0.0
        if speed < d.steer_min_speed:
            steer_scale = 0.0
        if self.v_forward < 0.0:
            steer_scale *= d.steer_reverse_mult
        self._dbg_steer_scale = steer_scale

        yaw = steer_input * d.steer_rate * steer_scale * dt
        if handbrake and throttle and steer_input != 0:
            yaw = self._step_apply_handbrake_steer_boost(yaw, speed_factor)
        if offroad_before:
            yaw *= d.offroad_steer_mult
        if yaw != 0.0:
            self._rotate_heading(yaw)

    def _step_apply_handbrake_steer_boost(self, yaw: float, speed_factor: float) -> float:
        """Усиливает руление от ручника (B) только на скорости.

        Идея: на низкой скорости ручник не должен “читерить”, а на высокой — помогает
        довернуть (эффект а-ля Mario Kart).
        """
        d = self._tuning.DRIVE

        hb_min = d.handbrake_steer_min_speed_factor
        if hb_min < 0.0:
            hb_min = 0.0
        if hb_min > 1.0:
            hb_min = 1.0

        hb_t = 0.0
        if speed_factor > hb_min:
            denom = 1.0 - hb_min
            if denom > 0.0:
                hb_t = (speed_factor - hb_min) / denom
            else:
                hb_t = 1.0
        if hb_t > 1.0:
            hb_t = 1.0
        if hb_t < 0.0:
            hb_t = 0.0

        hb_gain = d.handbrake_steer_mult - 1.0
        return yaw * (1.0 + hb_gain * hb_t)

    def _step_apply_dash(self, v_fwd: float, dash_pressed: bool) -> float:
        """Применяет рывок вперёд (dash), если включён тюнингом и нет кулдауна."""
        d = self._tuning.DRIVE
        if dash_pressed and d.dash_impulse > 0.0 and self._dash_cd <= 0.0:
            v_fwd += d.dash_impulse
            self._dash_cd = d.dash_cooldown
        return v_fwd

    def _step_apply_longitudinal(
        self,
        dt: float,
        v_fwd: float,
        throttle: bool,
        brake: bool,
        handbrake: bool,
        speed_factor: float
    ) -> float:
        """Продольная динамика: газ/тормоз/накат + доп. замедление от ручника."""
        d = self._tuning.DRIVE

        if throttle and not brake:
            if v_fwd < 0.0:
                v_fwd = self._approach(v_fwd, 0.0, d.brake * dt)
            else:
                v_fwd += d.accel * dt
        elif brake and not throttle:
            if v_fwd > 0.0:
                v_fwd = self._approach(v_fwd, 0.0, d.brake * dt)
            else:
                v_fwd -= d.accel * dt
        else:
            v_fwd = self._approach(v_fwd, 0.0, d.coast_decel * dt)

        if handbrake and d.handbrake_decel > 0.0:
            v_fwd = self._step_apply_handbrake_decel(dt, v_fwd, throttle, speed_factor)

        return v_fwd

    def _step_apply_handbrake_decel(
        self,
        dt: float,
        v_fwd: float,
        throttle: bool,
        speed_factor: float
    ) -> float:
        """Замедление от ручника: сильнее ощущается на скорости, слабее под газом."""
        d = self._tuning.DRIVE
        hb_sf = speed_factor
        if hb_sf < d.handbrake_decel_min_speed_factor:
            hb_sf = d.handbrake_decel_min_speed_factor
        hb_decel = d.handbrake_decel * hb_sf
        if throttle:
            hb_decel *= d.handbrake_decel_throttle_mult
        return self._approach(v_fwd, 0.0, hb_decel * dt)

    def _step_clamp_v_fwd(self, v_fwd: float) -> float:
        """Ограничивает задний ход и (опционально) верхнюю скорость по оси вперёд."""
        d = self._tuning.DRIVE
        if v_fwd < -d.max_reverse_speed:
            v_fwd = -d.max_reverse_speed
        if d.speed_cap > 0.0 and v_fwd > d.speed_cap:
            v_fwd = d.speed_cap
        return v_fwd

    def _step_effective_grip(self, handbrake: bool, offroad_before: bool) -> float:
        """Считает effective_grip для этого кадра и пишет dbg_effective_grip."""
        d = self._tuning.DRIVE

        effective_grip = d.grip
        if handbrake:
            effective_grip *= d.handbrake_grip_mult
        if offroad_before:
            effective_grip *= d.offroad_grip_mult
        if self._zone_grip_mult != 1.0:
            effective_grip *= self._zone_grip_mult
        if self._zone_grip_floor > 0.0 and effective_grip < self._zone_grip_floor:
            effective_grip = self._zone_grip_floor
        if effective_grip < 0.0:
            effective_grip = 0.0
        self._dbg_effective_grip = effective_grip
        return effective_grip

    def _step_apply_lateral_damping(
        self,
        dt: float,
        v_side: float,
        effective_grip: float,
        speed_factor: float
    ) -> float:
        """Гасит боковую скорость (занос) в текущем кадре через side_friction."""
        d = self._tuning.DRIVE
        v_side_before = v_side

        slip = 1.0 + d.side_slip_speed_mult * speed_factor
        if slip < 1.0:
            slip = 1.0
        side_damp = 1.0 - (d.side_friction * effective_grip * dt) / slip
        if side_damp < 0.0:
            side_damp = 0.0
        if side_damp > 1.0:
            side_damp = 1.0

        v_side *= side_damp
        self._dbg_side_damp = side_damp
        if dt > 0.0:
            self._dbg_side_accel = (v_side - v_side_before) / dt
        else:
            self._dbg_side_accel = 0.0

        return v_side

    def _step_apply_zone_antislip(self, dt: float, v_side: float) -> float:
        """Дополнительно гасит боковую скорость внутри зоны (ускорялки).

        Идея: бустер — “безопасная полоса”.
        Если игрок еле удержался и попал на панель на повороте, занос гасится быстрее,
        и машину проще стабилизировать.

        Реализация — мультипликативное демпфирование:
          v_side *= clamp(1 - k * dt, 0..1)
        Где `k` — `TUNING.DRIVE.zone_antislip` (единицы: 1/sec).
        """
        k = self._zone_antislip
        if k <= 0.0 or dt <= 0.0:
            return v_side
        factor = 1.0 - k * dt
        if factor < 0.0:
            factor = 0.0
        if factor > 1.0:
            factor = 1.0
        v_side *= factor
        return v_side

    def _step_apply_drag(self, dt: float) -> None:
        """Общие сопротивления движения + добавка от оффроуда.

        Модель (векторно):
          dv/dt = -C_lin * v - C_quad * v * |v|

        Оффроуд добавляет к C_lin/C_quad свои коэффициенты (вязкость/песок),
        чтобы на высокой скорости темп падал, но на низкой можно было выбраться обратно.
        """
        d = self._tuning.DRIVE
        drag_lin = d.drag_lin
        drag_quad = d.drag_quad
        if self._offroad:
            drag_lin += d.offroad_drag_lin
            drag_quad += d.offroad_drag_quad
        if drag_lin <= 0.0 and drag_quad <= 0.0:
            return

        v2 = self._vx * self._vx + self._vy * self._vy
        spd = v2 ** 0.5
        drag = drag_lin + drag_quad * spd
        if drag <= 0.0:
            return

        mult = 1.0 - drag * dt
        if mult < 0.0:
            mult = 0.0
        if mult > 1.0:
            mult = 1.0
        self._vx *= mult
        self._vy *= mult

    def _step_apply_fuel(self, dt: float, throttle: bool) -> None:
        """Списывает топливо по текущему вводу и поверхности (оффроуд дороже)."""
        d = self._tuning.DRIVE
        fuel_spend = d.fuel_per_sec_idle * dt
        if throttle:
            fuel_spend += d.fuel_per_sec_throttle * dt
        if self._offroad and d.offroad_fuel_mult > 0.0:
            fuel_spend *= d.offroad_fuel_mult
        if dt > 0.0:
            self._dbg_fuel_per_sec = fuel_spend / dt
        else:
            self._dbg_fuel_per_sec = 0.0
        if fuel_spend > 0.0:
            self._run.consume_fuel(fuel_spend)

    def finished(self) -> bool:
        """True, если игрок доехал по дороге до конца сегмента."""
        return self._road_s >= self._road.segment_total_length

    def hitbox_world_circles(self) -> tuple[float, float, float, float, float, float]:
        """Возвращает 2 круговых хитбокса в world-space: rear(x,y,r), front(x,y,r).

        Хитбоксы задаются в пикселях спрайта (см. tuning hitbox_*_px/py) и затем
        преобразуются в локальные оффсеты относительно car_sprite_anchor_*:
          right_offset = (hitbox_px - anchor_x)
          fwd_offset = -(hitbox_py - anchor_y)

        Затем оффсеты переводятся в world-space через (fwd/right) машины.
        """
        d = self._tuning.DRIVE

        ax = d.car_sprite_anchor_x
        ay = d.car_sprite_anchor_y

        steer_sign = 0.0
        steer_abs = 0.0
        if self._steer_input < 0:
            steer_sign = -1.0
            steer_abs = 1.0
        elif self._steer_input > 0:
            steer_sign = 1.0
            steer_abs = 1.0

        rear_px = d.hitbox_rear_px
        rear_py = d.hitbox_rear_py
        front_px = d.hitbox_front_px
        front_py = d.hitbox_front_py

        if d.car_turn_pose_enabled and steer_abs > 0.0:
            rear_px += steer_sign * d.hitbox_turn_rear_dx
            rear_py += steer_abs * d.hitbox_turn_rear_dy
            front_px += steer_sign * d.hitbox_turn_front_dx
            front_py += steer_abs * d.hitbox_turn_front_dy

        rear_right = rear_px - ax
        rear_fwd = -(rear_py - ay)
        front_right = front_px - ax
        front_fwd = -(front_py - ay)

        fwd_x = self._fwd_x
        fwd_y = self._fwd_y
        right_x = -fwd_y
        right_y = fwd_x

        x = self._x
        y = self._y

        rear_x = x + fwd_x * rear_fwd + right_x * rear_right
        rear_y = y + fwd_y * rear_fwd + right_y * rear_right
        front_x = x + fwd_x * front_fwd + right_x * front_right
        front_y = y + fwd_y * front_fwd + right_y * front_right

        rear_r = d.hitbox_rear_radius
        front_r = d.hitbox_front_radius
        if rear_r < 0.0:
            rear_r = 0.0
        if front_r < 0.0:
            front_r = 0.0

        return rear_x, rear_y, rear_r, front_x, front_y, front_r

    def hitbox_road_circles(self) -> tuple[float, float, float, float, float, float]:
        """Возвращает 2 круговых хитбокса машины (rear/front) в road-space.

        Формат: (rear_s, rear_d, rear_r, front_s, front_d, front_r).

        Зачем это нужно:
        - зоны/препятствия живут в координатах дороги (s вдоль, d поперёк);
        - игрок ориентируется по спрайту, а хитбоксы настроены под спрайт;
        - значит, пересечения с зонами должны проверяться по хитбоксам, а не по
          “центральной точке физики”.

        Реализация:
        - берём world позиции кругов,
        - отдельно проецируем каждую точку на ближайшую часть centerline в окне
          вокруг текущего `road_idx`.

        Примечание: это стабильнее, чем “локально-линейная” проекция через одну
        касательную в `road_s`, и лучше совпадает с тем, что игрок видит в кадре.
        """
        rear_x, rear_y, rear_r, front_x, front_y, front_r = self.hitbox_world_circles()
        idx0 = self._road_idx
        rear_s, rear_d = self._project_world_to_road_near_idx(rear_x, rear_y, idx0)
        front_s, front_d = self._project_world_to_road_near_idx(front_x, front_y, idx0)
        return rear_s, rear_d, rear_r, front_s, front_d, front_r

    def _project_world_to_road_near_idx(self, x: float, y: float, idx_guess: int) -> tuple[float, float]:
        """Проецирует world точку (x,y) в координаты дороги (s,d) около idx_guess.

        Возвращает:
        - s: прогресс по дороге (float, может быть между дискретными шагами)
        - d: смещение вправо от centerline (положительное = справа)
        """
        n = self._road.center_points_len()
        if n <= 0:
            return 0.0, 0.0

        start = idx_guess - 30
        end = idx_guess + 30
        if start < 0:
            start = 0
        if end > n - 1:
            end = n - 1

        best_i = start
        best_d2 = 1.0e30
        best_cx = 0.0
        best_cy = 0.0
        best_dx = 1.0
        best_dy = 0.0

        i = start
        while i <= end:
            cx, cy, dx, dy = self._road.center_point_at_index(i)
            ox = x - cx
            oy = y - cy
            d2 = ox * ox + oy * oy
            if d2 < best_d2:
                best_d2 = d2
                best_i = i
                best_cx = cx
                best_cy = cy
                best_dx = dx
                best_dy = dy
            i += 1

        # Локальные координаты относительно ближайшей точки centerline.
        ox = x - best_cx
        oy = y - best_cy
        s = best_i * self._road.ds + (ox * best_dx + oy * best_dy)

        right_x = -best_dy
        right_y = best_dx
        d = ox * right_x + oy * right_y
        return s, d

    def _apply_zone_boost(self, dt: float) -> None:
        """Применяет ускорялку зоны (если активна) к (vx, vy) в этом кадре."""
        forward = self._zone_boost_forward
        center = self._zone_boost_center
        if forward <= 0.0 and center <= 0.0:
            return
        if dt <= 0.0:
            return

        # Направление и нормаль дороги берём по текущему road_s (из прошлого кадра).
        dir_x, dir_y = self._road.direction_at(self._road_s)
        nrm_x = -dir_y
        nrm_y = dir_x

        ax = dir_x * forward
        ay = dir_y * forward

        if center > 0.0:
            # Пуш к центру: если d>0 (правее центра) -> толкаем влево (-nrm).
            # Если d<0 -> толкаем вправо (+nrm).
            if self._road_d > 0.0:
                ax -= nrm_x * center
                ay -= nrm_y * center
            elif self._road_d < 0.0:
                ax += nrm_x * center
                ay += nrm_y * center

        self._vx += ax * dt
        self._vy += ay * dt

    def _rotate_heading(self, delta: float) -> None:
        """Поворачивает направление машины на маленький угол `delta` (в радианах).

        Мы избегаем `math.sin/cos`: используем приближение малых углов и затем
        нормализуем вектор, чтобы он оставался unit-длины.
        """
        dx = self._fwd_x
        dy = self._fwd_y

        c = 1.0 - 0.5 * delta * delta
        s = delta
        ndx = dx * c - dy * s
        ndy = dx * s + dy * c

        l2 = ndx * ndx + ndy * ndy
        if l2 > 0.0:
            inv = 1.0 / (l2 ** 0.5)
            ndx *= inv
            ndy *= inv

        self._fwd_x = ndx
        self._fwd_y = ndy

    def _update_road_projection(self) -> None:
        """Обновляет (road_s, road_d, offroad) по текущей world позиции.

        Идея:
        - ищем ближайшую точку centerline в окне индексов вокруг предыдущей,
          чтобы было быстро и стабильно;
        - d считаем как проекцию на нормаль “вправо” от дороги.
        """
        n = self._road.center_points_len()
        if n <= 0:
            self._road_s = 0.0
            self._road_d = 0.0
            self._offroad = False
            return

        idx0 = self._road_idx
        start = idx0 - 40
        end = idx0 + 80
        if start < 0:
            start = 0
        if end > n - 1:
            end = n - 1

        best_i = start
        best_d2 = 1.0e30
        best_cx = 0.0
        best_cy = 0.0
        best_dx = 1.0
        best_dy = 0.0

        i = start
        while i <= end:
            cx, cy, dx, dy = self._road.center_point_at_index(i)
            ox = self._x - cx
            oy = self._y - cy
            d2 = ox * ox + oy * oy
            if d2 < best_d2:
                best_d2 = d2
                best_i = i
                best_cx = cx
                best_cy = cy
                best_dx = dx
                best_dy = dy
            i += 1

        max_far = self._road.road_width * self._road.road_width * 64.0
        if best_d2 > max_far:
            best_i = 0
            best_d2 = 1.0e30
            i = 0
            while i < n:
                cx, cy, dx, dy = self._road.center_point_at_index(i)
                ox = self._x - cx
                oy = self._y - cy
                d2 = ox * ox + oy * oy
                if d2 < best_d2:
                    best_d2 = d2
                    best_i = i
                    best_cx = cx
                    best_cy = cy
                    best_dx = dx
                    best_dy = dy
                i += 1

        self._road_idx = best_i
        self._road_s = best_i * self._road.ds

        # Важно: знак `road_d` должен совпадать со знаком `d` у объектов дороги (Obstacle/Zone).
        #
        # Для world позиции объектов мы используем нормаль `nrm = (-dir_y, dir_x)`:
        #   world = center + nrm * d
        #
        # Поэтому и `road_d` считаем по той же оси `nrm`, иначе всё “зеркалится”:
        # зона/препятствие рисуются справа, а `road_d` говорит, что это слева.
        right_x = -best_dy
        right_y = best_dx
        self._road_d = (self._x - best_cx) * right_x + (self._y - best_cy) * right_y

        width = self._road.width_at(self._road_s)
        self._offroad = abs(self._road_d) > (width * 0.5)

    @staticmethod
    def _approach(value: float, target: float, amount: float) -> float:
        """Двигает `value` к `target` не быстрее чем на `amount` за шаг."""
        if value < target:
            value += amount
            if value > target:
                value = target
            return value
        if value > target:
            value -= amount
            if value < target:
                value = target
            return value
        return value
