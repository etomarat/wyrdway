import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...data.tuning import TUNING
    from ...systems.drive.drive_logic_core import DriveLogic


class TopdownCameraRig:
    """Сглаживает направление камеры по heading/velocity и пружине yaw."""

    def __init__(self) -> None:
        self._cam_fwd_x = 1.0
        self._cam_fwd_y = 0.0
        self._cam_inited = False
        self._cam_angle = 0.0
        self._cam_ang_vel = 0.0
        self._cam_vel_x = 1.0
        self._cam_vel_y = 0.0

    def forward(self, logic: DriveLogic) -> tuple[float, float]:
        heading_x = logic.fwd_x
        heading_y = logic.fwd_y

        if not self._cam_inited:
            self._cam_fwd_x = heading_x
            self._cam_fwd_y = heading_y
            self._cam_vel_x = heading_x
            self._cam_vel_y = heading_y
            self._cam_angle = math.atan2(self._cam_fwd_y, self._cam_fwd_x)
            self._cam_ang_vel = 0.0
            self._cam_inited = True
            return (self._cam_fwd_x, self._cam_fwd_y)

        vel_speed = (logic.vx * logic.vx + logic.vy * logic.vy) ** 0.5

        speed_blend = self._speed_blend(vel_speed)
        if logic.v_forward < 0.0:
            speed_blend = 0.0
        if speed_blend <= 0.0:
            self._cam_vel_x = heading_x
            self._cam_vel_y = heading_y
        else:
            raw_x, raw_y = self._normalize_or_fallback(
                logic.vx, logic.vy, self._cam_vel_x, self._cam_vel_y
            )
            vel_lerp = self._clamp(float(TUNING.DRIVE.cam_vel_dir_lerp), 0.0, 1.0)
            self._cam_vel_x += (raw_x - self._cam_vel_x) * vel_lerp
            self._cam_vel_y += (raw_y - self._cam_vel_y) * vel_lerp
            self._cam_vel_x, self._cam_vel_y = self._normalize_or_fallback(
                self._cam_vel_x, self._cam_vel_y, heading_x, heading_y
            )

        target_x = heading_x * (1.0 - speed_blend) + self._cam_vel_x * speed_blend
        target_y = heading_y * (1.0 - speed_blend) + self._cam_vel_y * speed_blend
        target_x, target_y = self._normalize_or_fallback(target_x, target_y, heading_x, heading_y)

        target_angle = math.atan2(target_y, target_x)
        dt = float(TUNING.CORE.dt)
        target_angle = self._cap_low_speed_target_angle(target_angle, speed_blend, dt)
        self._step_camera_spring(target_angle, dt)
        self._cam_fwd_x = math.cos(self._cam_angle)
        self._cam_fwd_y = math.sin(self._cam_angle)
        return (self._cam_fwd_x, self._cam_fwd_y)

    def angle(self) -> float:
        return self._cam_angle

    def _speed_blend(self, speed: float) -> float:
        min_speed = float(TUNING.DRIVE.cam_vel_min_speed)
        full_speed = float(TUNING.DRIVE.cam_vel_full_speed)
        return self._speed_blend_range(speed, min_speed, full_speed)

    def _speed_blend_range(self, speed: float, min_speed: float, full_speed: float) -> float:
        if speed <= min_speed:
            return 0.0
        denom = full_speed - min_speed
        if denom <= 0.0:
            return 1.0
        t = self._clamp((speed - min_speed) / denom, 0.0, 1.0)
        return t * t * (3.0 - 2.0 * t)

    def _step_camera_spring(self, target_angle: float, dt: float) -> None:
        if dt <= 0.0:
            self._cam_angle = target_angle
            self._cam_ang_vel = 0.0
            return

        freq_hz = float(TUNING.DRIVE.cam_spring_freq_hz)
        damping = float(TUNING.DRIVE.cam_spring_damping)
        if freq_hz <= 0.0:
            self._cam_angle = target_angle
            self._cam_ang_vel = 0.0
            return
        if damping < 0.0:
            damping = 0.0

        omega = 2.0 * math.pi * freq_hz
        delta = self._wrap_angle(target_angle - self._cam_angle)
        accel = (omega * omega) * delta - (2.0 * damping * omega) * self._cam_ang_vel
        self._cam_ang_vel += accel * dt
        self._cam_angle = self._wrap_angle(self._cam_angle + self._cam_ang_vel * dt)

    def _cap_low_speed_target_angle(
        self,
        target_angle: float,
        speed_blend: float,
        dt: float
    ) -> float:
        if dt <= 0.0:
            return target_angle
        cap_blend_max = float(TUNING.DRIVE.cam_low_speed_cap_blend_max)
        if cap_blend_max <= 0.0:
            return target_angle
        if speed_blend >= cap_blend_max:
            return target_angle

        t = self._clamp(speed_blend / cap_blend_max, 0.0, 1.0)
        min_rate = float(TUNING.DRIVE.cam_low_speed_yaw_rate_min_deg)
        max_rate = float(TUNING.DRIVE.cam_low_speed_yaw_rate_max_deg)
        max_rate_deg = min_rate + (max_rate - min_rate) * t
        max_step = math.radians(max_rate_deg) * dt
        delta = self._wrap_angle(target_angle - self._cam_angle)
        if delta > max_step:
            return self._wrap_angle(self._cam_angle + max_step)
        if delta < -max_step:
            return self._wrap_angle(self._cam_angle - max_step)
        return target_angle

    @staticmethod
    def _normalize_or_fallback(
        x: float,
        y: float,
        fallback_x: float,
        fallback_y: float
    ) -> tuple[float, float]:
        l2 = x * x + y * y
        if l2 > 0.000001:
            inv = 1.0 / (l2 ** 0.5)
            return (x * inv, y * inv)
        return (fallback_x, fallback_y)

    @staticmethod
    def _clamp(value: float, min_value: float, max_value: float) -> float:
        if value < min_value:
            return min_value
        if value > max_value:
            return max_value
        return value

    @staticmethod
    def _wrap_angle(angle: float) -> float:
        pi = math.pi
        two_pi = 2.0 * pi
        while angle > pi:
            angle -= two_pi
        while angle < -pi:
            angle += two_pi
        return angle
