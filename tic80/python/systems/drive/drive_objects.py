from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...contracts import Tuning
    from .rng import Rng
    from .road_model import RoadModel


class DriveObstacle:
    """Жёсткое препятствие в road-space координатах (s, d).

    - `s` — прогресс по сегменту
    - `d` — боковое смещение от центра дороги
    - `radius` — радиус для коллизий/визуализации (в road-space единицах)
    """

    def __init__(self, s: float, d: float, radius: float) -> None:
        self.s = s
        self.d = d
        self.radius = radius
        self.hit = False


class DriveHazardZone:
    """Опасная зона: диапазон по s + радиус по d (капсула на дороге).

    - `s_start..s_end` — диапазон по прогрессу
    - `d_center` — центр зоны по d
    - `radius` — ширина зоны в стороны (по d)
    - `tick_damage` — урон в секунду, пока игрок внутри
    - `grip_mult` — множитель сцепления (effective_grip), пока игрок внутри
    """

    def __init__(
        self,
        s_start: float,
        s_end: float,
        d_center: float,
        radius: float,
        tick_damage: float,
        grip_mult: float
    ) -> None:
        self.s_start = s_start
        self.s_end = s_end
        self.d_center = d_center
        self.radius = radius
        self.tick_damage = tick_damage
        self.grip_mult = grip_mult


class DriveObjects:
    """Набор объектов сегмента DRIVE, сгенерированный по seed.

    Важно: это прототип под m1.5. Пока он отвечает только за:
    - хранение списка объектов (Obstacle / HazardZone),
    - детерминированный seeded-спавн при старте сегмента.

    Коллизии/эффекты делаем отдельно, чтобы можно было ревьюить по шагам.
    """

    def __init__(
        self,
        obstacles: list[DriveObstacle],
        hazard_zones: list[DriveHazardZone]
    ) -> None:
        self._obstacles = obstacles
        self._hazard_zones = hazard_zones

    def obstacles_count(self) -> int:
        """Количество препятствий на сегмент."""
        return len(self._obstacles)

    def hazard_zones_count(self) -> int:
        """Количество опасных зон на сегмент."""
        return len(self._hazard_zones)

    def obstacles_items(self) -> list[DriveObstacle]:
        """Копия списка препятствий."""
        return list(self._obstacles)

    def hazard_zones_items(self) -> list[DriveHazardZone]:
        """Копия списка опасных зон."""
        return list(self._hazard_zones)

    @classmethod
    def from_road_and_tuning(cls, seed: int, road: RoadModel, tuning: Tuning):
        """Генерирует объекты сегмента по seed + параметрам тюнинга.

        Принципы (m1.5):
        - детерминированно по seed (для сравнения A/B и тюнинга);
        - не спавнить в safe-start диапазоне;
        - выдерживать минимальную дистанцию между объектами по s;
        - избегать краёв дороги (через `spawn_min_distance_from_edges`).
        """
        d = tuning.DRIVE
        rng = Rng(seed ^ 0x9E3779B9)

        total = road.segment_total_length
        safe = road.safe_start_length
        width = road.road_width

        max_d = width * 0.5 - d.spawn_min_distance_from_edges
        if max_d < 0.0:
            max_d = 0.0

        obstacles: list[DriveObstacle] = []
        hazard_zones: list[DriveHazardZone] = []

        obstacles_n = int((total / 100.0) * d.obstacles_per_100m + 0.5)
        zones_n = int((total / 100.0) * d.zones_per_100m + 0.5)

        if safe > total:
            safe = total

        i = 0
        attempts = 0
        while i < obstacles_n and attempts < obstacles_n * 80 + 80:
            attempts += 1
            s = rng.uniform(safe, total)
            d0 = rng.uniform(-max_d, max_d) if max_d > 0.0 else 0.0

            ok = True
            j = 0
            while j < len(obstacles):
                if abs(obstacles[j].s - s) < d.spawn_min_distance_between:
                    ok = False
                    break
                j += 1
            if ok:
                obstacles.append(DriveObstacle(s, d0, d.obstacle_radius))
                i += 1

        i = 0
        attempts = 0
        zone_len = d.zone_length
        if zone_len < road.ds:
            zone_len = road.ds

        zone_s_max = total - zone_len
        if zone_s_max < safe:
            zone_s_max = safe

        while i < zones_n and attempts < zones_n * 80 + 80:
            attempts += 1
            s_start = rng.uniform(safe, zone_s_max)
            s_end = s_start + zone_len
            d_center = rng.uniform(-max_d, max_d) if max_d > 0.0 else 0.0

            ok = True
            j = 0
            while j < len(hazard_zones):
                if abs(hazard_zones[j].s_start - s_start) < d.spawn_min_distance_between:
                    ok = False
                    break
                j += 1
            if ok:
                hazard_zones.append(DriveHazardZone(
                    s_start,
                    s_end,
                    d_center,
                    d.zone_radius,
                    d.zone_tick_damage,
                    d.zone_grip_mult
                ))
                i += 1

        return cls(obstacles, hazard_zones)
