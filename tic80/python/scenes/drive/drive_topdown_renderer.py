import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import ttri

    from ...core.palette import Color
    from ...data.tuning import TUNING
    from ...systems.drive.drive_fx import TopdownProjector
    from ...systems.drive.drive_logic_core import DriveLogic
    from ...systems.drive.drive_objects import DriveObjects, DriveZone
    from ...systems.drive.road_model import RoadModel
    from .topdown_debug_draw import TopdownDebugDraw
    from .topdown_fx_overlay import TopdownFxOverlay
    from .topdown_obstacles_draw import TopdownObstaclesDraw
    from .topdown_road_draw import TopdownRoadDraw
    from .topdown_skid_marks import TopdownSkidMarks


class DriveTopdownRenderer:
    """Рендер DRIVE в варианте A (top-down).

    Задача класса: только рисовать. Никаких изменений состояния RunState/DriveLogic.
    """

    _CAR_SPRITE_BASE_ID = 320
    _CAR_SPRITE_PIXEL_SIZE = 32.0
    _CAR_CHROMAKEY = 12
    # Low-speed anti-jerk yaw cap (cam-v3.1):
    # - _LOW_SPEED_CAP_BLEND_MAX: до какого speed_blend действует ограничение (0..1).
    # - _LOW_SPEED_YAW_RATE_MIN_DEG: минимальная скорость поворота цели камеры при почти нулевой скорости.
    # - _LOW_SPEED_YAW_RATE_MAX_DEG: ограничение near-перехода к средней скорости.
    _LOW_SPEED_CAP_BLEND_MAX = 0.45
    _LOW_SPEED_YAW_RATE_MIN_DEG = 260.0
    _LOW_SPEED_YAW_RATE_MAX_DEG = 720.0
    # PRESET A (закомментированный): сильнее режет резкий поворот цели на very-low-speed.
    # _LOW_SPEED_CAP_BLEND_MAX = 0.60
    # _LOW_SPEED_YAW_RATE_MIN_DEG = 220.0
    # _LOW_SPEED_YAW_RATE_MAX_DEG = 720.0
    # PRESET B (закомментированный): более отзывчивый выход, меньше "ватности",
    # но рывки на very-low-speed могут быть чуть заметнее.
    # _LOW_SPEED_CAP_BLEND_MAX = 0.35
    # _LOW_SPEED_YAW_RATE_MIN_DEG = 300.0
    # _LOW_SPEED_YAW_RATE_MAX_DEG = 900.0

    def __init__(self) -> None:
        self._road_draw = TopdownRoadDraw()
        self._obstacles_draw = TopdownObstaclesDraw()
        self._skid_marks = TopdownSkidMarks()
        self._debug_draw = TopdownDebugDraw()
        self._fx_overlay = TopdownFxOverlay()
        self._cam_fwd_x = 1.0
        self._cam_fwd_y = 0.0
        self._cam_inited = False
        self._cam_angle = 0.0
        self._cam_ang_vel = 0.0
        self._cam_vel_x = 1.0
        self._cam_vel_y = 0.0
        self._cam_frame_offset_y = 0.0

    def notify_obstacle_hit(
        self,
        contact_wx: float,
        contact_wy: float,
        normal_x: float,
        normal_y: float,
        impact: float,
        damage: float,
        hitbox_radius: float
    ) -> None:
        self._fx_overlay.notify_obstacle_hit(
            contact_wx,
            contact_wy,
            normal_x,
            normal_y,
            impact,
            damage,
            hitbox_radius
        )

    def draw(
        self,
        road: RoadModel,
        logic: DriveLogic,
        objects: DriveObjects,
        active_zone: DriveZone | None
    ) -> None:
        center_x = 120

        p_s = logic.road_s
        car_x = logic.x
        car_y = logic.y
        cam_fwd_x, cam_fwd_y = self._camera_forward(logic)
        center_y = self._camera_center_y(logic)
        proj = TopdownProjector(car_x, car_y, cam_fwd_x, cam_fwd_y, center_x, center_y)

        start_idx, end_idx = self._road_draw.visible_index_range(road, p_s)
        zones = objects.zones_items_view()
        self._road_draw.draw_road_edges_and_zones(
            road,
            zones,
            start_idx,
            end_idx,
            proj
        )

        if TUNING.DRIVE.debug_zones_enabled:
            i = 0
            while i < len(zones):
                z = zones[i]
                color = Color.GREEN
                if active_zone is not None and z is active_zone:
                    color = Color.WHITE
                self._road_draw.draw_zone_outline(
                    road,
                    z,
                    start_idx,
                    end_idx,
                    proj,
                    color
                )
                i += 1

        obstacles = objects.obstacles_items_view()
        self._obstacles_draw.draw(
            obstacles,
            road,
            p_s,
            proj
        )

        # FX/следы лучше рисовать ДО машины, чтобы кузов перекрывал их.
        start_move = self._fx_overlay.update(road, logic, center_x, center_y, proj)
        if start_move:
            self._skid_marks.trigger_start(float(TUNING.DRIVE.start_skid_seconds))
        self._skid_marks.update_and_draw(logic, center_x, center_y)

        # Следы шин должны быть ПОД пылью/дымом.
        self._fx_overlay.draw_world()

        # Стартовый дым/пыль рисуем ВЫШЕ skid marks, но НИЖЕ кузова.
        self._fx_overlay.draw_under_car()
        self._draw_car_ttri_heading(logic, center_x, center_y, cam_fwd_x, cam_fwd_y)
        self._fx_overlay.draw_over_car()

        if TUNING.DRIVE.debug_vectors_enabled:
            self._debug_draw.draw_vectors(logic, center_x, center_y)
        if TUNING.DRIVE.debug_hitboxes_enabled:
            self._debug_draw.draw_hitboxes(logic.steer_input, center_x, center_y)

    def _camera_forward(self, logic: DriveLogic) -> tuple[float, float]:
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

    def _speed_blend(self, speed: float) -> float:
        min_speed = float(TUNING.DRIVE.cam_vel_min_speed)
        full_speed = float(TUNING.DRIVE.cam_vel_full_speed)
        return self._speed_blend_range(speed, min_speed, full_speed)

    def _frame_blend(self, speed: float) -> float:
        min_speed = float(TUNING.DRIVE.cam_frame_min_speed)
        full_speed = float(TUNING.DRIVE.cam_frame_full_speed)
        return self._speed_blend_range(speed, min_speed, full_speed)

    def _speed_blend_range(self, speed: float, min_speed: float, full_speed: float) -> float:
        if speed <= min_speed:
            return 0.0
        denom = full_speed - min_speed
        if denom <= 0.0:
            return 1.0
        t = self._clamp((speed - min_speed) / denom, 0.0, 1.0)
        return t * t * (3.0 - 2.0 * t)

    def _camera_center_y(self, logic: DriveLogic) -> int:
        speed = (logic.vx * logic.vx + logic.vy * logic.vy) ** 0.5
        frame_t = self._frame_blend(speed)
        max_shift = float(TUNING.DRIVE.cam_frame_max_px)
        if max_shift < 0.0:
            max_shift = 0.0
        target_shift = max_shift * frame_t
        frame_lerp = self._clamp(float(TUNING.DRIVE.cam_frame_lerp), 0.0, 1.0)
        self._cam_frame_offset_y += (target_shift - self._cam_frame_offset_y) * frame_lerp
        base_y = float(TUNING.DRIVE.view_center_y)
        center_y = int(base_y + self._cam_frame_offset_y)
        return self._road_draw.clamp_center_y(center_y)

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
        cap_blend_max = self._LOW_SPEED_CAP_BLEND_MAX
        if cap_blend_max <= 0.0:
            return target_angle
        if speed_blend >= cap_blend_max:
            return target_angle

        t = self._clamp(speed_blend / cap_blend_max, 0.0, 1.0)
        max_rate_deg = self._LOW_SPEED_YAW_RATE_MIN_DEG + (
            self._LOW_SPEED_YAW_RATE_MAX_DEG - self._LOW_SPEED_YAW_RATE_MIN_DEG
        ) * t
        max_step = math.radians(max_rate_deg) * dt
        delta = self._wrap_angle(target_angle - self._cam_angle)
        if delta > max_step:
            return self._wrap_angle(self._cam_angle + max_step)
        if delta < -max_step:
            return self._wrap_angle(self._cam_angle - max_step)
        return target_angle

    def _draw_car_ttri_heading(
        self,
        logic: DriveLogic,
        center_x: int,
        center_y: int,
        cam_fwd_x: float,
        cam_fwd_y: float
    ) -> None:
        ax = float(TUNING.DRIVE.car_sprite_anchor_x)
        ay = float(TUNING.DRIVE.car_sprite_anchor_y)
        size = self._CAR_SPRITE_PIXEL_SIZE

        x0 = float(center_x) - ax
        y0 = float(center_y) - ay
        x1 = x0 + size
        y1 = y0 + size

        heading_angle = self._car_heading_screen_angle(logic.fwd_x,
                                                       logic.fwd_y, cam_fwd_x, cam_fwd_y)
        cos_t = math.cos(heading_angle)
        sin_t = math.sin(heading_angle)
        px = float(center_x)
        py = float(center_y)

        rx0, ry0 = self._rotated_point(x0, y0, px, py, cos_t, sin_t)
        rx1, ry1 = self._rotated_point(x1, y0, px, py, cos_t, sin_t)
        rx2, ry2 = self._rotated_point(x1, y1, px, py, cos_t, sin_t)
        rx3, ry3 = self._rotated_point(x0, y1, px, py, cos_t, sin_t)

        u0 = float((self._CAR_SPRITE_BASE_ID % 16) * 8)
        v0 = float((self._CAR_SPRITE_BASE_ID // 16) * 8)
        u1 = u0 + size
        v1 = v0 + size

        ttri(
            rx0, ry0,
            rx1, ry1,
            rx2, ry2,
            u0, v0,
            u1, v0,
            u1, v1,
            0,
            self._CAR_CHROMAKEY
        )
        ttri(
            rx0, ry0,
            rx2, ry2,
            rx3, ry3,
            u0, v0,
            u1, v1,
            u0, v1,
            0,
            self._CAR_CHROMAKEY
        )

    @staticmethod
    def _car_heading_screen_angle(
        car_fwd_x: float,
        car_fwd_y: float,
        cam_fwd_x: float,
        cam_fwd_y: float
    ) -> float:
        cam_right_x = -cam_fwd_y
        cam_right_y = cam_fwd_x
        local_fwd = car_fwd_x * cam_fwd_x + car_fwd_y * cam_fwd_y
        local_right = car_fwd_x * cam_right_x + car_fwd_y * cam_right_y
        return math.atan2(local_right, local_fwd)

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
    def _rotated_point(
        x: float,
        y: float,
        px: float,
        py: float,
        cos_t: float,
        sin_t: float
    ) -> tuple[float, float]:
        dx = x - px
        dy = y - py
        rx = dx * cos_t - dy * sin_t
        ry = dx * sin_t + dy * cos_t
        return (px + rx, py + ry)

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
