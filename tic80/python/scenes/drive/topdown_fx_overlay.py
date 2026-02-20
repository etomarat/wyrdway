from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...data.tuning import TUNING
    from ...systems.drive.drive_fx import DriveFx, TopdownProjector
    from ...systems.drive.drive_logic_core import DriveLogic
    from ...systems.drive.fx_particles import Particles2D
    from ...systems.drive.road_model import RoadModel
    from ...systems.drive.rng import lcg_next_u31
    from ...systems.fx.vendor.vand_particles import VandParticles
    from .car_pose2d import CarPose2D
    from .topdown_fx_overlay_runtime import (
        topdown_fx_flush_hit_events,
        topdown_fx_maybe_start_move,
        topdown_fx_update_offroad_side_sign,
        topdown_fx_update_transition_cooldown,
        topdown_fx_update_world_particles
    )
    from .topdown_fx_overlay_emit import (
        topdown_fx_edge_spark_burst,
        topdown_fx_edge_spark_dir,
        topdown_fx_emit_exhaust_smoke_vand,
        topdown_fx_emit_offroad_smoke_vand,
        topdown_fx_emit_offroad_transition_sparks,
        topdown_fx_maybe_emit_exhaust_smoke,
        topdown_fx_maybe_emit_offroad_dust,
        topdown_fx_maybe_emit_transition_sparks
    )


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

    def _update_world_particles(self, dt: float, world_dx: float, world_dy: float) -> None:
        topdown_fx_update_world_particles(self, dt, world_dx, world_dy)

    def _update_transition_cooldown(self, dt: float) -> None:
        topdown_fx_update_transition_cooldown(self, dt)

    def _maybe_start_move(self, logic: DriveLogic, pose: CarPose2D) -> bool:
        return topdown_fx_maybe_start_move(self, logic, pose)

    def _update_offroad_side_sign(self, logic: DriveLogic) -> None:
        topdown_fx_update_offroad_side_sign(self, logic)

    def _maybe_emit_transition_sparks(
        self,
        road: RoadModel,
        logic: DriveLogic,
        proj: TopdownProjector,
        pose: CarPose2D
    ) -> None:
        topdown_fx_maybe_emit_transition_sparks(self, road, logic, proj, pose)

    def _maybe_emit_offroad_dust(self, logic: DriveLogic, dt: float, pose: CarPose2D) -> None:
        topdown_fx_maybe_emit_offroad_dust(self, logic, dt, pose)

    def _maybe_emit_exhaust_smoke(self, logic: DriveLogic, dt: float, pose: CarPose2D) -> None:
        topdown_fx_maybe_emit_exhaust_smoke(self, logic, dt, pose)

    def draw_world(self) -> None:
        self._offroad_smoke.draw()
        self._exhaust_smoke.draw()
        self._fx_transition.draw()

    def draw_under_car(self) -> None:
        self._drive_fx.draw(0)

    def draw_over_car(self) -> None:
        self._drive_fx.draw(1)

    def _flush_hit_events(self, proj: TopdownProjector) -> None:
        topdown_fx_flush_hit_events(self, proj)

    def _next_fx_seed(self) -> int:
        self._fx_seed = lcg_next_u31(self._fx_seed)
        return self._fx_seed

    def _emit_offroad_smoke_vand(
        self,
        count_accum: float,
        pose: CarPose2D
    ) -> None:
        topdown_fx_emit_offroad_smoke_vand(self, count_accum, pose)

    def _emit_exhaust_smoke_vand(
        self,
        count_accum: float,
        strength: float,
        pose: CarPose2D
    ) -> None:
        topdown_fx_emit_exhaust_smoke_vand(self, count_accum, strength, pose)

    def _emit_offroad_transition_sparks(
        self,
        entering_offroad: bool,
        road: RoadModel,
        logic: DriveLogic,
        proj: TopdownProjector,
        pose: CarPose2D
    ) -> None:
        topdown_fx_emit_offroad_transition_sparks(self, entering_offroad, road, logic, proj, pose)

    def _edge_spark_dir(
        self,
        road: RoadModel,
        logic: DriveLogic,
        proj: TopdownProjector,
        dir_sign: int,
        entering_offroad: bool
    ) -> tuple[float, float, float]:
        return topdown_fx_edge_spark_dir(self, road, logic, proj, dir_sign, entering_offroad)

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
        topdown_fx_edge_spark_burst(
            self,
            base_x,
            base_y,
            dir_x,
            dir_y,
            cross,
            speed,
            count,
            life,
            entering_offroad,
            scale,
            strength
        )
