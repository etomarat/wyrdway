from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..data.tuning import TUNING
    from ..systems.drive.rng import lcg_next_u32


class RoutePlanner:
    __slots__ = ("_run_seed")

    def __init__(self, run_seed: int) -> None:
        self._run_seed = int(run_seed)

    def _mix_seed(self, node_id: int, salt: int) -> int:
        s = self._run_seed & 0xFFFFFFFF
        n = (int(node_id) + 1) & 0xFFFFFFFF
        x = (s ^ (n * 0x45D9F3B) ^ salt) & 0xFFFFFFFF
        if x == 0:
            x = 0x12345678
        x ^= (x << 13) & 0xFFFFFFFF
        x ^= (x >> 17) & 0xFFFFFFFF
        x ^= (x << 5) & 0xFFFFFFFF
        return x & 0xFFFFFFFF

    def outbound_seed_base(self, to_node_id: int) -> int:
        return self._mix_seed(to_node_id, 0xC8013EA4)

    def _next_u32(self, x: int) -> int:
        return lcg_next_u32(x)

    def _roll_range(self, x: int, min_inclusive: int, max_inclusive: int) -> tuple[int, int]:
        a = int(min_inclusive)
        b = int(max_inclusive)
        if b < a:
            b = a
        span = b - a + 1
        if span <= 1:
            return a, self._next_u32(x)
        n = self._next_u32(x)
        return a + int(n % span), n

    def _pick_weighted_index(self, x: int, weights: list[float]) -> tuple[int, int]:
        n = self._next_u32(x)
        total = 0.0
        i = 0
        last_positive = 0
        while i < len(weights):
            w = float(weights[i])
            if w > 0.0:
                total += w
                last_positive = i
            i += 1
        if total <= 0.0:
            return 0, n

        r = (n / 4294967296.0) * total
        acc = 0.0
        i = 0
        while i < len(weights):
            w = float(weights[i])
            if w > 0.0:
                acc += w
                if r < acc:
                    return i, n
            i += 1
        return last_positive, n

    def pick_outbound_poi_type(self, to_node_id: int, seed_base: int) -> str:
        x = (seed_base ^ ((to_node_id + 31) * 0x85EBCA6B)) & 0xFFFFFFFF
        weights = TUNING.POI.poi_type_weights
        idx, _ = self._pick_weighted_index(x, weights)
        if idx == 0:
            return "gas_station"
        if idx == 1:
            return "scrapyard"
        return "depot"

    def roll_segment_rewards(self, to_node_id: int, seed_base: int, poi_type: str) -> tuple[int, int]:
        x = (seed_base ^ ((to_node_id + 17) * 0x9E3779B9)) & 0xFFFFFFFF
        poi = TUNING.POI

        if poi_type == "gas_station":
            scrap, x = self._roll_range(
                x, poi.gas_station_scrap_min, poi.gas_station_scrap_max)
            fuel, x = self._roll_range(
                x, poi.gas_station_fuel_min, poi.gas_station_fuel_max)
            return scrap, fuel

        if poi_type == "scrapyard":
            scrap, x = self._roll_range(
                x, poi.scrapyard_scrap_min, poi.scrapyard_scrap_max)
            fuel, x = self._roll_range(
                x, poi.scrapyard_fuel_min, poi.scrapyard_fuel_max)
            return scrap, fuel

        scrap, x = self._roll_range(x, poi.depot_scrap_min, poi.depot_scrap_max)
        fuel, x = self._roll_range(x, poi.depot_fuel_min, poi.depot_fuel_max)
        return scrap, fuel
