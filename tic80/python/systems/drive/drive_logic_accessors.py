from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .drive_logic_core import DriveLogic
    from .drive_logic_post_step import drive_logic_apply_zone_boost
    from .drive_logic_projection import (
        drive_hitbox_road_circles,
        drive_hitbox_world_circles,
        drive_project_world_to_road_near_idx,
        drive_update_road_projection
    )


def drive_logic_dbg_zone_boost_forward(logic: DriveLogic) -> float:
    """Текущее ускорение ускорялки вдоль дороги (units/sec^2), для дебага."""
    return logic._dbg_zone_boost_forward


def drive_logic_dbg_zone_boost_center(logic: DriveLogic) -> float:
    """Текущее ускорение ускорялки к центру дороги (units/sec^2), для дебага."""
    return logic._dbg_zone_boost_center


def drive_logic_dbg_zone_antislip(logic: DriveLogic) -> float:
    """Сила анти-заноса от зоны (1/sec), для дебага."""
    return logic._dbg_zone_antislip


def drive_logic_x(logic: DriveLogic) -> float:
    return logic._x


def drive_logic_y(logic: DriveLogic) -> float:
    return logic._y


def drive_logic_fwd_x(logic: DriveLogic) -> float:
    return logic._fwd_x


def drive_logic_fwd_y(logic: DriveLogic) -> float:
    return logic._fwd_y


def drive_logic_vx(logic: DriveLogic) -> float:
    return logic._vx


def drive_logic_vy(logic: DriveLogic) -> float:
    return logic._vy


def drive_logic_speed(logic: DriveLogic) -> float:
    v2 = logic._vx * logic._vx + logic._vy * logic._vy
    return float(v2 ** 0.5)


def drive_logic_v_forward(logic: DriveLogic) -> float:
    """Скорость вдоль направления машины (может быть отрицательной при реверсе)."""
    fwd_x = logic._fwd_x
    fwd_y = logic._fwd_y
    return logic._vx * fwd_x + logic._vy * fwd_y


def drive_logic_v_side(logic: DriveLogic) -> float:
    """Боковая скорость (как сильно “несёт боком” относительно направления)."""
    right_x = -logic._fwd_y
    right_y = logic._fwd_x
    return logic._vx * right_x + logic._vy * right_y


def drive_logic_road_s(logic: DriveLogic) -> float:
    """Прогресс вдоль дороги (проекция world position на centerline)."""
    return logic._road_s


def drive_logic_road_d(logic: DriveLogic) -> float:
    """Смещение от центра дороги (проекция на road-right нормаль)."""
    return logic._road_d


def drive_logic_offroad(logic: DriveLogic) -> bool:
    return logic._offroad


def drive_logic_steer_input(logic: DriveLogic) -> int:
    return logic._steer_input


def drive_logic_dbg_speed_factor(logic: DriveLogic) -> float:
    """Нормализованная скорость (0..1) для тюнинга управления."""
    return logic._dbg_speed_factor


def drive_logic_dbg_steer_scale(logic: DriveLogic) -> float:
    """Итоговый множитель руления в этом кадре."""
    return logic._dbg_steer_scale


def drive_logic_dbg_effective_grip(logic: DriveLogic) -> float:
    """effective_grip в этом кадре (с учётом ручника/оффроуда)."""
    return logic._dbg_effective_grip


def drive_logic_dbg_side_damp(logic: DriveLogic) -> float:
    """Итоговый коэффициент гашения боковой скорости (0..1) за кадр."""
    return logic._dbg_side_damp


def drive_logic_dbg_side_accel(logic: DriveLogic) -> float:
    """Боковое ускорение (units/sec^2) от гашения/коррекции заноса в кадре."""
    return logic._dbg_side_accel


def drive_logic_dbg_fuel_per_sec(logic: DriveLogic) -> float:
    """Текущий расход топлива в секунду (оценка для дебага)."""
    return logic._dbg_fuel_per_sec


def drive_logic_dbg_handbrake_decel(logic: DriveLogic) -> float:
    """Эффективное замедление от ручника в кадре (units/sec^2), для дебага."""
    return logic._dbg_handbrake_decel


def drive_logic_dbg_side_recovery(logic: DriveLogic) -> float:
    """Сколько скорости в кадре переведено из заноса в продольную ось (units/sec)."""
    return logic._dbg_side_recovery


def drive_logic_finished(logic: DriveLogic) -> bool:
    """True, если игрок доехал по дороге до конца сегмента."""
    return logic._road_s >= logic._road.segment_total_length


def drive_logic_hitbox_world(logic: DriveLogic) -> tuple[float, float, float, float, float, float]:
    """Возвращает 2 круговых хитбокса в world-space."""
    return drive_hitbox_world_circles(logic)


def drive_logic_hitbox_road(logic: DriveLogic) -> tuple[float, float, float, float, float, float]:
    """Возвращает 2 круговых хитбокса в road-space."""
    return drive_hitbox_road_circles(logic)


def drive_logic_project_world_to_road(
    logic: DriveLogic,
    x: float,
    y: float,
    idx_guess: int
) -> tuple[float, float]:
    """Проецирует world-точку в road-space около `idx_guess`."""
    return drive_project_world_to_road_near_idx(logic, x, y, idx_guess)


def drive_logic_apply_zone_boost_proxy(logic: DriveLogic, dt: float) -> None:
    """Применяет ускорялку зоны к текущему вектору скорости."""
    drive_logic_apply_zone_boost(logic, dt)


def drive_logic_update_road_projection_proxy(logic: DriveLogic) -> None:
    """Обновляет проекцию машины на дорогу (`road_s`, `road_d`, `offroad`)."""
    drive_update_road_projection(logic)
