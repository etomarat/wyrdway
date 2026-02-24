from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Self

    from ...contracts import Tuning

    from .rng import Rng
else:
    Self = object


class RoadModel:
    """Параметрическая дорога: curvature(s) + базовые параметры ширины/длины.

    В m1.5 RoadModel должна быть:
    - детерминированной по seed,
    - с safe-start (первые метры почти прямые),
    - с ограничением максимальной кривизны и плавной сменой curvature.
    """

    def __init__(
        self,
        seed: int,
        segment_total_length: float,
        safe_start_length: float,
        ds: float,
        road_width: float,
        min_piece_length: float,
        max_piece_length: float,
        max_curvature: float,
        straight_piece_chance: float,
        straight_max_curvature: float,
        ramp_fraction: float
    ) -> None:
        self.seed = seed
        self.segment_total_length = segment_total_length
        self.safe_start_length = safe_start_length
        self.ds = ds
        self.road_width = road_width
        self._min_piece_length = min_piece_length
        self._max_piece_length = max_piece_length
        self._max_curvature = max_curvature
        self._straight_piece_chance = straight_piece_chance
        self._straight_max_curvature = straight_max_curvature
        self._ramp_fraction = ramp_fraction

        self._curv: list[float] = []
        self._center_x: list[float] = []
        self._center_y: list[float] = []
        self._dir_x: list[float] = []
        self._dir_y: list[float] = []
        self._build()
        self._build_centerline()

    @classmethod
    def from_tuning(cls, seed: int, tuning: Tuning) -> Self:
        d = tuning.DRIVE
        return cls(
            seed,
            d.segment_total_length,
            d.safe_start_length,
            d.ds,
            d.road_width,
            d.min_piece_length,
            d.max_piece_length,
            d.max_curvature,
            d.straight_piece_chance,
            d.straight_max_curvature,
            d.ramp_fraction
        )

    @classmethod
    def from_tuning_with_length(
        cls,
        seed: int,
        tuning: Tuning,
        segment_total_length: float
    ) -> Self:
        d = tuning.DRIVE
        return cls(
            seed,
            segment_total_length,
            d.safe_start_length,
            d.ds,
            d.road_width,
            d.min_piece_length,
            d.max_piece_length,
            d.max_curvature,
            d.straight_piece_chance,
            d.straight_max_curvature,
            d.ramp_fraction
        )

    def _build(self) -> None:
        ds = self.ds
        if ds <= 0:
            ds = 1.0
            self.ds = ds

        total = self.segment_total_length
        if total <= 0:
            total = 1.0
            self.segment_total_length = total

        n = int(total / ds) + 1
        self._curv = [0.0] * n

        rng = Rng(self.seed)

        i = int(self.safe_start_length / ds)
        if i < 0:
            i = 0
        if i > n:
            i = n

        cur = 0.0
        while i < n:
            piece_len = rng.uniform(self._min_piece_length, self._max_piece_length)
            piece_n = int(piece_len / ds)
            if piece_n < 1:
                piece_n = 1

            end = i + piece_n
            if end > n:
                end = n

            target = self._pick_target_curvature(rng)

            ramp_n = int(piece_n * self._ramp_fraction)
            if ramp_n < 1:
                ramp_n = 1
            if ramp_n > piece_n:
                ramp_n = piece_n

            j = i
            ramp_end = i + ramp_n
            if ramp_end > end:
                ramp_end = end
            while j < ramp_end:
                t = (j - i + 1) / ramp_n
                self._curv[j] = cur + (target - cur) * t
                j += 1

            while j < end:
                self._curv[j] = target
                j += 1

            cur = target
            i = end

    def _pick_target_curvature(self, rng: Rng) -> float:
        """Выбирает target curvature для следующего куска дороги.

        По умолчанию target выбирается из [-max_curvature..+max_curvature], но это
        даёт “вечные повороты”. Чтобы иногда появлялись прямые участки, мы делаем
        bias:
        - с вероятностью `straight_piece_chance` берём маленький диапазон вокруг 0,
        - иначе берём полный диапазон.
        """
        full = self._max_curvature
        if full < 0.0:
            full = -full

        p = self._straight_piece_chance
        if p < 0.0:
            p = 0.0
        if p > 1.0:
            p = 1.0

        if p > 0.0 and rng.rand01() < p:
            m = self._straight_max_curvature
            if m < 0.0:
                m = -m
            if m > full:
                m = full
            return rng.uniform(-m, m)

        return rng.uniform(-full, full)

    def _build_centerline(self) -> None:
        """Предрасчёт centerline для top-down (список точек по шагам ds).

        Реализация не использует `math.sin/cos`: вместо этого мы храним
        forward-вектор (dir_x/dir_y) и каждый шаг поворачиваем его на маленький
        угол `delta = curvature * ds` через приближение малых углов.
        """
        n = len(self._curv)
        if n == 0:
            return

        ds = self.ds

        self._center_x = [0.0] * n
        self._center_y = [0.0] * n
        self._dir_x = [0.0] * n
        self._dir_y = [0.0] * n

        x = 0.0
        y = 0.0
        dx = 1.0
        dy = 0.0

        i = 0
        while i < n:
            self._center_x[i] = x
            self._center_y[i] = y
            self._dir_x[i] = dx
            self._dir_y[i] = dy

            delta = self._curv[i] * ds
            c = 1.0 - 0.5 * delta * delta
            s = delta
            ndx = dx * c - dy * s
            ndy = dx * s + dy * c
            l2 = ndx * ndx + ndy * ndy
            if l2 > 0.0:
                inv = 1.0 / (l2 ** 0.5)
                ndx *= inv
                ndy *= inv
            dx = ndx
            dy = ndy

            x += dx * ds
            y += dy * ds
            i += 1

    def reverse_geometry_in_place(self) -> None:
        """Разворачивает геометрию: новый s=0 начинается в старом конце сегмента."""
        n = len(self._center_x)
        if n <= 1:
            return

        curv_rev = [0.0] * n
        cx_rev = [0.0] * n
        cy_rev = [0.0] * n
        dx_rev = [0.0] * n
        dy_rev = [0.0] * n

        i = 0
        while i < n:
            src = n - 1 - i
            curv_rev[i] = -self._curv[src]
            cx_rev[i] = self._center_x[src]
            cy_rev[i] = self._center_y[src]
            dx_rev[i] = -self._dir_x[src]
            dy_rev[i] = -self._dir_y[src]
            i += 1

        x0 = cx_rev[0]
        y0 = cy_rev[0]
        i = 0
        while i < n:
            cx_rev[i] -= x0
            cy_rev[i] -= y0
            i += 1

        self._curv = curv_rev
        self._center_x = cx_rev
        self._center_y = cy_rev
        self._dir_x = dx_rev
        self._dir_y = dy_rev

    def curvature_at(self, s: float) -> float:
        """Возвращает кривизну дороги в точке прогресса `s`.

        `s` измеряется в тех же единицах, что и `segment_total_length`.
        Значение дискретизируется шагом `ds`.
        """
        if s <= 0:
            return self._curv[0]
        idx = int(s / self.ds)
        if idx < 0:
            idx = 0
        if idx >= len(self._curv):
            idx = len(self._curv) - 1
        return self._curv[idx]

    def width_at(self, s: float) -> float:
        """Ширина дороги в точке `s`.

        На m1.5 ширина константная, но метод оставлен, чтобы позже можно было
        делать сужения/расширения без переписывания логики.
        """
        return self.road_width

    def sample_centerline(self, s: float) -> tuple[float, float]:
        """Возвращает (x, y) центра дороги в точке `s`."""
        idx = int(s / self.ds)
        if idx < 0:
            idx = 0
        if idx >= len(self._center_x):
            idx = len(self._center_x) - 1
        return self._center_x[idx], self._center_y[idx]

    def direction_at(self, s: float) -> tuple[float, float]:
        """Возвращает unit-направление forward (dir_x, dir_y) вдоль дороги в `s`."""
        idx = int(s / self.ds)
        if idx < 0:
            idx = 0
        if idx >= len(self._dir_x):
            idx = len(self._dir_x) - 1
        return self._dir_x[idx], self._dir_y[idx]

    def center_points_len(self) -> int:
        """Количество предрасчитанных точек centerline."""
        return len(self._center_x)

    def center_point_at_index(
        self,
        idx: int
    ) -> tuple[float, float, float, float]:
        """Возвращает точку centerline по индексу.

        Формат: (center_x, center_y, dir_x, dir_y).
        Индекс соответствует дискретизации `ds`:
        - `s = idx * ds`
        """
        if idx < 0:
            idx = 0
        if idx >= len(self._center_x):
            idx = len(self._center_x) - 1
        return (
            self._center_x[idx],
            self._center_y[idx],
            self._dir_x[idx],
            self._dir_y[idx]
        )
