from typing import Literal

PoiAction = Literal["loot", "leave", "timeout"]
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
    __slots__ = ("_from_node_id", "_to_node_id", "_poi_type", "_leg_kind", "_seed_base", "_len_units", "_rewards")

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


class SegmentDelta:
    __slots__ = ("_node_id", "_poi_action", "_items_gained", "_fuel_gained")

    def __init__(self, node_id: int | None) -> None:
        self._node_id = node_id
        self._poi_action: PoiAction | None = None
        self._items_gained: list[RunItem] = []
        self._fuel_gained = 0

    @property
    def node_id(self) -> int | None:
        return self._node_id

    @property
    def poi_action(self) -> PoiAction | None:
        return self._poi_action

    @property
    def fuel_gained(self) -> int:
        return self._fuel_gained

    def set_poi_action(self, action: PoiAction) -> None:
        self._poi_action = action

    def add_item_gained(self, item: RunItem) -> None:
        self._items_gained.append(item)

    def add_fuel_gained(self, amount: int) -> None:
        self._fuel_gained += max(0, int(amount))

    def items_gained_count(self) -> int:
        return len(self._items_gained)
