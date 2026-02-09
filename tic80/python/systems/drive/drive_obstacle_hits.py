from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    from ...core.run_state import RunState
    from ...data.tuning import Tuning
    from .drive_logic_core import DriveLogic
    from .drive_objects import DriveObjects
    from .road_model import RoadModel

    ObstacleHitNotify = Callable[[float, float, float, float, float, float, float], None]


def apply_obstacle_hits(
    run: RunState,
    road: RoadModel,
    logic: DriveLogic,
    objects: DriveObjects,
    tuning: Tuning,
    notify_hit: ObstacleHitNotify
) -> None:
    """Проверяет столкновения с препятствиями и применяет урон.

    Коллизия:
    - препятствие = круг (radius) в world-space,
    - машина = 2 круга (задняя/передняя ось), позиции берём из DriveLogic.
    """
    d = tuning.DRIVE
    dmg_base = d.obstacle_damage_base
    dmg_mult = d.obstacle_damage_impact_mult
    dmg_min_impact = d.obstacle_damage_min_impact
    dmg_max = d.obstacle_damage_max

    rear_x, rear_y, rear_r, front_x, front_y, front_r = logic.hitbox_world_circles()

    # Небольшая оптимизация: проверяем только препятствия рядом по s.
    max_ds = d.obstacle_render_range_s
    if max_ds < 0.0:
        max_ds = 0.0
    p_s = logic.road_s

    obstacles = objects.obstacles_items_view()
    i = 0
    while i < len(obstacles):
        o = obstacles[i]
        if o.hit:
            i += 1
            continue
        if abs(o.s - p_s) > max_ds:
            i += 1
            continue

        cx, cy = road.sample_centerline(o.s)
        dx, dy = road.direction_at(o.s)
        nrm_x = -dy
        nrm_y = dx
        ox = cx + nrm_x * o.d
        oy = cy + nrm_y * o.d

        r0 = o.radius + rear_r
        r1 = o.radius + front_r
        hit = False
        best_d2 = None
        hit_cx = 0.0
        hit_cy = 0.0
        hit_r = 0.0

        if r0 > 0.0:
            vx = ox - rear_x
            vy = oy - rear_y
            d2 = vx * vx + vy * vy
            if d2 <= (r0 * r0):
                if best_d2 is None or d2 < best_d2:
                    hit = True
                    best_d2 = d2
                    hit_cx = rear_x
                    hit_cy = rear_y
                    hit_r = rear_r
        if r1 > 0.0:
            vx = ox - front_x
            vy = oy - front_y
            d2 = vx * vx + vy * vy
            if d2 <= (r1 * r1):
                if best_d2 is None or d2 < best_d2:
                    hit = True
                    best_d2 = d2
                    hit_cx = front_x
                    hit_cy = front_y
                    hit_r = front_r

        if hit:
            o.hit = True

            # Нормаль контакта: от препятствия к кругу машины.
            nx = hit_cx - ox
            ny = hit_cy - oy
            n2 = nx * nx + ny * ny
            if n2 > 0.0:
                inv = 1.0 / (n2 ** 0.5)
                nx *= inv
                ny *= inv
            else:
                # Редкий случай: центры совпали. Берём нормаль против скорости,
                # а если скорости нет — "назад" от направления машины.
                fwd_x = logic.fwd_x
                fwd_y = logic.fwd_y
                right_x = -fwd_y
                right_y = fwd_x
                v_fwd = logic.v_forward
                v_side = logic.v_side
                vwx = fwd_x * v_fwd + right_x * v_side
                vwy = fwd_y * v_fwd + right_y * v_side
                v2 = vwx * vwx + vwy * vwy
                if v2 > 0.0:
                    inv = 1.0 / (v2 ** 0.5)
                    nx = -vwx * inv
                    ny = -vwy * inv
                else:
                    nx = -fwd_x
                    ny = -fwd_y

            # Точка контакта на поверхности препятствия (удобно для FX).
            contact_x = ox + nx * o.radius
            contact_y = oy + ny * o.radius

            # Сила удара: скорость "в препятствие" по нормали.
            fwd_x = logic.fwd_x
            fwd_y = logic.fwd_y
            right_x = -fwd_y
            right_y = fwd_x
            v_fwd = logic.v_forward
            v_side = logic.v_side
            vwx = fwd_x * v_fwd + right_x * v_side
            vwy = fwd_y * v_fwd + right_y * v_side
            impact = -(vwx * nx + vwy * ny)
            if impact < 0.0:
                impact = 0.0

            # Урон как функция от impact (см. tuning).
            impact2 = impact - dmg_min_impact
            if impact2 < 0.0:
                impact2 = 0.0
            dmg = dmg_base + impact2 * dmg_mult
            if dmg < 0.0:
                dmg = 0.0
            if dmg_max > 0.0 and dmg > dmg_max:
                dmg = dmg_max

            if dmg > 0.0:
                run.apply_damage(dmg)

            notify_hit(
                contact_x,
                contact_y,
                nx,
                ny,
                impact,
                dmg,
                hit_r
            )

        i += 1
