from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...contracts import Tuning

    from .rng import Rng


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
        self._ramp_fraction = ramp_fraction

        self._curv: list[float] = []
        self._build()

    @classmethod
    def from_tuning(cls, seed: int, tuning: "Tuning") -> "RoadModel":
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

            target = rng.uniform(-self._max_curvature, self._max_curvature)

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

    def curvature_at(self, s: float) -> float:
        if s <= 0:
            return self._curv[0]
        idx = int(s / self.ds)
        if idx < 0:
            idx = 0
        if idx >= len(self._curv):
            idx = len(self._curv) - 1
        return self._curv[idx]

    def width_at(self, s: float) -> float:
        return self.road_width

