from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...data.tuning import TUNING
    from ...systems.drive.drive_fx import TopdownProjector
    from ...systems.drive.drive_logic_core import DriveLogic
    from .car_pose2d import CarPose2D
    from .topdown_fx_overlay import TopdownFxOverlay


def topdown_fx_update_world_particles(
    overlay: TopdownFxOverlay,
    dt: float,
    world_dx: float,
    world_dy: float
) -> None:
    """Обновляет все системы частиц и сдвигает world-эффекты камерой.

    Искры перехода дорога/оффроуд намеренно не двигаются world-shift-ом, чтобы
    оставаться локальным эффектом у колёс и не «плыть» вбок.
    """
    overlay._fx_transition.update(dt, 0.0, 0.0)
    overlay._drive_fx.update(dt, world_dx, world_dy)
    overlay._offroad_smoke.update(dt, world_dx, world_dy)
    overlay._exhaust_smoke.update(dt, world_dx, world_dy)


def topdown_fx_update_transition_cooldown(overlay: TopdownFxOverlay, dt: float) -> None:
    """Тикает кулдаун искр перехода между покрытиями."""
    if overlay._offroad_transition_cooldown <= 0.0:
        return
    overlay._offroad_transition_cooldown -= dt
    if overlay._offroad_transition_cooldown < 0.0:
        overlay._offroad_transition_cooldown = 0.0


def topdown_fx_maybe_start_move(
    overlay: TopdownFxOverlay,
    logic: DriveLogic,
    pose: CarPose2D
) -> bool:
    """Запускает стартовый дым/букс при переходе из «стоим» в «поехали».

    На оффроуде стартовый буст-эффект не запускается: там читается только
    постоянная пыль.
    """
    spd = logic.speed
    start_move = False
    min_speed = float(TUNING.DRIVE.fx_start_move_min_speed)
    if overlay._prev_speed <= min_speed and spd > min_speed:
        if not logic.offroad:
            start_move = True
            fx_cx, fx_cy = pose.screen_center()
            overlay._drive_fx.start_move(int(fx_cx), int(fx_cy), overlay._next_fx_seed())
    overlay._prev_speed = spd
    return start_move


def topdown_fx_update_offroad_side_sign(overlay: TopdownFxOverlay, logic: DriveLogic) -> None:
    """Обновляет знак стороны оффроуда относительно центра дороги."""
    if not logic.offroad:
        return
    rd = logic.road_d
    if rd > 0.0:
        overlay._offroad_side_sign = 1
    elif rd < 0.0:
        overlay._offroad_side_sign = -1


def topdown_fx_flush_hit_events(overlay: TopdownFxOverlay, proj: TopdownProjector) -> None:
    """Сбрасывает очередь попаданий препятствий в `DriveFx` текущего кадра."""
    if len(overlay._hit_events) <= 0:
        return

    i = 0
    while i < len(overlay._hit_events):
        wx, wy, nx, ny, impact, hit_r = overlay._hit_events[i]
        seed = overlay._next_fx_seed()
        overlay._drive_fx.obstacle_hit(wx, wy, nx, ny, impact, seed, hit_r, proj)
        i += 1
    overlay._hit_events = []
