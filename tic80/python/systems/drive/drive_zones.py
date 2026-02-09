from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .drive_logic_core import DriveLogic
    from .drive_objects import DriveZone


def zone_at_hitboxes(logic: DriveLogic, zones: list[DriveZone]) -> DriveZone | None:
    """Возвращает зону, которая пересекается с хитбоксом машины (если есть).

    Почему так:
    - игрок ориентируется по спрайту
    - у машины уже есть 2 круговых хитбокса (перед/зад), настроенные под спрайт
    - если проверять зону только по “центральной точке физики”, игрок будет видеть
      “я на полосках, но эффекта нет”

    Реализация:
    - берём 2 круга машины в road-space (`DriveLogic.hitbox_road_circles`)
    - каждая зона — прямоугольник в (s,d):
        s in [s_start..s_end]
        d in [d_center-radius .. d_center+radius]
    - проверяем пересечение круга и прямоугольника (circle-vs-AABB в road-space)
    """

    def clamp(v: float, lo: float, hi: float) -> float:
        if v < lo:
            return lo
        if v > hi:
            return hi
        return v

    rear_s, rear_d, rear_r, front_s, front_d, front_r = logic.hitbox_road_circles()

    if rear_r > 0.0:
        i = 0
        while i < len(zones):
            z = zones[i]
            zs0 = z.s_start
            zs1 = z.s_end
            zd0 = z.d_center - z.radius
            zd1 = z.d_center + z.radius

            cs = clamp(rear_s, zs0, zs1)
            cd = clamp(rear_d, zd0, zd1)
            ds = rear_s - cs
            dd = rear_d - cd
            if (ds * ds + dd * dd) <= (rear_r * rear_r):
                return z
            i += 1

    if front_r > 0.0:
        i = 0
        while i < len(zones):
            z = zones[i]
            zs0 = z.s_start
            zs1 = z.s_end
            zd0 = z.d_center - z.radius
            zd1 = z.d_center + z.radius

            cs = clamp(front_s, zs0, zs1)
            cd = clamp(front_d, zd0, zd1)
            ds = front_s - cs
            dd = front_d - cd
            if (ds * ds + dd * dd) <= (front_r * front_r):
                return z
            i += 1

    return None

