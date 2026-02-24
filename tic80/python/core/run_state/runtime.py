from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..route_planner import RoutePlanner
    from .models import PoiType, RunItem, RunItemId, SegmentDelta, SegmentPlan, SegmentRewards
    from .routes import RouteStack


class RunState:
    __slots__ = ("_seed", "_node_id", "_car_hp", "_car_fuel", "_inventory", "_delta", "_route_stack", "_active_segment", "_planner")

    def __init__(self, seed: int, car_hp: float, car_fuel: float) -> None:
        self._seed = seed
        self._node_id: int | None = None
        self._car_hp = car_hp
        self._car_fuel = car_fuel
        self._inventory: list[RunItem] = []
        self._delta: SegmentDelta | None = None
        self._route_stack = RouteStack()
        self._active_segment: SegmentPlan | None = None
        self._planner = RoutePlanner(seed)

    @property
    def seed(self) -> int:
        return self._seed

    @property
    def node_id(self) -> int | None:
        return self._node_id

    @property
    def car_hp(self) -> float:
        return self._car_hp

    @property
    def car_fuel(self) -> float:
        return self._car_fuel

    @property
    def delta(self) -> SegmentDelta | None:
        return self._delta

    @property
    def route_stack(self) -> RouteStack:
        return self._route_stack

    @property
    def active_segment(self) -> SegmentPlan | None:
        return self._active_segment

    def set_node_id(self, node_id: int) -> None:
        self._node_id = node_id

    def ensure_delta(self, node_id: int | None) -> SegmentDelta:
        if self._delta is None:
            self._delta = SegmentDelta(node_id)
        return self._delta

    def inventory_count(self) -> int:
        return len(self._inventory)

    def inventory_items(self) -> list[RunItem]:
        return list(self._inventory)

    def add_item(self, item_id: RunItemId, qty: int) -> RunItem:
        item = RunItem(item_id, qty)
        self._inventory.append(item)
        return item

    def run_scrap(self) -> int:
        total = 0
        i = 0
        while i < len(self._inventory):
            item = self._inventory[i]
            if item.id == "scrap":
                total += item.qty
            i += 1
        return total

    def drain_scrap(self, amount: int) -> int:
        need = int(amount)
        if need <= 0:
            return 0
        taken = 0
        i = len(self._inventory) - 1
        while i >= 0 and need > 0:
            item = self._inventory[i]
            if item.id == "scrap" and item.qty > 0:
                got = item.take(need)
                taken += got
                need -= got
                if item.qty <= 0:
                    del self._inventory[i]
            i -= 1
        return taken

    def apply_damage(self, amount: float) -> None:
        self._car_hp = max(0, self._car_hp - amount)

    def consume_fuel(self, amount: float) -> None:
        self._car_fuel = max(0.0, self._car_fuel - amount)

    def add_fuel(self, amount: float) -> None:
        self._car_fuel = max(0.0, self._car_fuel + float(amount))

    def reset_car_stats(self, car_hp: float, car_fuel: float) -> None:
        self._car_hp = car_hp
        self._car_fuel = car_fuel

    def _outbound_seed_base(self, to_node_id: int) -> int:
        return self._planner.outbound_seed_base(to_node_id)

    def _pick_outbound_poi_type(self, to_node_id: int, seed_base: int) -> PoiType:
        poi_type = self._planner.pick_outbound_poi_type(to_node_id, seed_base)
        if poi_type == "gas_station":
            return "gas_station"
        if poi_type == "scrapyard":
            return "scrapyard"
        return "depot"

    def _roll_segment_rewards(self, to_node_id: int, seed_base: int, poi_type: PoiType) -> SegmentRewards:
        scrap, fuel = self._planner.roll_segment_rewards(to_node_id, seed_base, poi_type)
        return SegmentRewards(scrap, fuel)

    def preview_outbound_rewards(self, to_node_id: int) -> SegmentRewards:
        existing = self._route_stack.find_outbound_by_target(to_node_id)
        if existing is not None:
            rewards = existing.rewards
            return SegmentRewards(rewards.scrap, rewards.fuel)
        seed_base = self._outbound_seed_base(to_node_id)
        poi_type = self._pick_outbound_poi_type(to_node_id, seed_base)
        return self._roll_segment_rewards(to_node_id, seed_base, poi_type)

    def preview_outbound_seed_base(self, to_node_id: int) -> int:
        existing = self._route_stack.find_outbound_by_target(to_node_id)
        if existing is not None:
            return existing.seed_base
        return self._outbound_seed_base(to_node_id)

    def preview_outbound_poi_type(self, to_node_id: int) -> PoiType:
        existing = self._route_stack.find_outbound_by_target(to_node_id)
        if existing is not None:
            return existing.poi_type
        seed_base = self._outbound_seed_base(to_node_id)
        return self._pick_outbound_poi_type(to_node_id, seed_base)

    def ensure_outbound_segment(self, to_node_id: int, len_units: float) -> SegmentPlan:
        to_node_id = int(to_node_id)
        plan = self._route_stack.find_outbound_by_target(to_node_id)
        if plan is None:
            from_node_id = 0
            if self._node_id is not None:
                from_node_id = self._node_id
            seed_base = self._outbound_seed_base(to_node_id)
            poi_type = self._pick_outbound_poi_type(to_node_id, seed_base)
            rewards = self._roll_segment_rewards(to_node_id, seed_base, poi_type)
            plan = SegmentPlan(
                from_node_id,
                to_node_id,
                poi_type,
                "OUTBOUND",
                seed_base,
                len_units,
                rewards
            )
            self._route_stack.push_outbound(plan)
        self._active_segment = plan
        self._node_id = to_node_id
        return plan

    def ensure_return_from_active_outbound(self) -> SegmentPlan | None:
        active = self._active_segment
        if active is None:
            return None
        if active.leg_kind == "RETURN":
            return active
        if active.leg_kind != "OUTBOUND":
            return None

        from_node_id = active.to_node_id
        to_node_id = active.from_node_id
        plan = self._route_stack.find_return_by_nodes(from_node_id, to_node_id)
        if plan is None:
            plan = SegmentPlan(
                from_node_id,
                to_node_id,
                active.poi_type,
                "RETURN",
                active.seed_base,
                active.len_units,
                SegmentRewards(0, 0)
            )
            self._route_stack.push_return(plan)
        self._active_segment = plan
        self._node_id = to_node_id
        return plan
