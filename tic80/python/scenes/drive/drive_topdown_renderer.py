import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import circ, circb, line, print, ttri

    from ...contracts import PursuerVariantTuning
    from ...core.palette import Color
    from ...data.tuning import TUNING
    from ...systems.drive.drive_fx import TopdownProjector
    from ...systems.drive.drive_logic_core import DriveLogic
    from ...systems.drive.drive_objects import DriveObjects, DriveZone
    from ...systems.drive.pursuer_chase import PursuerState, PursuerStateId
    from ...systems.drive.drive_screen_shake import DriveScreenShake
    from ...systems.drive.pursuers.archetypes import PursuerArchetype
    from ...systems.drive.road_model import RoadModel
    from .car_pose2d import CarPose2D
    from .pursuer_body_renderer import PursuerBodyRenderer
    from .pursuer_screen_tracker import PursuerScreenTracker
    from .pursuer_strike_renderer import PursuerStrikeRenderer
    from .pursuer_text_bank import PursuerTextBank
    from .pursuer_text_overlay import PursuerTextOverlay
    from .topdown_debug_draw import TopdownDebugDraw
    from .topdown_fx_overlay import TopdownFxOverlay
    from .topdown_obstacles_draw import TopdownObstaclesDraw
    from .topdown_road_draw import TopdownRoadDraw
    from .topdown_skid_marks import TopdownSkidMarks


