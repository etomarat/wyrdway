from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...contracts import Tuning
    from ...core.run_state import RunState

    from .road_model import RoadModel
    from .drive_logic_utils import (
        drive_logic_update_dash_cooldown,
        drive_logic_speed_factor,
        drive_logic_estimated_vmax
    )
    from .drive_logic_controls import (
        drive_logic_apply_steering,
        drive_logic_apply_dash,
        drive_logic_apply_longitudinal,
        drive_logic_clamp_v_fwd
    )
    from .drive_logic_lateral import (
        drive_logic_effective_grip,
        drive_logic_apply_lateral_damping,
        drive_logic_apply_zone_antislip,
        drive_logic_apply_side_recovery
    )
    from .drive_logic_projection import (
        drive_hitbox_road_circles,
        drive_hitbox_world_circles,
        drive_project_world_to_road_near_idx,
        drive_update_road_projection
    )
    from .drive_logic_post_step import (
        drive_logic_apply_drag,
        drive_logic_apply_fuel,
        drive_logic_apply_offroad_damage,
        drive_logic_apply_zone_boost
    )
    from .drive_logic_state import (
        drive_logic_set_zone_grip_mult,
        drive_logic_set_zone_boost,
        drive_logic_set_zone_antislip,
        drive_logic_set_zone_grip_floor,
        drive_logic_init_on_road_start,
        drive_logic_rotate_heading
    )


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
        self._dbg_handbrake_decel = 0.0
        self._dbg_side_recovery = 0.0
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
        """Задаёт множитель сцепления от дорожной зоны на следующий кадр.

        Важно: сама проверка «игрок в зоне или нет» делается во внешнем слое
        (`drive_zone_effects`), а здесь только применение значения к физике.
        """
        drive_logic_set_zone_grip_mult(self, mult)

    def set_zone_boost(self, forward_accel: float, center_accel: float) -> None:
        """Задаёт параметры ускорялки зоны на следующий кадр.

        - `forward_accel`: ускорение вдоль направления дороги.
        - `center_accel`: ускорение по нормали к центру трассы (`d -> 0`).
        """
        drive_logic_set_zone_boost(self, forward_accel, center_accel)

    def set_zone_antislip(self, strength: float) -> None:
        """Задаёт силу анти-заноса от зоны на следующий кадр.

        Это дополнительное гашение боковой скорости внутри зоны.
        """
        drive_logic_set_zone_antislip(self, strength)

    def set_zone_grip_floor(self, value: float) -> None:
        """Задаёт нижнюю границу effective_grip внутри зоны.

        Нужна как страховка, чтобы сцепление не падало слишком низко (например,
        при ручнике), пока игрок находится в буст-зоне.
        """
        drive_logic_set_zone_grip_floor(self, value)

    def set_preview_motion_state(
        self,
        x: float,
        y: float,
        fwd_x: float,
        fwd_y: float,
        vx: float,
        vy: float,
        dbg_handbrake_decel: float = 0.0
    ) -> None:
        """Задаёт scripted-состояние для превью/фоновых сцен.

        Используется вне обычного `update()` цикла (например, в main menu backdrop),
        чтобы не дублировать доступ к внутренним полям и держать проекцию на дорогу
        консистентной в одном месте.
        """
        nx = float(fwd_x)
        ny = float(fwd_y)
        l2 = nx * nx + ny * ny
        if l2 > 0.0001:
            inv = 1.0 / (l2 ** 0.5)
            nx *= inv
            ny *= inv
        else:
            nx = self._fwd_x
            ny = self._fwd_y

        self._x = float(x)
        self._y = float(y)
        self._fwd_x = nx
        self._fwd_y = ny
        self._vx = float(vx)
        self._vy = float(vy)
        self._dbg_handbrake_decel = float(dbg_handbrake_decel)
        drive_update_road_projection(self)

    def refresh_road_projection(self) -> None:
        drive_update_road_projection(self)

    @property
    def dbg_zone_boost_forward(self) -> float:
        return self._dbg_zone_boost_forward

    @property
    def dbg_zone_boost_center(self) -> float:
        return self._dbg_zone_boost_center

    @property
    def dbg_zone_antislip(self) -> float:
        return self._dbg_zone_antislip

    def _init_on_road_start(self) -> None:
        """Ставит машину в начало дороги и выравнивает по направлению трассы."""
        drive_logic_init_on_road_start(self)

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
    def vx(self) -> float:
        return self._vx

    @property
    def vy(self) -> float:
        return self._vy

    @property
    def speed(self) -> float:
        v2 = self._vx * self._vx + self._vy * self._vy
        return v2 ** 0.5

    @property
    def v_forward(self) -> float:
        return self._vx * self._fwd_x + self._vy * self._fwd_y

    @property
    def v_side(self) -> float:
        right_x = -self._fwd_y
        right_y = self._fwd_x
        return self._vx * right_x + self._vy * right_y

    def estimated_vmax_road(self) -> float:
        """Оценивает "крейсерскую максималку" (плато) на дороге.

        Это не жёсткий лимит: реальная скорость ниже на поворотах и при заносе, потому что
        часть энергии уходит в боковую скорость. Но оценка полезна, чтобы понимать,
        почему при текущих `accel/drag_*` машина стабилизируется примерно на X.
        """
        return drive_logic_estimated_vmax(self, False)

    def estimated_vmax_offroad(self) -> float:
        """Оценивает "крейсерскую максималку" (плато) на оффроуде."""
        return drive_logic_estimated_vmax(self, True)

    @property
    def road_s(self) -> float:
        return self._road_s

    @property
    def road_d(self) -> float:
        return self._road_d

    @property
    def offroad(self) -> bool:
        return self._offroad

    @property
    def steer_input(self) -> int:
        return self._steer_input

    @property
    def dbg_speed_factor(self) -> float:
        return self._dbg_speed_factor

    @property
    def dbg_steer_scale(self) -> float:
        return self._dbg_steer_scale

    @property
    def dbg_effective_grip(self) -> float:
        return self._dbg_effective_grip

    @property
    def dbg_side_damp(self) -> float:
        return self._dbg_side_damp

    @property
    def dbg_side_accel(self) -> float:
        return self._dbg_side_accel

    @property
    def dbg_fuel_per_sec(self) -> float:
        return self._dbg_fuel_per_sec

    @property
    def dbg_handbrake_decel(self) -> float:
        return self._dbg_handbrake_decel

    @property
    def dbg_side_recovery(self) -> float:
        return self._dbg_side_recovery

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

        Управление (логические действия, конкретные кнопки см. `00_spec/10_controls.md`):
        - throttle: разгон вперёд (клава: UP, пад: South/RT)
        - brake: тормоз, а при почти нулевой скорости — задний ход (клава: DOWN, пад: East/LT)
        - steer_input: поворот направления машины (LEFT/RIGHT)
        - handbrake: снижает сцепление => больше заноса, чуть резче поворот (клава: X, пад: West/LB)
        - module: слот модульной кнопки (клава: Z, пад: North/RB); сейчас это рывок вперёд, позже здесь могут жить нитро, ловушки и другие модули

        Важно: если вообще не рулить, машина едет “как направлена”, а дорога
        уходит в сторону на поворотах. То есть “автопилота” нет.
        """
        d = self._tuning.DRIVE
        self._steer_input = steer_input
        self._dbg_handbrake_decel = 0.0
        self._dbg_side_recovery = 0.0

        offroad_before = self._offroad

        drive_logic_update_dash_cooldown(self, dt)

        speed = self.speed
        speed_factor = drive_logic_speed_factor(speed, d.max_speed)
        self._dbg_speed_factor = speed_factor

        drive_logic_apply_steering(
            self,
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

        v_fwd = drive_logic_apply_dash(self, v_fwd, dash_pressed)
        v_fwd = drive_logic_apply_longitudinal(
            self,
            dt,
            v_fwd,
            throttle,
            brake,
            handbrake,
            steer_input,
            speed_factor
        )
        v_fwd = drive_logic_clamp_v_fwd(self, v_fwd)

        effective_grip = drive_logic_effective_grip(self, handbrake, offroad_before)
        v_side_before = v_side
        v_side = drive_logic_apply_lateral_damping(
            self,
            dt,
            v_side,
            effective_grip,
            speed_factor
        )
        v_side = drive_logic_apply_zone_antislip(self, dt, v_side)
        v_fwd = drive_logic_apply_side_recovery(
            self,
            v_fwd,
            v_side_before,
            v_side,
            throttle,
            speed_factor
        )
        v_fwd = drive_logic_clamp_v_fwd(self, v_fwd)
        if dt > 0.0:
            # dbg_side_accel должен отражать итоговое гашение заноса,
            # включая дополнительный анти-занос от зоны.
            self._dbg_side_accel = (v_side - v_side_before) / dt
        else:
            self._dbg_side_accel = 0.0

        self._vx = fwd_x * v_fwd + right_x * v_side
        self._vy = fwd_y * v_fwd + right_y * v_side

        drive_logic_apply_zone_boost(self, dt)

        self._x += self._vx * dt
        self._y += self._vy * dt

        drive_update_road_projection(self)

        drive_logic_apply_drag(self, dt)
        drive_logic_apply_fuel(self, dt, throttle)
        drive_logic_apply_offroad_damage(self, dt)

    def finished(self) -> bool:
        """True, если игрок доехал по дороге до конца сегмента."""
        return self._road_s >= self._road.segment_total_length

    def hitbox_world_circles(self) -> tuple[float, float, float, float, float, float]:
        return drive_hitbox_world_circles(self)

    def hitbox_road_circles(self) -> tuple[float, float, float, float, float, float]:
        return drive_hitbox_road_circles(self)

    def _project_world_to_road_near_idx(self, x: float, y: float, idx_guess: int) -> tuple[float, float]:
        return drive_project_world_to_road_near_idx(self, x, y, idx_guess)

    def _rotate_heading(self, delta: float) -> None:
        """Поворачивает heading на малый угол `delta` (в радианах)."""
        drive_logic_rotate_heading(self, delta)

    def _update_road_projection(self) -> None:
        drive_update_road_projection(self)
