from typing import TYPE_CHECKING, Optional, Dict, Any

if TYPE_CHECKING:
    from tic80 import *

_garage_note: str = "Press A to start run"


def garage_scene_enter(params: Optional[Dict[str, Any]] = None) -> None:
    pass


def garage_scene_update(dt: float) -> None:
    pass


def garage_scene_draw() -> None:
    cls(0)
    print("GARAGE", 98, 40, 12)
    print(_garage_note, 56, 60, 12)


def garage_scene_exit() -> None:
    pass