class DriveTopdownRenderer:
    """Рендер DRIVE в варианте A (top-down).

    Задача класса: только рисовать. Никаких изменений состояния RunState/DriveLogic.
    """

    _CAR_SPRITE_BASE_ID = 256
    _CAR_CHROMAKEY = 12
    # Crop empty right column (8px) from repacked #256 block.
    _CAR_SRC_X0 = 0.0
    _CAR_SRC_Y0 = 0.0
    _CAR_SRC_X1 = 24.0
    _CAR_SRC_Y1 = 32.0
    # Internal compensation for atlas repack: old 32x32 sprite had 8px empty left column.
    # Not gameplay tuning; keeps existing anchor-aligned geometry unchanged.
    _CAR_SOURCE_REPACK_SHIFT_X = 8.0

    def __init__(self) -> None:
        self._road_draw = TopdownRoadDraw()
        self._obstacles_draw = TopdownObstaclesDraw()
        self._skid_marks = TopdownSkidMarks()
        self._debug_draw = TopdownDebugDraw()
        self._fx_overlay = TopdownFxOverlay()
        self._shake = DriveScreenShake()
        self._pursuer_text_bank = PursuerTextBank()
        self._pursuer_screen_tracker = PursuerScreenTracker()
        self._pursuer_body_renderer = PursuerBodyRenderer(self._pursuer_text_bank)
        self._pursuer_strike_renderer = PursuerStrikeRenderer()
        self._pursuer_text_overlay = PursuerTextOverlay(self._pursuer_text_bank)
        self._cam_fwd_x = 1.0
        self._cam_fwd_y = 0.0
        self._cam_inited = False
        self._cam_angle = 0.0
        self._cam_ang_vel = 0.0
        self._cam_vel_x = 1.0
        self._cam_vel_y = 0.0
        self._pursuer_anim_t = 0.0

    def notify_obstacle_hit(
        self,
        contact_wx: float,
        contact_wy: float,
        normal_x: float,
        normal_y: float,
        impact: float,
        hitbox_radius: float
    ) -> None:
        self._fx_overlay.notify_obstacle_hit(
            contact_wx,
            contact_wy,
            normal_x,
            normal_y,
            impact,
            hitbox_radius
        )
        self._shake.notify_hit(impact, TUNING)

    def notify_pursuer_strike(self, intensity: float, variant_id: str) -> None:
        if intensity <= 0.0:
            return
        self._shake.notify_hit(float(intensity), TUNING)
        self._pursuer_text_overlay.queue_error_text(str(variant_id), self._pursuer_anim_t)

    def notify_pursuer_hp_strike_fx(
        self,
        logic: DriveLogic,
        hp_loss: int,
        strike_shake_intensity: float
    ) -> None:
        if hp_loss <= 0:
            return
        rear_x, rear_y, rear_r, front_x, front_y, front_r = logic.hitbox_world_circles()
        if rear_r <= 0.0 and front_r <= 0.0:
            return

        # Спавним FX в фактической точке удара (задний хитбокс машины).
        fwd_x = float(logic.fwd_x)
        fwd_y = float(logic.fwd_y)
        hit_r = rear_r
        if hit_r <= 0.0:
            hit_r = 4.0

        impact = float(strike_shake_intensity) * 1.8 + float(hp_loss) * 12.0
        if impact < 36.0:
            impact = 36.0
        if impact > 120.0:
            impact = 120.0

        # Разворачиваем нормаль так, чтобы вылет искр читался "внутрь машины".
        nx = -fwd_x
        ny = -fwd_y
        self._fx_overlay.notify_obstacle_hit(
            rear_x,
            rear_y,
            nx,
            ny,
            impact,
            hit_r
        )

    def draw(
        self,
        road: RoadModel,
        logic: DriveLogic,
        objects: DriveObjects,
        active_zone: DriveZone | None,
        pursuer_archetype: PursuerArchetype | None = None,
        pursuer_state: PursuerState | None = None,
        pursuer_s: float = 0.0,
        strike_flash: float = 0.0,
        screen_glitch_active: bool = False
    ) -> None:
        self._shake.ensure_seed(road.seed)
        self._pursuer_anim_t += float(TUNING.CORE.dt)
        self._pursuer_text_overlay.update(float(TUNING.CORE.dt))
        shake_x, shake_y = self._shake.update(
            float(TUNING.CORE.dt),
            logic.offroad,
            self._fx_overlay.exhaust_strength(),
            TUNING
        )

        center_x = 120 + self._round_to_int(shake_x)
        center_y = self._road_draw.clamp_center_y(int(TUNING.DRIVE.view_center_y))
        center_y += self._round_to_int(shake_y)

        p_s = logic.road_s
        car_x = logic.x
        car_y = logic.y
        cam_fwd_x, cam_fwd_y = self._camera_forward(logic)
        proj = TopdownProjector(car_x, car_y, cam_fwd_x, cam_fwd_y, center_x, center_y)
        pose = CarPose2D(logic, proj, center_x, center_y)

        start_idx, end_idx = self._road_draw.visible_index_range(road, p_s)
        zones = objects.zones_items()
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

        obstacles = objects.obstacles_items()
        self._obstacles_draw.draw(
            obstacles,
            road,
            p_s,
            proj
        )

        # FX/следы лучше рисовать ДО машины, чтобы кузов перекрывал их.
        start_move = self._fx_overlay.update(road, logic, proj, pose)
        if start_move:
            self._skid_marks.trigger_start(float(TUNING.DRIVE.start_skid_seconds))
        self._skid_marks.update_and_draw(logic, proj, pose)

        # Следы шин должны быть ПОД пылью/дымом.
        self._fx_overlay.draw_world()

        # Стартовый дым/пыль рисуем ВЫШЕ skid marks, но НИЖЕ кузова.
        self._fx_overlay.draw_under_car()
        self._draw_car_ttri(pose)
        self._fx_overlay.draw_over_car()
        # Преследователь рисуем ПОСЛЕ машины, чтобы он всегда был поверх кузова.
        self._draw_pursuer_world(
            road,
            proj,
            logic,
            pose,
            pursuer_archetype,
            pursuer_state,
            pursuer_s,
            strike_flash,
            screen_glitch_active
        )

        if TUNING.DRIVE.debug_vectors_enabled:
            self._debug_draw.draw_vectors(logic, proj, center_x, center_y)
        if TUNING.DRIVE.debug_hitboxes_enabled:
            self._debug_draw.draw_hitboxes(logic, proj)
            if pursuer_archetype is not None:
                profile = pursuer_archetype.profile
                self._debug_draw.draw_pursuer_strike_range(
                    road,
                    proj,
                    float(logic.road_s),
                    float(profile.strike_begin_dist_s)
                )

    def _draw_pursuer_world(
        self,
        road: RoadModel,
        proj: TopdownProjector,
        logic: DriveLogic,
        pose: CarPose2D,
        pursuer_archetype: PursuerArchetype | None,
        pursuer_state: PursuerState | None,
        pursuer_s: float,
        strike_flash: float,
        screen_glitch_active: bool
    ) -> None:
        if pursuer_state is None or pursuer_state == PursuerStateId.FAR or pursuer_archetype is None:
            self._pursuer_screen_tracker.reset()
            return

        profile = pursuer_archetype.profile
        contact_s = float(pursuer_s)
        if contact_s < 0.0:
            contact_s = 0.0
        if contact_s > road.segment_total_length:
            contact_s = road.segment_total_length
        s = contact_s
        visual_offset = float(profile.contact_offset_s)
        if visual_offset > 0.0:
            s -= visual_offset
        if s < 0.0:
            s = 0.0
        if s > road.segment_total_length:
            s = road.segment_total_length

        draw_s = self._pursuer_screen_tracker.smooth_draw_s(s)
        cx, cy = road.sample_centerline(draw_s)
        dir_x, dir_y = road.direction_at(draw_s)
        right_x = -dir_y
        right_y = dir_x
        half_w = road.width_at(draw_s) * 0.5
        max_follow_d = half_w * 0.92
        target_d = float(logic.road_d)
        if target_d > max_follow_d:
            target_d = max_follow_d
        if target_d < -max_follow_d:
            target_d = -max_follow_d
        draw_d = self._pursuer_screen_tracker.smooth_draw_d(target_d, half_w, pursuer_state)

        t = self._pursuer_anim_t
        wobble = 1.4
        if pursuer_state == PursuerStateId.NEAR:
            wobble = 2.2
        phase = float(road.seed & 1023) * 0.01
        wobble *= (
            0.60 * math.sin(t * 4.5 + phase + self._cam_angle * 1.6)
            + 0.40 * math.sin(t * 2.7 + phase * 1.3)
        )
        lateral_d = draw_d + wobble
        wx = cx + right_x * lateral_d
        wy = cy + right_y * lateral_d
        sx, sy = proj.world_to_screen(wx, wy)
        px, py = self._pursuer_screen_tracker.screen_position(
            sx,
            sy,
            profile,
            pursuer_state,
            float(TUNING.CORE.dt)
        )

        seed_base = (
            road.seed
            ^ int(draw_s * 17.0)
            ^ int(self._pursuer_anim_t * 1000.0)
        ) & 0xFFFFFFFF
        c_sx, c_sy = proj.world_to_screen(cx, cy)
        rx, ry = proj.world_to_screen(
            cx + right_x * half_w,
            cy + right_y * half_w
        )
        road_half_px = ((rx - c_sx) * (rx - c_sx) + (ry - c_sy) * (ry - c_sy)) ** 0.5
        pursuer_archetype.draw_body(
            self,
            px,
            py,
            pursuer_state,
            seed_base,
            road_half_px
        )
        self._pursuer_text_overlay.draw(screen_glitch_active)
        if profile.debug_contact_marker:
            # TEMP: яркая метка в логической контактной точке (до visual contact_offset_s).
            # Нужна для настройки offset относительно тела преследователя.
            ccx, ccy = road.sample_centerline(contact_s)
            cdir_x, cdir_y = road.direction_at(contact_s)
            crx = -cdir_y
            cry = cdir_x
            cwobble = 1.4
            if pursuer_state == PursuerStateId.NEAR:
                cwobble = 2.2
            cwobble *= (
                0.60 * math.sin(t * 4.5 + phase + self._cam_angle * 1.6)
                + 0.40 * math.sin(t * 2.7 + phase * 1.3)
            )
            clateral_d = draw_d + cwobble
            csx, csy = proj.world_to_screen(
                ccx + crx * clateral_d,
                ccy + cry * clateral_d
            )
            circ(int(csx), int(csy), 2, Color.WHITE)
            circb(int(csx), int(csy), 3, Color.RED)

        rear_x, rear_y, _, _, _, _ = logic.hitbox_world_circles()
        hit_sx, hit_sy = proj.world_to_screen(rear_x, rear_y)
        if strike_flash > 0.0:
            flash_dur = float(profile.strike_flash_seconds)
            flash_n = 1.0
            if flash_dur > 0.0001:
                flash_n = strike_flash / flash_dur
            if flash_n < 0.0:
                flash_n = 0.0
            if flash_n > 1.0:
                flash_n = 1.0
            pursuer_archetype.draw_strike(
                self,
                px,
                py,
                int(hit_sx),
                int(hit_sy),
                flash_n,
                seed_base ^ 0x9E3779B9
            )

    def draw_glitch_pursuer_body(
        self,
        px: int,
        py: int,
        pursuer_state: PursuerState,
        seed_base: int,
        road_half_px: float,
        profile: PursuerVariantTuning
    ) -> None:
        self._pursuer_body_renderer.draw_glitch_body(
            px,
            py,
            pursuer_state,
            seed_base,
            road_half_px,
            profile,
            self._pursuer_anim_t,
            self._cam_angle
        )

    def draw_prime_pursuer_body(
        self,
        px: int,
        py: int,
        pursuer_state: PursuerState,
        seed_base: int,
        road_half_px: float,
        profile: PursuerVariantTuning
    ) -> None:
        self._pursuer_body_renderer.draw_prime_body(
            px,
            py,
            pursuer_state,
            seed_base,
            road_half_px,
            profile,
            self._pursuer_anim_t,
            self._cam_angle
        )

    def draw_entity_pursuer_body(
        self,
        px: int,
        py: int,
        pursuer_state: PursuerState,
        seed_base: int,
        profile: PursuerVariantTuning
    ) -> None:
        self._pursuer_body_renderer.draw_entity_body(
            px,
            py,
            pursuer_state,
            seed_base,
            profile,
            self._pursuer_anim_t
        )

    def draw_entity_pursuer_strike(
        self,
        px: int,
        py: int,
        tx: int,
        ty: int,
        flash_n: float,
        seed_base: int
    ) -> None:
        self._pursuer_strike_renderer.draw_entity_strike(
            px,
            py,
            tx,
            ty,
            flash_n,
            seed_base
        )

    def draw_glitch_pursuer_strike(
        self,
        px: int,
        py: int,
        tx: int,
        ty: int,
        flash_n: float,
        seed_base: int
    ) -> None:
        self._pursuer_strike_renderer.draw_glitch_strike(
            px,
            py,
            tx,
            ty,
            flash_n,
            seed_base
        )

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

    def _draw_car_ttri(self, pose: CarPose2D) -> None:
        sx0 = self._CAR_SRC_X0
        sy0 = self._CAR_SRC_Y0
        sx1 = self._CAR_SRC_X1
        sy1 = self._CAR_SRC_Y1
        src_shift_x = self._CAR_SOURCE_REPACK_SHIFT_X
        rx0, ry0 = pose.sprite_px_to_screen(sx0 + src_shift_x, sy0)
        rx1, ry1 = pose.sprite_px_to_screen(sx1 + src_shift_x, sy0)
        rx2, ry2 = pose.sprite_px_to_screen(sx1 + src_shift_x, sy1)
        rx3, ry3 = pose.sprite_px_to_screen(sx0 + src_shift_x, sy1)

        base_u = float((self._CAR_SPRITE_BASE_ID % 16) * 8)
        base_v = float((self._CAR_SPRITE_BASE_ID // 16) * 8)
        u0 = base_u + sx0
        v0 = base_v + sy0
        u1 = base_u + sx1
        v1 = base_v + sy1

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
    def _round_to_int(value: float) -> int:
        if value >= 0.0:
            return int(value + 0.5)
        return int(value - 0.5)

    @staticmethod
    def _wrap_angle(angle: float) -> float:
        pi = math.pi
        two_pi = 2.0 * pi
        while angle > pi:
            angle -= two_pi
        while angle < -pi:
            angle += two_pi
        return angle
