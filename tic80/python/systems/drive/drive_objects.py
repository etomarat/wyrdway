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


class DriveZone:
    """Дорожная зона (m1.5): полоса по s и радиус по d.

    - `s_start..s_end` — диапазон по прогрессу
    - `d_center` — центр зоны по d
    - `radius` — ширина зоны в стороны (по d)
    - `grip_mult` — множитель сцепления (effective_grip), пока игрок внутри

    В текущем дизайне m1.5 это “ускорялки/безопасные полосы” (boost pads),
    а не “обязательный урон по таймеру”.
    """

    def __init__(
        self,
        s_start: float,
        s_end: float,
        d_center: float,
        radius: float,
        grip_mult: float
    ) -> None:
        self.s_start = s_start
        self.s_end = s_end
        self.d_center = d_center
        self.radius = radius
        self.grip_mult = grip_mult


class DriveObjects:
    """Набор объектов сегмента DRIVE, сгенерированный по seed.

    Важно: это прототип под m1.5. Пока он отвечает только за:
    - хранение списка объектов (Obstacle / Zone),
    - детерминированный seeded-спавн при старте сегмента.

    Коллизии/эффекты делаем отдельно, чтобы можно было ревьюить по шагам.
    """

    def __init__(
        self,
        obstacles: list[DriveObstacle],
        zones: list[DriveZone]
    ) -> None:
        self._obstacles = obstacles
        self._zones = zones

    def obstacles_count(self) -> int:
        """Количество препятствий на сегмент."""
        return len(self._obstacles)

    def zones_count(self) -> int:
        """Количество зон на сегмент."""
        return len(self._zones)

    def obstacles_items(self) -> list[DriveObstacle]:
        """Ссылка на внутренний список препятствий (без копии).

        Важно: не мутировать список извне. Используйте только для чтения.
        """
        return self._obstacles

    def zones_items(self) -> list[DriveZone]:
        """Ссылка на внутренний список зон (без копии).

        Важно: не мутировать список извне. Используйте только для чтения.
        """
        return self._zones

    @classmethod
    def from_road_and_tuning(
        cls,
        seed: int,
        road: RoadModel,
        tuning: Tuning,
        spawn_threats: bool = True,
        reverse_layout: bool = False
    ):
        """Генерирует объекты сегмента по seed + параметрам тюнинга.

        Принципы (m1.5):
        - детерминированно по seed (для сравнения A/B и тюнинга);
        - base-слой (зоны/ускорители) и threats-слой (препятствия) генерируются
          разными RNG, чтобы base не зависел от включения/выключения threats;
        - не спавнить в safe-start диапазоне;
        - выдерживать минимальную дистанцию между объектами по s;
        - избегать краёв дороги (через `spawn_min_distance_from_edges`).
        """
        d = tuning.DRIVE
        rng_threats = Rng(seed ^ 0x9E3779B9)
        rng_base = Rng(seed ^ 0xA341316C)

        total = road.segment_total_length
        safe = road.safe_start_length
        width = road.road_width

        max_d_base = width * 0.5 - d.spawn_min_distance_from_edges
        if max_d_base < 0.0:
            max_d_base = 0.0

        rmin = d.obstacle_radius_min
        rmax = d.obstacle_radius_max
        if rmin < 0.0:
            rmin = 0.0
        if rmax < rmin:
            rmax = rmin

        obstacles: list[DriveObstacle] = []
        zones: list[DriveZone] = []

        obstacles_n = int((total / 100.0) * d.obstacles_per_100m + 0.5)
        zones_n = int((total / 100.0) * d.zones_per_100m + 0.5)

        if safe > total:
            safe = total

        if spawn_threats:
            i = 0
            attempts = 0
            while i < obstacles_n and attempts < obstacles_n * 80 + 80:
                attempts += 1
                s = rng_threats.uniform(safe, total)

                radius_int = -1
                weights = d.obstacle_radius_weights
                if weights is not None and len(weights) > 0:
                    idx = rng_threats.choice_weighted_index(weights)
                    if idx >= 0:
                        radius_int = idx

                if radius_int < 0:
                    rmin_i = int(rmin)
                    if float(rmin_i) < rmin:
                        rmin_i += 1
                    rmax_i = int(rmax)
                    if rmax_i < rmin_i:
                        rmax_i = rmin_i
                    radius_int = rng_threats.randint_inclusive(rmin_i, rmax_i)

                radius = float(radius_int)
                max_d = max_d_base - radius
                if max_d < 0.0:
                    max_d = 0.0
                d0 = rng_threats.uniform(-max_d, max_d) if max_d > 0.0 else 0.0

                ok = True
                j = 0
                while j < len(obstacles):
                    if abs(obstacles[j].s - s) < d.spawn_min_distance_between:
                        ok = False
                        break
                    j += 1
                if ok:
                    obstacles.append(DriveObstacle(s, d0, radius))
                    i += 1

        i = 0
        attempts = 0
        zone_len = d.zone_length
        if zone_len < road.ds:
            zone_len = road.ds
        zone_radius = d.zone_radius
        if zone_radius < 0.0:
            zone_radius = 0.0
        max_d_zone = max_d_base - zone_radius
        if max_d_zone < 0.0:
            max_d_zone = 0.0

        zone_s_max = total - zone_len
        if zone_s_max < safe:
            zone_s_max = safe

        while i < zones_n and attempts < zones_n * 80 + 80:
            attempts += 1
            s_start = rng_base.uniform(safe, zone_s_max)
            s_end = s_start + zone_len
            d_center = rng_base.uniform(-max_d_zone, max_d_zone) if max_d_zone > 0.0 else 0.0

            ok = True
            j = 0
            while j < len(zones):
                z = zones[j]
                left = z.s_start - d.spawn_min_distance_between
                right = z.s_end + d.spawn_min_distance_between
                if s_end >= left and s_start <= right:
                    ok = False
                    break
                j += 1
            if ok:
                zones.append(DriveZone(
                    s_start,
                    s_end,
                    d_center,
                    zone_radius,
                    d.zone_grip_mult
                ))
                i += 1

        if reverse_layout:
            i = 0
            while i < len(obstacles):
                ob = obstacles[i]
                ob.s = max(0.0, total - ob.s)
                ob.d = -ob.d
                i += 1

            i = 0
            while i < len(zones):
                z = zones[i]
                s_start = max(0.0, total - z.s_end)
                s_end = max(0.0, total - z.s_start)
                z.s_start = s_start
                z.s_end = s_end
                z.d_center = -z.d_center
                i += 1

        return cls(obstacles, zones)
