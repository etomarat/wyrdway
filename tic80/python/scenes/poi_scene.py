from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from tic80 import *
    from ..types import PoiEnterParams

DEFAULT_POI_TIMER: float = 10.0

_poi_timer: float = DEFAULT_POI_TIMER


def poi_scene_enter(params: Optional[PoiEnterParams] = None) -> None:
    global _poi_timer
    _poi_timer = DEFAULT_POI_TIMER


def poi_scene_update(dt: float) -> None:
    global _poi_timer
    _poi_timer = max(0.0, _poi_timer - dt)


def poi_scene_draw() -> None:
    cls(0)
    print("POI", 112, 30, 12)
    print("timer=" + str(round(_poi_timer, 1)), 82, 50, 12)
    print("A = LOOT", 90, 70, 12)
    print("B = LEAVE", 88, 80, 12)


def poi_scene_exit() -> None:
    pass
