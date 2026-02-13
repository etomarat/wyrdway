from typing import Literal

PoiAction = Literal["loot", "leave", "timeout"]
EscapeOutcome = Literal["ok", "fail"]
RunItemId = Literal["scrap"]
LegKind = Literal["OUTBOUND", "RETURN"]


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
    __slots__ = ("_from_node_id", "_to_node_id", "_leg_kind",
                 "_seed_base", "_len_units", "_rewards")

    def __init__(
        self,
        from_node_id: int,
        to_node_id: int,
        leg_kind: LegKind,
        seed_base: int,
        len_units: float,
        rewards: SegmentRewards
    ) -> None:
        self._from_node_id = int(from_node_id)
        self._to_node_id = int(to_node_id)
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
    __slots__ = ("_node_id", "_poi_action", "_items_gained", "_escape_outcome")

    def __init__(self, node_id: int | None) -> None:
        self._node_id = node_id
        self._poi_action: PoiAction | None = None
        self._items_gained: list[RunItem] = []
        self._escape_outcome: EscapeOutcome | None = None

    @property
    def node_id(self) -> int | None:
        return self._node_id

    @property
    def poi_action(self) -> PoiAction | None:
        return self._poi_action

    @property
    def escape_outcome(self) -> EscapeOutcome | None:
        return self._escape_outcome

    def set_poi_action(self, action: PoiAction) -> None:
        self._poi_action = action

    def set_escape_outcome(self, outcome: EscapeOutcome) -> None:
        self._escape_outcome = outcome

    def add_item_gained(self, item: RunItem) -> None:
        self._items_gained.append(item)

    def items_gained_count(self) -> int:
        return len(self._items_gained)


class RunState:
    __slots__ = ("_seed", "_node_id", "_car_hp",
                 "_car_fuel", "_inventory", "_delta",
                 "_route_stack", "_active_segment")

    def __init__(self, seed: int, car_hp: float, car_fuel: float) -> None:
        self._seed = seed
        self._node_id: int | None = None
        self._car_hp = car_hp
        self._car_fuel = car_fuel
        self._inventory: list[RunItem] = []
        self._delta: SegmentDelta | None = None
        self._route_stack = RouteStack()
        self._active_segment: SegmentPlan | None = None

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

    def apply_damage(self, amount: float) -> None:
        self._car_hp = max(0, self._car_hp - amount)

    def consume_fuel(self, amount: float) -> None:
        self._car_fuel = max(0.0, self._car_fuel - amount)

    def add_fuel(self, amount: float) -> None:
        self._car_fuel = max(0.0, self._car_fuel + float(amount))

    def reset_car_stats(self, car_hp: float, car_fuel: float) -> None:
        self._car_hp = car_hp
        self._car_fuel = car_fuel

    def _mix_seed(self, node_id: int, salt: int) -> int:
        s = self._seed & 0xFFFFFFFF
        n = (int(node_id) + 1) & 0xFFFFFFFF
        x = (s ^ (n * 0x45D9F3B) ^ salt) & 0xFFFFFFFF
        if x == 0:
            x = 0x12345678
        x ^= (x << 13) & 0xFFFFFFFF
        x ^= (x >> 17) & 0xFFFFFFFF
        x ^= (x << 5) & 0xFFFFFFFF
        return x & 0xFFFFFFFF

    def _outbound_seed_base(self, to_node_id: int) -> int:
        return self._mix_seed(to_node_id, 0xC8013EA4)

    def _roll_segment_rewards(self, to_node_id: int, seed_base: int) -> SegmentRewards:
        x = (seed_base ^ ((to_node_id + 17) * 0x9E3779B9)) & 0xFFFFFFFF
        scrap = 3 + int(x % 9)
        y = ((x * 1103515245) + 12345) & 0x7FFFFFFF
        fuel = 6 + int(y % 19)
        return SegmentRewards(scrap, fuel)

    def preview_outbound_rewards(self, to_node_id: int) -> SegmentRewards:
        existing = self._route_stack.find_outbound_by_target(to_node_id)
        if existing is not None:
            rewards = existing.rewards
            return SegmentRewards(rewards.scrap, rewards.fuel)
        seed_base = self._outbound_seed_base(to_node_id)
        return self._roll_segment_rewards(to_node_id, seed_base)

    def ensure_outbound_segment(self, to_node_id: int, len_units: float) -> SegmentPlan:
        to_node_id = int(to_node_id)
        plan = self._route_stack.find_outbound_by_target(to_node_id)
        if plan is None:
            from_node_id = 0
            if self._node_id is not None:
                from_node_id = self._node_id
            seed_base = self._outbound_seed_base(to_node_id)
            rewards = self._roll_segment_rewards(to_node_id, seed_base)
            plan = SegmentPlan(
                from_node_id,
                to_node_id,
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
                "RETURN",
                active.seed_base,
                active.len_units,
                SegmentRewards(0, 0)
            )
            self._route_stack.push_return(plan)
        self._active_segment = plan
        self._node_id = to_node_id
        return plan
