from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import SegmentPlan


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
