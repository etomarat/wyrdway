from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .drive_logic_core import DriveLogic


def drive_logic_update_dash_cooldown(logic: DriveLogic, dt: float) -> None:
    """Update internal dash cooldown timer."""
    if logic._dash_cd > 0.0:
        logic._dash_cd -= dt
        if logic._dash_cd < 0.0:
            logic._dash_cd = 0.0


def drive_logic_speed_factor(speed: float, max_speed: float) -> float:
    """Normalize speed to [0..1] range."""
    if max_speed <= 0.0:
        return 0.0
    sf = speed / max_speed
    if sf > 1.0:
        sf = 1.0
    if sf < 0.0:
        sf = 0.0
    return sf


def drive_logic_estimated_vmax(logic: DriveLogic, offroad: bool) -> float:
    """Estimate asymptotic top speed from accel/drag coefficients."""
    d = logic._tuning.DRIVE
    accel = d.accel
    if accel <= 0.0:
        return 0.0

    drag_lin = d.drag_lin
    drag_quad = d.drag_quad
    if offroad:
        drag_lin += d.offroad_drag_lin
        drag_quad += d.offroad_drag_quad

    speed_cap = d.speed_cap

    v = 0.0
    if drag_lin <= 0.0 and drag_quad <= 0.0:
        v = speed_cap if speed_cap > 0.0 else 9999.0
    elif drag_quad <= 0.0:
        if drag_lin <= 0.0:
            v = speed_cap if speed_cap > 0.0 else 9999.0
        else:
            v = accel / drag_lin
    else:
        disc = drag_lin * drag_lin + 4.0 * drag_quad * accel
        if disc < 0.0:
            disc = 0.0
        v = (-drag_lin + (disc ** 0.5)) / (2.0 * drag_quad)

    if speed_cap > 0.0 and v > speed_cap:
        v = speed_cap
    if v < 0.0:
        v = 0.0
    return v
