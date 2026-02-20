from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .drive_logic_core import DriveLogic


def drive_logic_apply_steering(
    logic: DriveLogic,
    dt: float,
    steer_input: int,
    throttle: bool,
    handbrake: bool,
    offroad_before: bool,
    speed: float,
    speed_factor: float
) -> None:
    """Rotate heading from steering input and current movement conditions."""
    d = logic._tuning.DRIVE

    steer_scale = d.steer_scale_max + (d.steer_scale_min - d.steer_scale_max) * speed_factor
    if steer_scale < 0.0:
        steer_scale = 0.0
    if speed < d.steer_min_speed:
        steer_scale = 0.0
    if logic.v_forward < 0.0:
        steer_scale *= d.steer_reverse_mult
    logic._dbg_steer_scale = steer_scale

    yaw = steer_input * d.steer_rate * steer_scale * dt
    if handbrake and throttle and steer_input != 0:
        yaw = drive_logic_apply_handbrake_steer_boost(logic, yaw, speed_factor)
    if offroad_before:
        yaw *= d.offroad_steer_mult
    if yaw != 0.0:
        logic._rotate_heading(yaw)


def drive_logic_apply_handbrake_steer_boost(
    logic: DriveLogic,
    yaw: float,
    speed_factor: float
) -> float:
    """Boost steering while handbrake is active, mostly at higher speed."""
    d = logic._tuning.DRIVE

    hb_min = d.handbrake_steer_min_speed_factor
    if hb_min < 0.0:
        hb_min = 0.0
    if hb_min > 1.0:
        hb_min = 1.0

    hb_t = 0.0
    if speed_factor > hb_min:
        denom = 1.0 - hb_min
        if denom > 0.0:
            hb_t = (speed_factor - hb_min) / denom
        else:
            hb_t = 1.0
    if hb_t > 1.0:
        hb_t = 1.0
    if hb_t < 0.0:
        hb_t = 0.0

    hb_gain = d.handbrake_steer_mult - 1.0
    return yaw * (1.0 + hb_gain * hb_t)


def drive_logic_apply_dash(logic: DriveLogic, v_fwd: float, dash_pressed: bool) -> float:
    """Apply dash impulse if enabled and cooldown is ready."""
    d = logic._tuning.DRIVE
    if dash_pressed and d.dash_impulse > 0.0 and logic._dash_cd <= 0.0:
        v_fwd += d.dash_impulse
        logic._dash_cd = d.dash_cooldown
    return v_fwd


def drive_logic_apply_longitudinal(
    logic: DriveLogic,
    dt: float,
    v_fwd: float,
    throttle: bool,
    brake: bool,
    handbrake: bool,
    steer_input: int,
    speed_factor: float
) -> float:
    """Apply forward/backward acceleration, braking, coasting and handbrake decel."""
    d = logic._tuning.DRIVE

    if throttle and not brake:
        if v_fwd < 0.0:
            v_fwd = _approach(v_fwd, 0.0, d.brake * dt)
        else:
            v_fwd += d.accel * dt
    elif brake and not throttle:
        if v_fwd > 0.0:
            v_fwd = _approach(v_fwd, 0.0, d.brake * dt)
        else:
            v_fwd -= d.accel * dt
    else:
        v_fwd = _approach(v_fwd, 0.0, d.coast_decel * dt)

    if handbrake and d.handbrake_decel > 0.0:
        v_fwd = drive_logic_apply_handbrake_decel(
            logic,
            dt,
            v_fwd,
            throttle,
            steer_input,
            speed_factor
        )

    return v_fwd


def drive_logic_apply_handbrake_decel(
    logic: DriveLogic,
    dt: float,
    v_fwd: float,
    throttle: bool,
    steer_input: int,
    speed_factor: float
) -> float:
    """Apply extra longitudinal deceleration from handbrake."""
    d = logic._tuning.DRIVE
    hb_sf = speed_factor
    if hb_sf < d.handbrake_decel_min_speed_factor:
        hb_sf = d.handbrake_decel_min_speed_factor
    hb_decel = d.handbrake_decel * hb_sf
    if throttle:
        if steer_input != 0:
            hb_decel *= d.handbrake_decel_throttle_turn_mult
        else:
            hb_decel *= d.handbrake_decel_throttle_straight_mult
    logic._dbg_handbrake_decel = hb_decel
    return _approach(v_fwd, 0.0, hb_decel * dt)


def drive_logic_clamp_v_fwd(logic: DriveLogic, v_fwd: float) -> float:
    """Clamp reverse speed and optional positive speed cap."""
    d = logic._tuning.DRIVE
    if v_fwd < -d.max_reverse_speed:
        v_fwd = -d.max_reverse_speed
    if d.speed_cap > 0.0 and v_fwd > d.speed_cap:
        v_fwd = d.speed_cap
    return v_fwd


def _approach(value: float, target: float, amount: float) -> float:
    """Сдвигает `value` к `target` максимум на `amount` за шаг."""
    if value < target:
        value += amount
        if value > target:
            value = target
        return value
    if value > target:
        value -= amount
        if value < target:
            value = target
        return value
    return value
