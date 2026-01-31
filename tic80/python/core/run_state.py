from typing import Literal

PoiAction = Literal["loot", "leave", "timeout"]
EscapeOutcome = Literal["ok", "fail"]
RunItemId = Literal["scrap"]


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
                 "_car_fuel", "_inventory", "_delta")

    def __init__(self, seed: int, car_hp: float, car_fuel: float) -> None:
        self._seed = seed
        self._node_id: int | None = None
        self._car_hp = car_hp
        self._car_fuel = car_fuel
        self._inventory: list[RunItem] = []
        self._delta: SegmentDelta | None = None

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
