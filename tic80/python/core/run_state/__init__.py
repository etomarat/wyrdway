from typing import TYPE_CHECKING, Literal

PoiAction = Literal["loot", "leave", "timeout"]
EscapeOutcome = Literal["ok", "fail"]
RunItemId = Literal["scrap"]
LegKind = Literal["OUTBOUND", "RETURN"]
PoiType = Literal["gas_station", "scrapyard", "depot"]

if TYPE_CHECKING:
    from tic80 import include

    from .models import RunItem as _RunItem
    from .models import SegmentDelta as _SegmentDelta
    from .models import SegmentPlan as _SegmentPlan
    from .models import SegmentRewards as _SegmentRewards
    from .routes import RouteStack as _RouteStack
    from .runtime import RunState as _RunState

    RunItem = _RunItem
    SegmentDelta = _SegmentDelta
    SegmentPlan = _SegmentPlan
    SegmentRewards = _SegmentRewards
    RouteStack = _RouteStack
    RunState = _RunState


include("core.run_state.models")
include("core.run_state.routes")
include("core.run_state.runtime")
