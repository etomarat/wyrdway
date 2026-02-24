from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .drive_logic_core import DriveLogic


def drive_logic_apply_drag(logic: DriveLogic, dt: float) -> None:
    """Apply global movement drag plus offroad drag contribution."""
    d = logic._tuning.DRIVE
    drag_lin = d.drag_lin
    drag_quad = d.drag_quad
    if logic._offroad:
        drag_lin += d.offroad_drag_lin
        drag_quad += d.offroad_drag_quad
    if drag_lin <= 0.0 and drag_quad <= 0.0:
        return

    v2 = logic._vx * logic._vx + logic._vy * logic._vy
    spd = v2 ** 0.5
    drag = drag_lin + drag_quad * spd
    if drag <= 0.0:
        return

    mult = 1.0 - drag * dt
    if mult < 0.0:
        mult = 0.0
    if mult > 1.0:
        mult = 1.0
    logic._vx *= mult
    logic._vy *= mult


def drive_logic_apply_fuel(logic: DriveLogic, dt: float, throttle: bool) -> None:
    """Consume fuel based on input and surface (offroad is more expensive)."""
    d = logic._tuning.DRIVE
    fuel_spend = d.fuel_per_sec_idle * dt
    if throttle:
        fuel_spend += d.fuel_per_sec_throttle * dt
    if logic._offroad and d.offroad_fuel_mult > 0.0:
        fuel_spend *= d.offroad_fuel_mult
    if dt > 0.0:
        logic._dbg_fuel_per_sec = fuel_spend / dt
    else:
        logic._dbg_fuel_per_sec = 0.0
    if fuel_spend > 0.0:
        logic._run.consume_fuel(fuel_spend)


def drive_logic_apply_offroad_damage(logic: DriveLogic, dt: float) -> None:
    """Apply small continuous damage while moving offroad."""
    d = logic._tuning.DRIVE
    if not logic._offroad:
        return
    rate = d.offroad_damage_per_sec
    if rate <= 0.0:
        return

    v2 = logic._vx * logic._vx + logic._vy * logic._vy
    if v2 <= 0.0:
        return
    speed = v2 ** 0.5
    if speed <= d.offroad_damage_min_speed:
        return

    dmg = rate * dt
    if dmg > 0.0:
        logic._run.apply_damage(dmg)


def drive_logic_apply_zone_boost(logic: DriveLogic, dt: float) -> None:
    """Apply zone boost acceleration to velocity for this frame."""
    forward = logic._zone_boost_forward
    center = logic._zone_boost_center
    if forward <= 0.0 and center <= 0.0:
        return
    if dt <= 0.0:
        return

    dir_x, dir_y = logic._road.direction_at(logic._road_s)
    nrm_x = -dir_y
    nrm_y = dir_x

    ax = dir_x * forward
    ay = dir_y * forward

    if center > 0.0:
        if logic._road_d > 0.0:
            ax -= nrm_x * center
            ay -= nrm_y * center
        elif logic._road_d < 0.0:
            ax += nrm_x * center
            ay += nrm_y * center

    logic._vx += ax * dt
    logic._vy += ay * dt
