from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from .route_planner import RoutePlanner

PoiAction = Literal["loot", "leave", "timeout"]
EscapeOutcome = Literal["ok", "fail"]
RunItemId = Literal["scrap"]
LegKind = Literal["OUTBOUND", "RETURN"]
PoiType = Literal["gas_station", "scrapyard", "depot"]


class RunItem:
    __slots__ = ("_id", "_qty")

    def __init__(self, item_id: RunItemId, qty: int) -> None:
        self._id: RunItemId = item_id
        self._qty = qty

    @property
    def id(self) -> RunItemId:
        return self._id

    @property
    def qty(self) -> int:
        return self._qty

    def take(self, amount: int) -> int:
        take = int(amount)
        if take <= 0:
            return 0
        if take > self._qty:
            take = self._qty
        self._qty -= take
        return take


class SegmentRewards:
    __slots__ = ("_scrap", "_fuel")

    def __init__(self, scrap: int, fuel: int) -> None:
        self._scrap = max(0, int(scrap))
        self._fuel = max(0, int(fuel))

    @property
    def scrap(self) -> int:
        return self._scrap

    @property
    def fuel(self) -> int:
        return self._fuel

class SegmentPlan:
    __slots__ = ("_from_node_id", "_to_node_id", "_poi_type", "_leg_kind",
                 "_seed_base", "_len_units", "_rewards")

    def __init__(
        self,
        from_node_id: int,
        to_node_id: int,
        poi_type: PoiType,
        leg_kind: LegKind,
        seed_base: int,
        len_units: float,
        rewards: SegmentRewards
    ) -> None:
        self._from_node_id = int(from_node_id)
        self._to_node_id = int(to_node_id)
        self._poi_type: PoiType = poi_type
        self._leg_kind: LegKind = leg_kind
        self._seed_base = int(seed_base)
        self._len_units = float(len_units)
        self._rewards = rewards

    @property
    def from_node_id(self) -> int:
        return self._from_node_id

    @property
    def to_node_id(self) -> int:
        return self._to_node_id

    @property
    def poi_type(self) -> PoiType:
        return self._poi_type

    @property
    def leg_kind(self) -> LegKind:
        return self._leg_kind

    @property
    def seed_base(self) -> int:
        return self._seed_base

    @property
    def len_units(self) -> float:
        return self._len_units

    @property
    def rewards(self) -> SegmentRewards:
        return self._rewards


class RouteStack:
    __slots__ = ("_outbound", "_return")

    def __init__(self) -> None:
        self._outbound: list[SegmentPlan] = []
        self._return: list[SegmentPlan] = []

    def outbound_items(self) -> list[SegmentPlan]:
        return list(self._outbound)

    def return_items(self) -> list[SegmentPlan]:
        return list(self._return)

    def find_outbound_by_target(self, to_node_id: int) -> SegmentPlan | None:
        i = 0
        while i < len(self._outbound):
            plan = self._outbound[i]
            if plan.to_node_id == to_node_id:
                return plan
            i += 1
        return None

    def push_outbound(self, plan: SegmentPlan) -> None:
        self._outbound.append(plan)

    def find_return_by_nodes(self, from_node_id: int, to_node_id: int) -> SegmentPlan | None:
        i = 0
        while i < len(self._return):
            plan = self._return[i]
            if plan.from_node_id == from_node_id and plan.to_node_id == to_node_id:
                return plan
            i += 1
        return None

    def push_return(self, plan: SegmentPlan) -> None:
        self._return.append(plan)


class SegmentDelta:
    __slots__ = ("_node_id", "_poi_action", "_items_gained",
                 "_escape_outcome", "_fuel_gained")

    def __init__(self, node_id: int | None) -> None:
        self._node_id = node_id
        self._poi_action: PoiAction | None = None
        self._items_gained: list[RunItem] = []
        self._escape_outcome: EscapeOutcome | None = None
        self._fuel_gained = 0

    @property
    def node_id(self) -> int | None:
        return self._node_id

    @property
    def poi_action(self) -> PoiAction | None:
        return self._poi_action

    @property
    def escape_outcome(self) -> EscapeOutcome | None:
        return self._escape_outcome

    @property
    def fuel_gained(self) -> int:
        return self._fuel_gained

    def set_poi_action(self, action: PoiAction) -> None:
        self._poi_action = action

    def set_escape_outcome(self, outcome: EscapeOutcome) -> None:
        self._escape_outcome = outcome

    def add_item_gained(self, item: RunItem) -> None:
        self._items_gained.append(item)

    def add_fuel_gained(self, amount: int) -> None:
        self._fuel_gained += max(0, int(amount))

    def items_gained_count(self) -> int:
        return len(self._items_gained)


class RunState:
    __slots__ = ("_seed", "_node_id", "_car_hp",
                  "_car_fuel", "_inventory", "_delta",
                 "_route_stack", "_active_segment", "_planner")

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
        scrap, fuel = self._planner.roll_segment_rewards(
            to_node_id, seed_base, poi_type)
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
