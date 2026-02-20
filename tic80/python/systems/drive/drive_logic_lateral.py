from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .drive_logic_core import DriveLogic


def drive_logic_effective_grip(
    logic: DriveLogic,
    handbrake: bool,
    offroad_before: bool
) -> float:
    """Compute per-frame effective grip with handbrake/offroad/zone modifiers."""
    d = logic._tuning.DRIVE

    effective_grip = d.grip
    if handbrake:
        effective_grip *= d.handbrake_grip_mult
    if offroad_before:
        effective_grip *= d.offroad_grip_mult
    if logic._zone_grip_mult != 1.0:
        effective_grip *= logic._zone_grip_mult
    if logic._zone_grip_floor > 0.0 and effective_grip < logic._zone_grip_floor:
        effective_grip = logic._zone_grip_floor
    if effective_grip < 0.0:
        effective_grip = 0.0
    logic._dbg_effective_grip = effective_grip
    return effective_grip


def drive_logic_apply_lateral_damping(
    logic: DriveLogic,
    dt: float,
    v_side: float,
    effective_grip: float,
    speed_factor: float
) -> float:
    """Damp side velocity (drift) and update debug values."""
    d = logic._tuning.DRIVE
    v_side_before = v_side

    slip = 1.0 + d.side_slip_speed_mult * speed_factor
    if slip < 1.0:
        slip = 1.0
    side_damp = 1.0 - (d.side_friction * effective_grip * dt) / slip
    if side_damp < 0.0:
        side_damp = 0.0
    if side_damp > 1.0:
        side_damp = 1.0

    v_side *= side_damp
    logic._dbg_side_damp = side_damp
    if dt > 0.0:
        logic._dbg_side_accel = (v_side - v_side_before) / dt
    else:
        logic._dbg_side_accel = 0.0

    return v_side


def drive_logic_apply_zone_antislip(logic: DriveLogic, dt: float, v_side: float) -> float:
    """Apply extra side damping from zone antislip."""
    k = logic._zone_antislip
    if k <= 0.0 or dt <= 0.0:
        return v_side
    factor = 1.0 - k * dt
    if factor < 0.0:
        factor = 0.0
    if factor > 1.0:
        factor = 1.0
    v_side *= factor
    return v_side


def drive_logic_apply_side_recovery(
    logic: DriveLogic,
    v_fwd: float,
    v_side_before: float,
    v_side_after: float,
    throttle: bool,
    speed_factor: float
) -> float:
    """Convert part of removed side speed back into forward speed."""
    d = logic._tuning.DRIVE
    if not throttle:
        return v_fwd
    if speed_factor < d.side_recovery_min_speed_factor:
        return v_fwd
    if d.side_recovery_mult <= 0.0:
        return v_fwd

    removed = abs(v_side_before) - abs(v_side_after)
    if removed <= 0.0:
        return v_fwd

    add = removed * d.side_recovery_mult
    if add > d.side_recovery_max_add:
        add = d.side_recovery_max_add
    if add < 0.0:
        add = 0.0
    logic._dbg_side_recovery = add

    if v_fwd >= 0.0:
        return v_fwd + add
    return v_fwd - add
