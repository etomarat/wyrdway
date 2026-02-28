from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...core.palette import Color
    from ...data.tuning import TUNING
    from ...systems.drive.drive_fx import DriveFx, TopdownProjector
    from ...systems.drive.drive_logic_core import DriveLogic
    from ...systems.drive.fx_particles import Particles2D
    from ...systems.drive.rng import lcg_next_u31
    from ...systems.drive.road_model import RoadModel
    from ...systems.fx.vendor.vand_particles import VandParticles
    from .car_pose2d import CarPose2D


class TopdownFxOverlay:
    def __init__(self) -> None:
        # Вспышки искр при переходе “дорога <-> оффроад” должны читаться поверх пыли.
        self._fx_transition = Particles2D(40)
        self._drive_fx = DriveFx(TUNING)
        self._offroad_smoke = VandParticles(1337)
        self._exhaust_smoke = VandParticles(2469)

        self._prev_speed = 0.0
        self._prev_offroad = False

        self._offroad_side_sign = 1
        self._offroad_transition_cooldown = 0.0
        self._fx_spawn_accum_off_smoke = 0.0
        self._fx_spawn_accum_exhaust = 0.0
        self._fx_seed = 1
        self._hit_events: list[tuple[float, float, float, float, float, float]] = []
        self._exhaust_strength = 0.0

    def notify_obstacle_hit(
        self,
        contact_wx: float,
        contact_wy: float,
        normal_x: float,
        normal_y: float,
        impact: float,
        hitbox_radius: float
    ) -> None:
        # Ударные эффекты обрабатываем в draw(), когда у нас есть актуальная проекция world->screen.
        self._hit_events.append((contact_wx, contact_wy, normal_x, normal_y, impact, hitbox_radius))

    def update(
        self,
        road: RoadModel,
        logic: DriveLogic,
        proj: TopdownProjector,
        pose: CarPose2D
    ) -> bool:
        dt = TUNING.CORE.dt
        self._exhaust_strength = 0.0

        world_dx, world_dy = proj.world_vec_to_screen(-logic.vx * dt, -logic.vy * dt)
        self._update_world_particles(dt, world_dx, world_dy)
        self._update_transition_cooldown(dt)
        self._flush_hit_events(proj)
        start_move = self._maybe_start_move(logic, pose)
        self._update_offroad_side_sign(logic)
        self._maybe_emit_transition_sparks(road, logic, proj, pose)
        self._maybe_emit_offroad_dust(logic, dt, pose)
        self._maybe_emit_exhaust_smoke(logic, dt, pose)
        return start_move

    def exhaust_strength(self) -> float:
        """Текущая сила выхлопа (0..1), вычисленная в этом кадре."""
        return self._exhaust_strength

    def draw_world(self) -> None:
        self._offroad_smoke.draw()
        self._exhaust_smoke.draw()
        self._fx_transition.draw()

    def draw_under_car(self) -> None:
        self._drive_fx.draw(0)

    def draw_over_car(self) -> None:
        self._drive_fx.draw(1)

    def _next_fx_seed(self) -> int:
        self._fx_seed = lcg_next_u31(self._fx_seed)
        return self._fx_seed

    def _update_world_particles(self, dt: float, world_dx: float, world_dy: float) -> None:
        """Обновляет все системы частиц и сдвигает world-эффекты камерой.

        Искры перехода дорога/оффроуд намеренно не двигаются world-shift-ом, чтобы
        оставаться локальным эффектом у колёс и не «плыть» вбок.
        """
        self._fx_transition.update(dt, 0.0, 0.0)
        self._drive_fx.update(dt, world_dx, world_dy)
        self._offroad_smoke.update(dt, world_dx, world_dy)
        self._exhaust_smoke.update(dt, world_dx, world_dy)

    def _update_transition_cooldown(self, dt: float) -> None:
        """Тикает кулдаун искр перехода между покрытиями."""
        if self._offroad_transition_cooldown <= 0.0:
            return
        self._offroad_transition_cooldown -= dt
        if self._offroad_transition_cooldown < 0.0:
            self._offroad_transition_cooldown = 0.0

    def _maybe_start_move(self, logic: DriveLogic, pose: CarPose2D) -> bool:
        """Запускает стартовый дым/букс при переходе из «стоим» в «поехали».

        На оффроуде стартовый буст-эффект не запускается: там читается только
        постоянная пыль.
        """
        spd = logic.speed
        start_move = False
        min_speed = float(TUNING.DRIVE.fx_start_move_min_speed)
        if self._prev_speed <= min_speed and spd > min_speed:
            if not logic.offroad:
                start_move = True
                fx_cx, fx_cy = pose.screen_center()
                self._drive_fx.start_move(int(fx_cx), int(fx_cy), self._next_fx_seed())
        self._prev_speed = spd
        return start_move

    def _update_offroad_side_sign(self, logic: DriveLogic) -> None:
        """Обновляет знак стороны оффроуда относительно центра дороги."""
        if not logic.offroad:
            return
        rd = logic.road_d
        if rd > 0.0:
            self._offroad_side_sign = 1
        elif rd < 0.0:
            self._offroad_side_sign = -1

    def _flush_hit_events(self, proj: TopdownProjector) -> None:
        """Сбрасывает очередь попаданий препятствий в `DriveFx` текущего кадра."""
        if len(self._hit_events) <= 0:
            return
        i = 0
        while i < len(self._hit_events):
            wx, wy, nx, ny, impact, hit_r = self._hit_events[i]
            seed = self._next_fx_seed()
            self._drive_fx.obstacle_hit(wx, wy, nx, ny, impact, seed, hit_r, proj)
            i += 1
        self._hit_events = []

    def _maybe_emit_transition_sparks(
        self,
        road: RoadModel,
        logic: DriveLogic,
        proj: TopdownProjector,
        pose: CarPose2D
    ) -> None:
        """Эмитит искры только в кадр смены покрытия дорога/оффроуд."""
        if logic.offroad == self._prev_offroad:
            return
        d = TUNING.DRIVE
        spd = logic.speed
        if spd > d.fx_dust_min_speed and self._offroad_transition_cooldown <= 0.0:
            self._emit_offroad_transition_sparks(logic.offroad, road, logic, proj, pose)
            self._offroad_transition_cooldown = float(TUNING.DRIVE.fx_transition_cooldown_seconds)
        self._prev_offroad = logic.offroad

    def _maybe_emit_offroad_dust(self, logic: DriveLogic, dt: float, pose: CarPose2D) -> None:
        """Эмитит постоянную оффроуд-пыль из-под колёс."""
        d = TUNING.DRIVE
        if not logic.offroad or logic.speed <= d.fx_dust_min_speed:
            return
        self._fx_spawn_accum_off_smoke += (d.fx_dust_rate_offroad * 0.65) * dt
        self._emit_offroad_smoke_vand(self._fx_spawn_accum_off_smoke, pose)
        self._fx_spawn_accum_off_smoke -= int(self._fx_spawn_accum_off_smoke)

    def _maybe_emit_exhaust_smoke(self, logic: DriveLogic, dt: float, pose: CarPose2D) -> None:
        """Эмитит выхлоп в зависимости от доли текущей скорости от max_speed."""
        d = TUNING.DRIVE
        if d.max_speed <= 0.0 or d.fx_exhaust_rate <= 0.0:
            return
        speed_factor = logic.speed / d.max_speed
        over = speed_factor - d.fx_exhaust_min_speed_factor
        ramp = float(d.fx_exhaust_ramp_speed_factor)
        if ramp < 0.01:
            ramp = 0.01
        strength = over / ramp
        if strength < 0.0:
            strength = 0.0
        if strength > 1.0:
            strength = 1.0
        strength = strength * strength
        if strength <= 0.0:
            return
        self._exhaust_strength = strength
        rate = d.fx_exhaust_rate * strength
        self._fx_spawn_accum_exhaust += rate * dt
        self._emit_exhaust_smoke_vand(self._fx_spawn_accum_exhaust, strength, pose)
        self._fx_spawn_accum_exhaust -= int(self._fx_spawn_accum_exhaust)

    def _emit_offroad_smoke_vand(
        self,
        count_accum: float,
        pose: CarPose2D
    ) -> None:
        """Спавнит жёлто-оранжевые пуфы пыли `VandParticles` у задних колёс."""
        n = int(count_accum)
        if n <= 0:
            return

        d = TUNING.DRIVE
        wheel_dx, back = pose.local_from_center_reference(
            float(d.fx_dust_wheel_dx_px),
            float(d.fx_dust_back_px)
        )
        jitter_x = float(d.fx_dust_jitter_x_px)
        jitter_y = float(d.fx_dust_jitter_y_px)
        c0 = int(d.fx_offroad_dust_color_a)
        c1 = int(d.fx_offroad_dust_color_b)

        i = 0
        while i < n:
            r0 = self._next_fx_seed()
            r1 = self._next_fx_seed()

            jx = ((r1 % 1000) / 1000.0 - 0.5) * jitter_x
            jy = ((r0 % 1000) / 1000.0) * jitter_y

            x_l, y_l = pose.local_to_screen(-wheel_dx + jx, back + jy)
            x_r, y_r = pose.local_to_screen(wheel_dx - jx, back + jy)

            t = (r0 % 1000) / 1000.0
            r = 1.0 + t * 2.0
            c = c0
            if (r1 % 1000) >= 500:
                c = c1

            self._offroad_smoke.spawn_dust_down_color(float(x_l), float(y_l), float(r), int(c))
            self._offroad_smoke.spawn_dust_down_color(float(x_r), float(y_r), float(r), int(c))

            r2 = 0.75 + ((r1 % 1000) / 1000.0) * 1.75
            c2 = c1 if c == c0 else c0
            side = 2.0 + ((r1 % 1000) / 1000.0) * 4.0
            x_l2, y_l2 = pose.local_to_screen(-wheel_dx + jx - side, back + jy)
            x_r2, y_r2 = pose.local_to_screen(wheel_dx - jx + side, back + jy)
            self._offroad_smoke.spawn_dust_down_color(float(x_l2), float(y_l2), float(r2), int(c2))
            self._offroad_smoke.spawn_dust_down_color(float(x_r2), float(y_r2), float(r2), int(c2))
            i += 1

    def _emit_exhaust_smoke_vand(
        self,
        count_accum: float,
        strength: float,
        pose: CarPose2D
    ) -> None:
        """Спавнит многослойный выхлоп `VandParticles` (струйка + хвост-клубы)."""
        n = int(count_accum)
        if n <= 0:
            return

        d = TUNING.DRIVE
        s = float(strength)
        if s < 0.0:
            s = 0.0
        if s > 1.0:
            s = 1.0

        base_x, base_back = pose.local_from_center_reference(
            float(d.fx_exhaust_dx_px),
            float(d.fx_exhaust_dy_px)
        )
        r0 = float(d.fx_exhaust_r_min)
        r1 = float(d.fx_exhaust_r_max)
        if r1 < r0:
            t = r0
            r0 = r1
            r1 = t
        c0 = int(d.fx_exhaust_color_a)
        c1 = int(d.fx_exhaust_color_b)

        i = 0
        while i < n:
            r = self._next_fx_seed()
            t = (r % 1000) / 1000.0
            u = ((r // 1000) % 1000) / 1000.0

            s_jx = (t - 0.5) * 0.8
            s_jy = (u - 0.5) * 0.35
            sr = r0 * (0.70 + t * 0.40) * (0.85 + 0.35 * s)
            if sr < 1.2:
                sr = 1.2
            x1, y1 = pose.local_to_screen(base_x + s_jx, base_back + s_jy)
            x2, y2 = pose.local_to_screen(base_x - s_jx * 0.55, base_back + s_jy * 0.55)
            self._exhaust_smoke.spawn_dust_down_two_tone_life(x1, y1, sr, c0, c1, 18)
            self._exhaust_smoke.spawn_dust_down_two_tone_life(x2, y2, sr * 0.85, c0, c1, 16)

            m_back = base_back + 3.0 + u * 4.0
            mr = (r0 + (r1 - r0) * (0.25 + t * 0.20)) * (0.80 + 0.55 * s)
            if mr < sr:
                mr = sr
            mid_life = 14 + int(s * 8.0)
            x3, y3 = pose.local_to_screen(base_x + (u - 0.5) * 1.6, m_back)
            x4, y4 = pose.local_to_screen(base_x - (u - 0.5) * 1.2, m_back + 1.2)
            self._exhaust_smoke.spawn_dust_down_two_tone_life(x3, y3, mr, c0, c1, mid_life)
            self._exhaust_smoke.spawn_dust_down_two_tone_life(x4, y4, mr * 0.95, c0, c1, mid_life - 2)

            tail_back = base_back + 5.0 + u * 6.0
            tail_r = r1 * (0.85 + t * 0.35) * (0.70 + 0.70 * s)
            if tail_r < mr:
                tail_r = mr
            tail_life = 18 + int(s * 10.0)
            x5, y5 = pose.local_to_screen(base_x + (t - 0.5) * 2.8, tail_back)
            x6, y6 = pose.local_to_screen(base_x + (u - 0.5) * 2.2 + 1.2, tail_back + 1.6)
            x7, y7 = pose.local_to_screen(base_x - (u - 0.5) * 2.0 - 1.0, tail_back + 2.6)
            x8, y8 = pose.local_to_screen(base_x + (t - 0.5) * 2.0 - 1.4, tail_back + 3.6)
            self._exhaust_smoke.spawn_dust_down_two_tone_life(x5, y5, tail_r, c0, c1, tail_life)
            self._exhaust_smoke.spawn_dust_down_two_tone_life(x6, y6, tail_r * 0.92, c0, c1, tail_life - 2)
            self._exhaust_smoke.spawn_dust_down_two_tone_life(x7, y7, tail_r * 0.88, c0, c1, tail_life - 4)
            self._exhaust_smoke.spawn_dust_down_two_tone_life(x8, y8, tail_r * 0.84, c0, c1, tail_life - 6)
            i += 1

    def _emit_offroad_transition_sparks(
        self,
        entering_offroad: bool,
        road: RoadModel,
        logic: DriveLogic,
        proj: TopdownProjector,
        pose: CarPose2D
    ) -> None:
        """Эмитит краткий burst искр по краю трассы при пересечении границы."""
        d = TUNING.DRIVE

        boundary_sign = self._offroad_side_sign
        spawn_sign = -boundary_sign
        dir_sign = -boundary_sign
        if not entering_offroad:
            spawn_sign = boundary_sign
            dir_sign = boundary_sign

        dir_x, dir_y, cross = self._edge_spark_dir(road, logic, proj, dir_sign, entering_offroad)

        spd = logic.speed
        min_spd = float(d.fx_transition_sparks_min_speed)
        ramp = float(d.fx_transition_sparks_ramp_speed)
        if ramp < 0.01:
            ramp = 0.01
        strength = (spd - min_spd) / ramp
        if strength <= 0.0:
            return
        if strength > 1.0:
            strength = 1.0

        n_base = 4 + int(spd * 0.04)
        n = int(n_base * strength)
        if not entering_offroad:
            n = int(n * 1.7)
        if n < 1:
            return
        if n > 20:
            n = 20

        speed = 55.0 + spd * 1.1
        if speed > 180.0:
            speed = 180.0
        speed *= 0.65 + 0.35 * strength

        life = 12 + int(spd * 0.012)
        if not entering_offroad:
            life += 3
        life = int(life * (0.60 + 0.60 * strength))
        if life < 7:
            life = 7
        if life > 26:
            life = 26

        wheel_dx, back = pose.local_from_center_reference(
            float(d.fx_transition_sparks_wheel_dx_px),
            float(d.fx_transition_sparks_back_px)
        )
        wheelbase = float(d.fx_transition_sparks_wheelbase_px)

        rear_x, rear_y = pose.local_to_screen(float(spawn_sign) * wheel_dx, back)
        front_x, front_y = pose.local_to_screen(
            float(spawn_sign) * (wheel_dx * 0.72),
            back - wheelbase + 3.0
        )

        n_front = int(n * 0.6)
        if n_front < 3:
            n_front = 3
        if n_front > n:
            n_front = n

        self._edge_spark_burst(
            rear_x,
            rear_y,
            dir_x,
            dir_y,
            cross,
            speed,
            n,
            life,
            entering_offroad,
            1.0,
            strength
        )
        self._edge_spark_burst(
            front_x,
            front_y,
            dir_x,
            dir_y,
            cross,
            speed,
            n_front,
            life,
            entering_offroad,
            0.85,
            strength
        )

    def _edge_spark_dir(
        self,
        road: RoadModel,
        logic: DriveLogic,
        proj: TopdownProjector,
        dir_sign: int,
        entering_offroad: bool
    ) -> tuple[float, float, float]:
        """Считает screen-направление burst и коэффициент поперечной компоненты."""
        dx, dy = road.direction_at(logic.road_s)
        rx = -dy
        ry = dx

        fx = logic.fwd_x
        fy = logic.fwd_y
        crx = -fy
        cry = fx

        sx = rx * crx + ry * cry
        sy = -(rx * fx + ry * fy)
        d0 = abs(sx) + abs(sy)
        if d0 < 0.001:
            sx = 1.0
            sy = 0.0
            d0 = 1.0
        sx = (sx / d0) * float(dir_sign)
        sy = (sy / d0) * float(dir_sign)

        mx, my = proj.world_vec_to_screen(logic.vx, logic.vy)
        d1 = abs(mx) + abs(my)
        if d1 < 0.001:
            d1 = 1.0
        mx /= d1
        my /= d1
        cross = abs(mx * sx + my * sy)
        if cross > 1.0:
            cross = 1.0

        wn = 0.45 + 1.10 * cross
        wt = 1.10
        if not entering_offroad:
            wt = 1.35

        dx = sx * wn
        dy = sy * wn + wt
        d2 = abs(dx) + abs(dy)
        if d2 < 0.001:
            d2 = 1.0
        dx /= d2
        dy /= d2
        return dx, dy, cross

    def _edge_spark_burst(
        self,
        base_x: float,
        base_y: float,
        dir_x: float,
        dir_y: float,
        cross: float,
        speed: float,
        count: int,
        life: int,
        entering_offroad: bool,
        scale: float,
        strength: float
    ) -> None:
        """Спавнит burst сегментов-искр в локальном направлении края трассы."""
        px = -dir_y
        py = dir_x

        i = 0
        while i < count:
            r0 = self._next_fx_seed()
            r1 = self._next_fx_seed()

            t = (r0 % 1000) / 1000.0
            u = (r1 % 1000) / 1000.0

            spread = (0.28 + u * 0.26) * (0.75 + 0.70 * cross)
            if not entering_offroad:
                spread += 0.12
            spread *= (0.80 + 0.20 * scale)

            vx = dir_x + px * ((t - 0.5) * 2.0 * spread)
            vy = dir_y + py * ((t - 0.5) * 2.0 * spread)
            den = abs(vx) + abs(vy)
            if den < 0.001:
                den = 1.0
            vx /= den
            vy /= den

            seg = (2.0 + t * 4.0) * scale
            if not entering_offroad:
                seg *= 1.15
            seg *= 0.70 + 0.50 * strength

            pvx = vx * speed * (0.80 + t * 0.40) * scale
            pvy = vy * speed * (0.80 + u * 0.40) * scale

            color = Color.WHITE
            m = int(r0 % 3)
            if m == 1:
                color = Color.YELLOW
            elif m == 2:
                color = Color.ORANGE

            self._fx_transition.spawn(
                base_x + (t - 0.5) * 2.5 * scale,
                base_y + (u - 0.5) * 2.0 * scale,
                vx * seg,
                vy * seg,
                pvx,
                pvy,
                life,
                color
            )
            i += 1
