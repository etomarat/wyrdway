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

    def __init__(self, run: "RunState", road: "RoadModel", tuning: "Tuning") -> None:
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

        self._init_on_road_start()

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

        speed = self.speed
        if self._dash_cd > 0.0:
            self._dash_cd -= dt
            if self._dash_cd < 0.0:
                self._dash_cd = 0.0
        speed_factor = 0.0
        if d.max_speed > 0:
            speed_factor = speed / d.max_speed
        if speed_factor > 1.0:
            speed_factor = 1.0
        self._dbg_speed_factor = speed_factor

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
            # Усиление руления от ручника должно зависеть от скорости:
            # на низкой скорости ручник не “читерит”, а на высокой помогает довернуть.
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
            hb_gain = d.handbrake_steer_mult - 1.0
            yaw *= 1.0 + hb_gain * hb_t
        if offroad_before:
            yaw *= d.offroad_steer_mult
        if yaw != 0.0:
            self._rotate_heading(yaw)

        fwd_x = self._fwd_x
        fwd_y = self._fwd_y
        right_x = -fwd_y
        right_y = fwd_x

        v_fwd = self._vx * fwd_x + self._vy * fwd_y
        v_side = self._vx * right_x + self._vy * right_y

        if dash_pressed and d.dash_impulse > 0.0 and self._dash_cd <= 0.0:
            # Dash = резкое добавление продольной скорости (как “нитро/аномалия”).
            # В базовой игре выключено через tuning (dash_impulse=0).
            v_fwd += d.dash_impulse
            self._dash_cd = d.dash_cooldown

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
            # Ручник должен “съедать” скорость, особенно на высокой.
            # Иначе он ощущается как бесполезная кнопка “сделать хуже сцепление”.
            hb_sf = speed_factor
            if hb_sf < d.handbrake_decel_min_speed_factor:
                hb_sf = d.handbrake_decel_min_speed_factor
            hb_decel = d.handbrake_decel * hb_sf
            if throttle:
                hb_decel *= d.handbrake_decel_throttle_mult
            v_fwd = self._approach(v_fwd, 0.0, hb_decel * dt)

        if v_fwd > d.max_speed:
            v_fwd = d.max_speed
        if v_fwd < -d.max_reverse_speed:
            v_fwd = -d.max_reverse_speed

        effective_grip = d.grip
        if handbrake:
            effective_grip *= d.handbrake_grip_mult
        if offroad_before:
            effective_grip *= d.offroad_grip_mult
        if effective_grip < 0.0:
            effective_grip = 0.0
        self._dbg_effective_grip = effective_grip

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

        self._vx = fwd_x * v_fwd + right_x * v_side
        self._vy = fwd_y * v_fwd + right_y * v_side

        self._x += self._vx * dt
        self._y += self._vy * dt

        self._update_road_projection()

        if self._offroad and d.offroad_slowdown > 0.0:
            slow = 1.0 - d.offroad_slowdown * dt
            if slow < 0.0:
                slow = 0.0
            self._vx *= slow
            self._vy *= slow

        fuel_spend = d.fuel_per_sec_idle * dt
        if throttle:
            fuel_spend += d.fuel_per_sec_throttle * dt
        if dt > 0.0:
            self._dbg_fuel_per_sec = fuel_spend / dt
        else:
            self._dbg_fuel_per_sec = 0.0
        if fuel_spend > 0.0:
            self._run.consume_fuel(fuel_spend)

    def finished(self) -> bool:
        """True, если игрок доехал по дороге до конца сегмента."""
        return self._road_s >= self._road.segment_total_length

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

        right_x = best_dy
        right_y = -best_dx
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
