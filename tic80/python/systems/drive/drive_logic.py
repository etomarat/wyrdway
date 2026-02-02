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

    def update(
        self,
        dt: float,
        steer_input: int,
        throttle: bool,
        brake: bool,
        handbrake: bool
    ) -> None:
        """Обновляет физику машины на один шаг `dt`.

        Управление:
        - throttle (UP): разгон вперёд
        - brake (DOWN): тормоз, а при почти нулевой скорости — задний ход
        - steer_input (LEFT/RIGHT): поворот направления машины
        - handbrake (B): снижает сцепление => больше заноса, чуть резче поворот

        Важно: если вообще не рулить, машина едет “как направлена”, а дорога
        уходит в сторону на поворотах. То есть “автопилота” нет.
        """
        d = self._tuning.DRIVE
        self._steer_input = steer_input

        offroad_before = self._offroad

        speed = self.speed
        speed_factor = 0.0
        if d.max_speed > 0:
            speed_factor = speed / d.max_speed
        if speed_factor > 1.0:
            speed_factor = 1.0

        steer_scale = speed_factor
        if speed < 0.5:
            steer_scale = 0.0
        yaw = steer_input * d.steer_rate * steer_scale * dt
        if handbrake:
            yaw *= 1.40
        if offroad_before:
            yaw *= 0.80
        if yaw != 0.0:
            self._rotate_heading(yaw)

        fwd_x = self._fwd_x
        fwd_y = self._fwd_y
        right_x = -fwd_y
        right_y = fwd_x

        v_fwd = self._vx * fwd_x + self._vy * fwd_y
        v_side = self._vx * right_x + self._vy * right_y

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

        side_damp = 1.0 - d.side_friction * effective_grip * dt
        slip = 1.0 + d.side_slip_speed_mult * speed_factor
        if slip < 1.0:
            slip = 1.0
        side_damp = 1.0 - (d.side_friction * effective_grip * dt) / slip
        if side_damp < 0.0:
            side_damp = 0.0
        if side_damp > 1.0:
            side_damp = 1.0
        v_side *= side_damp

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
