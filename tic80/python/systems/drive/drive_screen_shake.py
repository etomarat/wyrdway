from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...data.tuning import Tuning
    from .rng import Rng


class _ShakeChannel:
    def __init__(self) -> None:
        self._x = 0.0
        self._y = 0.0
        self._target_x = 0.0
        self._target_y = 0.0
        self._time_to_next = 0.0

    def reset(self) -> None:
        self._x = 0.0
        self._y = 0.0
        self._target_x = 0.0
        self._target_y = 0.0
        self._time_to_next = 0.0

    def update(
        self,
        dt: float,
        rng: "Rng",
        amplitude: float,
        freq_hz: float,
        smooth_rate: float
    ) -> tuple[float, float]:
        if amplitude <= 0.0 or freq_hz <= 0.0:
            self._target_x = 0.0
            self._target_y = 0.0
            self._time_to_next = 0.0
        else:
            self._time_to_next -= dt
            if self._time_to_next <= 0.0:
                self._time_to_next = 1.0 / freq_hz
                dx = rng.rand01() * 2.0 - 1.0
                dy = rng.rand01() * 2.0 - 1.0
                l2 = dx * dx + dy * dy
                if l2 < 0.0001:
                    dx = 1.0
                    dy = 0.0
                else:
                    inv = 1.0 / (l2 ** 0.5)
                    dx *= inv
                    dy *= inv
                self._target_x = dx * amplitude
                self._target_y = dy * amplitude

        alpha = smooth_rate * dt
        if alpha < 0.0:
            alpha = 0.0
        if alpha > 1.0:
            alpha = 1.0
        self._x += (self._target_x - self._x) * alpha
        self._y += (self._target_y - self._y) * alpha
        return (self._x, self._y)


class DriveScreenShake:
    def __init__(self) -> None:
        self._seed: int | None = None
        self._rng: Rng | None = None
        self._offroad_level = 0.0
        self._hit_trauma = 0.0
        self._exhaust_level = 0.0
        self._exhaust_pulse_trauma = 0.0
        self._offroad_channel = _ShakeChannel()
        self._hit_channel = _ShakeChannel()
        self._exhaust_channel = _ShakeChannel()
        self._exhaust_pulse_channel = _ShakeChannel()

    def ensure_seed(self, seed: int) -> None:
        if self._seed == seed and self._rng is not None:
            return
        self._seed = seed
        self._rng = Rng(seed ^ 0xA5A5A5A5)
        self._offroad_level = 0.0
        self._hit_trauma = 0.0
        self._exhaust_level = 0.0
        self._exhaust_pulse_trauma = 0.0
        self._offroad_channel.reset()
        self._hit_channel.reset()
        self._exhaust_channel.reset()
        self._exhaust_pulse_channel.reset()

    def notify_hit(self, impact: float, tuning: "Tuning") -> None:
        d = tuning.DRIVE
        if impact <= 0.0:
            return
        add = impact * float(d.shake_hit_impact_mult)
        if add <= 0.0:
            return
        self._hit_trauma += add
        max_t = float(d.shake_hit_trauma_max)
        if max_t <= 0.0:
            max_t = 1.0
        if self._hit_trauma > max_t:
            self._hit_trauma = max_t

    def update(
        self,
        dt: float,
        offroad: bool,
        exhaust_strength: float,
        tuning: "Tuning"
    ) -> tuple[float, float]:
        rng = self._rng
        if rng is None:
            return (0.0, 0.0)

        d = tuning.DRIVE

        if offroad:
            rate = float(d.shake_offroad_ramp_up)
            self._offroad_level += rate * dt
            if self._offroad_level > 1.0:
                self._offroad_level = 1.0
        else:
            rate = float(d.shake_offroad_ramp_down)
            self._offroad_level -= rate * dt
            if self._offroad_level < 0.0:
                self._offroad_level = 0.0

        # Оффроуд: амплитуда = сила * уровень (0..1).
        offroad_amp = self._offroad_level * float(d.shake_offroad_strength)

        # Удар: травма убывает со скоростью decay (1/sec).
        decay = float(d.shake_hit_decay_per_sec)
        if decay > 0.0:
            self._hit_trauma -= decay * dt
            if self._hit_trauma < 0.0:
                self._hit_trauma = 0.0

        # Удар: амплитуда от травмы (квадрат — мягче на малых значениях).
        hit_amp = float(d.shake_hit_strength) * (self._hit_trauma * self._hit_trauma)

        # Выхлоп: целевой уровень (0..1) берём из визуального эффекта дыма.
        target_exhaust = float(exhaust_strength)
        if target_exhaust < 0.0:
            target_exhaust = 0.0
        if target_exhaust > 1.0:
            target_exhaust = 1.0
        if target_exhaust > self._exhaust_level:
            rate = float(d.shake_exhaust_ramp_up)
            self._exhaust_level += rate * dt
            if self._exhaust_level > target_exhaust:
                self._exhaust_level = target_exhaust
        else:
            rate = float(d.shake_exhaust_ramp_down)
            self._exhaust_level -= rate * dt
            if self._exhaust_level < target_exhaust:
                self._exhaust_level = target_exhaust

        # Выхлоп: плавный дрейф камеры (чем сильнее дым, тем выше амплитуда).
        exhaust_amp = self._exhaust_level * float(d.shake_exhaust_strength)

        # Редкие "толчки" от высокой скорости: вероятность и сила завязаны на дым.
        if self._exhaust_level > 0.0:
            chance = float(d.shake_exhaust_pulse_chance_per_sec) * self._exhaust_level
            if chance > 0.0 and rng.rand01() < chance * dt:
                self._exhaust_pulse_trauma += 1.0
                if self._exhaust_pulse_trauma > 1.0:
                    self._exhaust_pulse_trauma = 1.0

        pulse_decay = float(d.shake_exhaust_pulse_decay_per_sec)
        if pulse_decay > 0.0:
            self._exhaust_pulse_trauma -= pulse_decay * dt
            if self._exhaust_pulse_trauma < 0.0:
                self._exhaust_pulse_trauma = 0.0

        pulse_amp = float(d.shake_exhaust_pulse_strength)
        pulse_amp *= (self._exhaust_pulse_trauma * self._exhaust_pulse_trauma)

        off_x, off_y = self._offroad_channel.update(
            dt,
            rng,
            offroad_amp,
            float(d.shake_offroad_freq_hz),
            float(d.shake_offroad_freq_hz) * 1.2
        )
        hit_x, hit_y = self._hit_channel.update(
            dt,
            rng,
            hit_amp,
            float(d.shake_hit_freq_hz),
            float(d.shake_hit_smooth_rate)
        )
        ex_x, ex_y = self._exhaust_channel.update(
            dt,
            rng,
            exhaust_amp,
            float(d.shake_exhaust_freq_hz),
            float(d.shake_exhaust_smooth_rate)
        )
        pulse_x, pulse_y = self._exhaust_pulse_channel.update(
            dt,
            rng,
            pulse_amp,
            float(d.shake_exhaust_pulse_freq_hz),
            float(d.shake_exhaust_pulse_smooth_rate)
        )

        total_x = off_x + hit_x + ex_x + pulse_x
        total_y = off_y + hit_y + ex_y + pulse_y
        # Общий лимит по амплитуде (px).
        max_px = float(d.shake_max_px)
        if max_px > 0.0:
            m2 = total_x * total_x + total_y * total_y
            limit2 = max_px * max_px
            if m2 > limit2:
                inv = max_px / (m2 ** 0.5)
                total_x *= inv
                total_y *= inv

        return (total_x, total_y)
