from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .rumble import rumble_try


class Haptics:
    __slots__ = (
        "_steps",
        "_step_index",
        "_step_wait_s",
        "_active",
        "_pulse_weak",
        "_pulse_strong",
        "_pulse_time_s",
        "_gravel_weak",
        "_gravel_strong",
        "_engine_base_weak",
        "_engine_base_strong",
        "_engine_level",
        "_engine_pulse_weak",
        "_engine_pulse_strong",
        "_engine_pulse_time_s",
        "_engine_cycle_time_s",
        "_drift_base_weak",
        "_drift_base_strong",
        "_drift_level",
        "_drift_pulse_weak",
        "_drift_pulse_strong",
        "_drift_pulse_time_s",
        "_drift_cycle_time_s",
        "_drive_duck_time_s",
        "_drive_duck_n",
        "_rumble_refresh_s",
        "_last_sent_weak",
        "_last_sent_strong"
    )

    def __init__(self) -> None:
        self._steps: list[tuple[int, int, int, int]] = []
        self._step_index = -1
        self._step_wait_s = 0.0
        self._active = False
        self._pulse_weak = 0
        self._pulse_strong = 0
        self._pulse_time_s = 0.0
        self._gravel_weak = 0
        self._gravel_strong = 0
        self._engine_base_weak = 0
        self._engine_base_strong = 0
        self._engine_level = 0.0
        self._engine_pulse_weak = 0
        self._engine_pulse_strong = 0
        self._engine_pulse_time_s = 0.0
        self._engine_cycle_time_s = 0.0
        self._drift_base_weak = 0
        self._drift_base_strong = 0
        self._drift_level = 0.0
        self._drift_pulse_weak = 0
        self._drift_pulse_strong = 0
        self._drift_pulse_time_s = 0.0
        self._drift_cycle_time_s = 0.0
        self._drive_duck_time_s = 0.0
        self._drive_duck_n = 0.0
        self._rumble_refresh_s = 0.0
        self._last_sent_weak = 0
        self._last_sent_strong = 0

    def clear(self) -> None:
        self._clear_pattern()
        self._pulse_weak = 0
        self._pulse_strong = 0
        self._pulse_time_s = 0.0
        self.clear_drive_feedback()
        self._flush_rumble(True)

    def clear_drive_feedback(self) -> None:
        self._gravel_weak = 0
        self._gravel_strong = 0
        self._engine_base_weak = 0
        self._engine_base_strong = 0
        self._engine_level = 0.0
        self._engine_pulse_weak = 0
        self._engine_pulse_strong = 0
        self._engine_pulse_time_s = 0.0
        self._engine_cycle_time_s = 0.0
        self._drift_base_weak = 0
        self._drift_base_strong = 0
        self._drift_level = 0.0
        self._drift_pulse_weak = 0
        self._drift_pulse_strong = 0
        self._drift_pulse_time_s = 0.0
        self._drift_cycle_time_s = 0.0
        self._drive_duck_time_s = 0.0
        self._drive_duck_n = 0.0
        self._flush_rumble(True)

    def set_drive_feedback(self, gravel: float, engine: float, drift: float) -> None:
        gravel_n = self._clamp01(gravel)
        engine_n = self._clamp01(engine)
        drift_n = self._clamp01(drift)
        self._engine_level = engine_n
        self._drift_level = drift_n
        self._gravel_weak = self._scale_int(0, 9500, gravel_n)
        self._gravel_strong = self._scale_int(0, 5500, gravel_n)
        self._engine_base_weak = self._scale_int(0, 450, engine_n)
        self._engine_base_strong = self._scale_int(0, 3200, engine_n)
        self._drift_base_weak = self._scale_int(0, 1100, drift_n)
        self._drift_base_strong = self._scale_int(0, 2400, drift_n)

    def update(self, dt: float) -> None:
        dt_s = float(dt)
        if self._pulse_time_s > 0.0:
            self._pulse_time_s -= dt_s
            if self._pulse_time_s <= 0.0:
                self._pulse_time_s = 0.0
                self._pulse_weak = 0
                self._pulse_strong = 0
        if self._engine_pulse_time_s > 0.0:
            self._engine_pulse_time_s -= dt_s
            if self._engine_pulse_time_s <= 0.0:
                self._engine_pulse_time_s = 0.0
                self._engine_pulse_weak = 0
                self._engine_pulse_strong = 0
        if self._drift_pulse_time_s > 0.0:
            self._drift_pulse_time_s -= dt_s
            if self._drift_pulse_time_s <= 0.0:
                self._drift_pulse_time_s = 0.0
                self._drift_pulse_weak = 0
                self._drift_pulse_strong = 0
        if self._drive_duck_time_s > 0.0:
            self._drive_duck_time_s -= dt_s
            if self._drive_duck_time_s <= 0.0:
                self._drive_duck_time_s = 0.0
                self._drive_duck_n = 0.0
        if self._engine_level > 0.10:
            self._engine_cycle_time_s -= dt_s
            if self._engine_cycle_time_s <= 0.0:
                self._trigger_engine_pulse()
        else:
            self._engine_pulse_weak = 0
            self._engine_pulse_strong = 0
            self._engine_pulse_time_s = 0.0
            self._engine_cycle_time_s = 0.0
        if self._drift_level > 0.14:
            self._drift_cycle_time_s -= dt_s
            if self._drift_cycle_time_s <= 0.0:
                self._trigger_drift_pulse()
        else:
            self._drift_pulse_weak = 0
            self._drift_pulse_strong = 0
            self._drift_pulse_time_s = 0.0
            self._drift_cycle_time_s = 0.0
        if self._active:
            self._step_wait_s -= dt_s
            while self._active and self._step_wait_s <= 0.0:
                next_step = self._step_index + 1
                if next_step >= len(self._steps):
                    self._clear_pattern()
                    break
                if not self._play_step(next_step):
                    self._clear_pattern()
                    break
        if self._rumble_refresh_s > 0.0:
            self._rumble_refresh_s -= dt_s
            if self._rumble_refresh_s < 0.0:
                self._rumble_refresh_s = 0.0
        self._flush_rumble(False)

    def play_engine_startup(self) -> None:
        self._start_pattern([
            # Short startup: two quick roars.
            (9000, 32000, 120, 200),
            (0, 0, 40, 120),
            (13000, 43000, 160, 220),
            (4500, 12000, 90, 0)
        ])

    def pulse(self, weak: int, strong: int, duration: int = 120) -> bool:
        self._clear_pattern()
        self._set_pulse(weak, strong, duration)
        return self._flush_rumble(True)

    def fail(self) -> None:
        self._start_pattern([
            (900, 4200, 30, 88),
            (2600, 13000, 58, 0)
        ])

    def success(self) -> None:
        self._start_pattern([
            (0, 18000, 26, 98),
            (300, 11000, 30, 0)
        ])

    def burnout_start(self) -> None:
        self._start_pattern([
            (8500, 26000, 150, 220),
            (5200, 15500, 135, 200),
            (10800, 32000, 170, 230),
            (6800, 19000, 145, 200),
            (3600, 9500, 180, 0)
        ])

    def offroad_transition(self, speed_n: float) -> None:
        t = self._clamp01(speed_n)
        self._start_pattern([
            (
                self._scale_int(4500, 11000, t),
                self._scale_int(14000, 30000, t),
                self._scale_int(55, 90, t),
                70
            ),
            (
                self._scale_int(1800, 5200, t),
                self._scale_int(6000, 14000, t),
                50,
                0
            )
        ])

    def booster_enter(self, speed_n: float) -> None:
        t = self._clamp01(speed_n)
        self._drive_duck_n = 0.82
        self._drive_duck_time_s = 0.16
        self._start_pattern([
            (
                self._scale_int(7000, 12000, t),
                self._scale_int(22000, 32000, t),
                self._scale_int(78, 98, t),
                self._scale_int(78, 98, t)
            ),
            (
                self._scale_int(4200, 7600, t),
                self._scale_int(14000, 22000, t),
                self._scale_int(65, 82, t),
                0
            )
        ])

    def obstacle_hit(self, impact: float) -> None:
        impact_n = self._clamp01(float(impact) / 28.0)
        if impact_n <= 0.05:
            return
        weak = self._scale_int(2500, 12000, impact_n)
        strong = self._scale_int(12000, 43000, impact_n)
        duration = self._scale_int(45, 105, impact_n)
        if impact_n < 0.55:
            self.pulse(weak, strong, duration)
            return
        self._start_pattern([
            (weak, strong, duration, duration + 25),
            (0, 0, 22, 28),
            (
                self._scale_int(1800, 6200, impact_n),
                self._scale_int(7000, 18000, impact_n),
                55,
                0
            )
        ])

    def pursuer_strike(self, hp_loss: int, intensity: float) -> None:
        hp_n = self._clamp01(float(hp_loss) / 8.0)
        strike_n = self._clamp01(float(intensity) / 22.0)
        total_n = strike_n
        if hp_n > total_n:
            total_n = hp_n
        self._start_pattern([
            (
                self._scale_int(7000, 15000, total_n),
                self._scale_int(22000, 43000, total_n),
                self._scale_int(75, 120, total_n),
                95
            ),
            (0, 0, 26, 36),
            (
                self._scale_int(5000, 11000, total_n),
                self._scale_int(15000, 28000, total_n),
                self._scale_int(60, 95, total_n),
                0
            )
        ])

    def _clear_pattern(self) -> None:
        self._steps = []
        self._step_index = -1
        self._step_wait_s = 0.0
        self._active = False

    def _start_pattern(self, steps: list[tuple[int, int, int, int]]) -> None:
        self._clear_pattern()
        if not steps:
            return
        self._steps = list(steps)
        self._active = True
        if not self._play_step(0):
            self._clear_pattern()

    def _play_step(self, step_index: int) -> bool:
        weak, strong, duration, wait_ms = self._steps[step_index]
        self._set_pulse(weak, strong, duration)
        self._step_index = step_index
        self._step_wait_s = wait_ms / 1000.0
        return self._flush_rumble(True)

    def _set_pulse(self, weak: int, strong: int, duration: int) -> None:
        duration_ms = int(duration)
        if duration_ms <= 0:
            self._pulse_weak = 0
            self._pulse_strong = 0
            self._pulse_time_s = 0.0
            return
        self._pulse_weak = self._clamp_motor(weak)
        self._pulse_strong = self._clamp_motor(strong)
        self._pulse_time_s = duration_ms / 1000.0

    def _flush_rumble(self, force: bool) -> bool:
        weak = self._combined_weak()
        strong = self._combined_strong()
        changed = weak != self._last_sent_weak or strong != self._last_sent_strong
        active = weak > 0 or strong > 0
        if not force:
            if not changed:
                if not active:
                    return True
                if self._rumble_refresh_s > 0.0:
                    return True
        duration = 0
        if active:
            duration = 90
        ok = bool(rumble_try(0, weak, strong, duration))
        if ok:
            self._last_sent_weak = weak
            self._last_sent_strong = strong
            if active:
                self._rumble_refresh_s = 0.04
            else:
                self._rumble_refresh_s = 0.0
        return ok

    def _combined_weak(self) -> int:
        drive_mult = self._drive_feedback_mult()
        return self._clamp_motor(
            self._gravel_weak
            + self._pulse_weak
            + self._scaled_motor(self._engine_base_weak, drive_mult)
            + self._scaled_motor(self._engine_pulse_weak, drive_mult)
            + self._scaled_motor(self._drift_base_weak, drive_mult)
            + self._scaled_motor(self._drift_pulse_weak, drive_mult)
        )

    def _combined_strong(self) -> int:
        drive_mult = self._drive_feedback_mult()
        return self._clamp_motor(
            self._gravel_strong
            + self._pulse_strong
            + self._scaled_motor(self._engine_base_strong, drive_mult)
            + self._scaled_motor(self._engine_pulse_strong, drive_mult)
            + self._scaled_motor(self._drift_base_strong, drive_mult)
            + self._scaled_motor(self._drift_pulse_strong, drive_mult)
        )

    def _trigger_engine_pulse(self) -> None:
        pulse_n = (self._engine_level - 0.10) / 0.90
        pulse_n = self._clamp01(pulse_n)
        self._engine_pulse_weak = self._scale_int(700, 1600, pulse_n)
        self._engine_pulse_strong = self._scale_int(2600, 7200, pulse_n)
        self._engine_pulse_time_s = self._scale_int(20, 34, pulse_n) / 1000.0
        self._engine_cycle_time_s = self._scale_int(230, 120, pulse_n) / 1000.0

    def _trigger_drift_pulse(self) -> None:
        pulse_n = (self._drift_level - 0.14) / 0.86
        pulse_n = self._clamp01(pulse_n)
        self._drift_pulse_weak = self._scale_int(1800, 5200, pulse_n)
        self._drift_pulse_strong = self._scale_int(5200, 16000, pulse_n)
        self._drift_pulse_time_s = self._scale_int(24, 42, pulse_n) / 1000.0
        self._drift_cycle_time_s = self._scale_int(155, 82, pulse_n) / 1000.0

    @staticmethod
    def _clamp01(value: float) -> float:
        if value <= 0.0:
            return 0.0
        if value >= 1.0:
            return 1.0
        return value

    @staticmethod
    def _scale_int(low: int, high: int, t: float) -> int:
        t_i = Haptics._clamp01(t)
        return int(low + (high - low) * t_i)

    def _drive_feedback_mult(self) -> float:
        if self._drive_duck_time_s <= 0.0:
            return 1.0
        n = self._clamp01(self._drive_duck_n)
        return 1.0 - n

    @staticmethod
    def _scaled_motor(value: int, mult: float) -> int:
        return int(value * mult)

    @staticmethod
    def _clamp_motor(value: int) -> int:
        value_i = int(value)
        if value_i <= 0:
            return 0
        if value_i >= 65535:
            return 65535
        return value_i
