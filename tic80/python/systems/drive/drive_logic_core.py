from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...contracts import Tuning
    from ...core.run_state import RunState

    from .road_model import RoadModel
    from .drive_logic_projection import (
        drive_hitbox_road_circles,
        drive_hitbox_world_circles,
        drive_project_world_to_road_near_idx,
        drive_update_road_projection
    )
    from .drive_logic_utils import (
        drive_logic_update_dash_cooldown,
        drive_logic_speed_factor,
        drive_logic_estimated_vmax
    )
    from .drive_logic_controls import (
        drive_logic_apply_steering,
        drive_logic_apply_handbrake_steer_boost,
        drive_logic_apply_dash,
        drive_logic_apply_longitudinal,
        drive_logic_apply_handbrake_decel,
        drive_logic_clamp_v_fwd
    )
    from .drive_logic_lateral import (
        drive_logic_effective_grip,
        drive_logic_apply_lateral_damping,
        drive_logic_apply_zone_antislip,
        drive_logic_apply_side_recovery
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
        return float(v2 ** 0.5)

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
        return drive_logic_estimated_vmax(self, False)

    def estimated_vmax_offroad(self) -> float:
        """Оценивает "крейсерскую максималку" (плато) на оффроуде."""
        return drive_logic_estimated_vmax(self, True)

    def _estimated_vmax(self, offroad: bool) -> float:
        """Внутренняя оценка плато скорости при постоянном газе.

        Упрощённая модель как в коде:
          dv/dt = +accel - (drag_lin + drag_quad*|v|) * v

        Равновесие:
          accel ≈ (drag_lin + drag_quad*v) * v
          => drag_quad*v^2 + drag_lin*v - accel ≈ 0
        """
        return drive_logic_estimated_vmax(self, offroad)

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

    @property
    def dbg_handbrake_decel(self) -> float:
        """Эффективное замедление от ручника в этом кадре (units/sec^2), для дебага.

        Это уже “посчитанное” значение с учётом:
        - скорости (через speed_factor и handbrake_decel_min_speed_factor)
        - газа и поворота (через handbrake_decel_throttle_*_mult)
        """
        return self._dbg_handbrake_decel

    @property
    def dbg_side_recovery(self) -> float:
        """Сколько скорости мы “вернули” из заноса в продольную ось в этом кадре (units/sec).

        Аркадный приём: часть схлопнутой боковой скорости переводим в `v_forward`, чтобы
        в повороте под газом машина не теряла темп “сама по себе”.
        """
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
        self._dbg_handbrake_decel = 0.0
        self._dbg_side_recovery = 0.0

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
            steer_input,
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
        v_fwd = self._step_apply_side_recovery(v_fwd, v_side_before, v_side, throttle, speed_factor)
        v_fwd = self._step_clamp_v_fwd(v_fwd)
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
        self._step_apply_offroad_damage(dt)

    def _step_update_dash_cooldown(self, dt: float) -> None:
        """Обновляет внутренний таймер кулдауна рывка (dash)."""
        drive_logic_update_dash_cooldown(self, dt)

    @staticmethod
    def _step_speed_factor(speed: float, max_speed: float) -> float:
        """Нормализует скорость в диапазон 0..1 (для тюнинга рулёжки/заноса)."""
        return drive_logic_speed_factor(speed, max_speed)

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

    def _step_apply_handbrake_steer_boost(self, yaw: float, speed_factor: float) -> float:
        """Усиливает руление от ручника (B) только на скорости.

        Идея: на низкой скорости ручник не должен “читерить”, а на высокой — помогает
        довернуть (эффект а-ля Mario Kart).
        """
        return drive_logic_apply_handbrake_steer_boost(self, yaw, speed_factor)

    def _step_apply_dash(self, v_fwd: float, dash_pressed: bool) -> float:
        """Применяет рывок вперёд (dash), если включён тюнингом и нет кулдауна."""
        return drive_logic_apply_dash(self, v_fwd, dash_pressed)

    def _step_apply_longitudinal(
        self,
        dt: float,
        v_fwd: float,
        throttle: bool,
        brake: bool,
        handbrake: bool,
        steer_input: int,
        speed_factor: float
    ) -> float:
        """Продольная динамика: газ/тормоз/накат + доп. замедление от ручника."""
        return drive_logic_apply_longitudinal(
            self,
            dt,
            v_fwd,
            throttle,
            brake,
            handbrake,
            steer_input,
            speed_factor
        )

    def _step_apply_handbrake_decel(
        self,
        dt: float,
        v_fwd: float,
        throttle: bool,
        steer_input: int,
        speed_factor: float
    ) -> float:
        """Замедление от ручника: сильнее ощущается на скорости, слабее под газом."""
        return drive_logic_apply_handbrake_decel(
            self,
            dt,
            v_fwd,
            throttle,
            steer_input,
            speed_factor
        )

    def _step_clamp_v_fwd(self, v_fwd: float) -> float:
        """Ограничивает задний ход и (опционально) верхнюю скорость по оси вперёд."""
        return drive_logic_clamp_v_fwd(self, v_fwd)

    def _step_effective_grip(self, handbrake: bool, offroad_before: bool) -> float:
        """Считает effective_grip для этого кадра и пишет dbg_effective_grip."""
        return drive_logic_effective_grip(self, handbrake, offroad_before)

    def _step_apply_lateral_damping(
        self,
        dt: float,
        v_side: float,
        effective_grip: float,
        speed_factor: float
    ) -> float:
        """Гасит боковую скорость (занос) в текущем кадре через side_friction."""
        return drive_logic_apply_lateral_damping(
            self,
            dt,
            v_side,
            effective_grip,
            speed_factor
        )

    def _step_apply_zone_antislip(self, dt: float, v_side: float) -> float:
        """Дополнительно гасит боковую скорость внутри зоны (ускорялки).

        Идея: бустер — “безопасная полоса”.
        Если игрок еле удержался и попал на панель на повороте, занос гасится быстрее,
        и машину проще стабилизировать.

        Реализация — мультипликативное демпфирование:
          v_side *= clamp(1 - k * dt, 0..1)
        Где `k` — `TUNING.DRIVE.zone_antislip` (единицы: 1/sec).
        """
        return drive_logic_apply_zone_antislip(self, dt, v_side)

    def _step_apply_side_recovery(
        self,
        v_fwd: float,
        v_side_before: float,
        v_side_after: float,
        throttle: bool,
        speed_factor: float
    ) -> float:
        """Частично переводит “схлопнутую” боковую скорость в продольную.

        Без этого эффекта игрок часто ощущает “в повороте тормозит”, потому что:
        - при повороте часть скорости становится боковой (`v_side`)
        - боковое трение гасит `v_side`, уменьшая модуль скорости

        Мы делаем аркадный компромисс:
        - только под газом,
        - только после порога скорости,
        - и только долю потерь,
        возвращаем в `v_forward`.
        """
        return drive_logic_apply_side_recovery(
            self,
            v_fwd,
            v_side_before,
            v_side_after,
            throttle,
            speed_factor
        )

    def _step_apply_drag(self, dt: float) -> None:
        """Общие сопротивления движения + добавка от оффроуда.

        Модель (векторно):
          dv/dt = -C_lin * v - C_quad * v * |v|

        Оффроуд добавляет к C_lin/C_quad свои коэффициенты (вязкость/песок),
        чтобы на высокой скорости темп падал, но на низкой можно было выбраться обратно.
        """
        drive_logic_apply_drag(self, dt)

    def _step_apply_fuel(self, dt: float, throttle: bool) -> None:
        """Списывает топливо по текущему вводу и поверхности (оффроуд дороже)."""
        drive_logic_apply_fuel(self, dt, throttle)

    def _step_apply_offroad_damage(self, dt: float) -> None:
        """Наносит небольшой урон за езду по оффроуду (rate * dt).

        Важно: урон должен быть только при движении. Стоя на месте вне дороги, игрок
        не должен терять hp.
        """
        drive_logic_apply_offroad_damage(self, dt)

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
        return drive_hitbox_world_circles(self)

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
        return drive_hitbox_road_circles(self)

    def _project_world_to_road_near_idx(self, x: float, y: float, idx_guess: int) -> tuple[float, float]:
        """Проецирует world точку (x,y) в координаты дороги (s,d) около idx_guess.

        Возвращает:
        - s: прогресс по дороге (float, может быть между дискретными шагами)
        - d: смещение вправо от centerline (положительное = справа)
        """
        return drive_project_world_to_road_near_idx(self, x, y, idx_guess)

    def _apply_zone_boost(self, dt: float) -> None:
        """Применяет ускорялку зоны (если активна) к (vx, vy) в этом кадре."""
        drive_logic_apply_zone_boost(self, dt)

    def _rotate_heading(self, delta: float) -> None:
        """Поворачивает heading на малый угол `delta` (в радианах)."""
        drive_logic_rotate_heading(self, delta)

    def _update_road_projection(self) -> None:
        """Обновляет (road_s, road_d, offroad) по текущей world позиции.

        Идея:
        - ищем ближайшую точку centerline в окне индексов вокруг предыдущей,
          чтобы было быстро и стабильно;
        - d считаем как проекцию на нормаль “вправо” от дороги.
        """
        drive_update_road_projection(self)
