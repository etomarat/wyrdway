from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from tic80 import *
    from ..types import GarageEnterParams

_garage_note: str = "Press A to start run"


def garage_scene_enter(params: Optional[GarageEnterParams] = None) -> None:
    pass


def garage_scene_update(dt: float) -> None:
    pass


def garage_scene_draw() -> None:
    cls(0)
    print("GARAGE", 98, 40, 12)
    print(_garage_note, 56, 60, 12)


def garage_scene_exit() -> None:
    pass
