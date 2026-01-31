from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...contracts import Tuning
    from ...core.run_state import RunState

    from .road_model import RoadModel


class DriveLogic:
    """Единая логика DRIVE (m1.5), независимая от варианта рендера.

    Координаты:
    - s: прогресс по сегменту (в "метрах"/юнитах road-space)
    - d: боковое смещение от центра дороги
    """

    def __init__(
        self,
        run: "RunState",
        road: "RoadModel",
        tuning: "Tuning"
    ) -> None:
        self._run = run
        self._road = road
        self._tuning = tuning

        self._s = 0.0
        self._d = 0.0
        self._speed = 0.0
        self._offroad = False

    @property
    def s(self) -> float:
        return self._s

    @property
    def d(self) -> float:
        return self._d

    @property
    def speed(self) -> float:
        return self._speed

    @property
    def offroad(self) -> bool:
        return self._offroad

    def update(
        self,
        dt: float,
        steer_input: int,
        throttle: bool,
        brake: bool,
        handbrake: bool
    ) -> None:
        d = self._tuning.DRIVE

        if throttle:
            self._speed = min(d.max_speed, self._speed + d.accel * dt)
        if brake:
            self._speed = max(0.0, self._speed - d.brake * dt)

        self._s += self._speed * dt
        if self._s < 0:
            self._s = 0.0

        width = self._road.width_at(self._s)
        self._offroad = abs(self._d) > (width * 0.5)

        effective_grip = d.grip
        if handbrake:
            effective_grip *= d.handbrake_grip_mult
        if self._offroad:
            effective_grip *= d.offroad_grip_mult
        if effective_grip <= 0:
            effective_grip = 0.001

        speed_factor = 0.0
        if d.max_speed > 0:
            speed_factor = self._speed / d.max_speed

        self._d += (steer_input * d.steer_rate * speed_factor * dt) / effective_grip

        if self._offroad and d.offroad_slowdown > 0:
            slow = 1.0 - d.offroad_slowdown * dt
            if slow < 0.0:
                slow = 0.0
            self._speed *= slow

        fuel_spend = d.fuel_per_sec_idle * dt
        if throttle:
            fuel_spend += d.fuel_per_sec_throttle * dt
        if fuel_spend > 0.0:
            self._run.consume_fuel(fuel_spend)

    def finished(self) -> bool:
        return self._s >= self._road.segment_total_length

