from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .drive_logic_core import DriveLogic


def drive_logic_set_zone_grip_mult(logic: DriveLogic, mult: float) -> None:
    """Применяет множитель сцепления зоны, с зажимом в диапазон `>= 0`."""
    if mult < 0.0:
        mult = 0.0
    logic._zone_grip_mult = mult


def drive_logic_set_zone_boost(logic: DriveLogic, forward_accel: float, center_accel: float) -> None:
    """Применяет ускорения зоны и обновляет debug-поля текущего кадра.

    - `forward_accel`: вдоль дороги.
    - `center_accel`: к центру дороги.
    """
    if forward_accel < 0.0:
        forward_accel = 0.0
    if center_accel < 0.0:
        center_accel = 0.0
    logic._zone_boost_forward = forward_accel
    logic._zone_boost_center = center_accel
    logic._dbg_zone_boost_forward = forward_accel
    logic._dbg_zone_boost_center = center_accel


def drive_logic_set_zone_antislip(logic: DriveLogic, strength: float) -> None:
    """Применяет анти-занос зоны (гашение боковой скорости), `>= 0`."""
    if strength < 0.0:
        strength = 0.0
    logic._zone_antislip = strength
    logic._dbg_zone_antislip = strength


def drive_logic_set_zone_grip_floor(logic: DriveLogic, value: float) -> None:
    """Применяет нижнюю границу сцепления в зоне, `>= 0`."""
    if value < 0.0:
        value = 0.0
    logic._zone_grip_floor = value


def drive_logic_init_on_road_start(logic: DriveLogic) -> None:
    """Ставит машину в начало дороги и выравнивает heading по трассе."""
    cx, cy = logic._road.sample_centerline(0.0)
    dx, dy = logic._road.direction_at(0.0)
    logic._x = cx
    logic._y = cy
    logic._fwd_x = dx
    logic._fwd_y = dy
    logic._vx = 0.0
    logic._vy = 0.0
    logic._road_idx = 0
    logic._update_road_projection()


def drive_logic_rotate_heading(logic: DriveLogic, delta: float) -> None:
    """Поворачивает heading на малый угол через приближение малых углов.

    После поворота вектор направления нормализуется в unit-длину.
    """
    dx = logic._fwd_x
    dy = logic._fwd_y

    c = 1.0 - 0.5 * delta * delta
    s = delta
    ndx = dx * c - dy * s
    ndy = dx * s + dy * c

    l2 = ndx * ndx + ndy * ndy
    if l2 > 0.0:
        inv = 1.0 / (l2 ** 0.5)
        ndx *= inv
        ndy *= inv

    logic._fwd_x = ndx
    logic._fwd_y = ndy
