from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from tic80 import *
    from ..types import DriveEnterParams

DEFAULT_DRIVE_T: float = 0.0
DEFAULT_DRIVE_MODE: str = "travel"

_drive_t: float = DEFAULT_DRIVE_T
_drive_mode: str = DEFAULT_DRIVE_MODE


def drive_scene_enter(params: Optional[DriveEnterParams] = None) -> None:
    global _drive_t, _drive_mode
    _drive_t = DEFAULT_DRIVE_T
    _drive_mode = DEFAULT_DRIVE_MODE
    if params is not None and "mode" in params:
        _drive_mode = str(params["mode"])


def drive_scene_update(dt: float) -> None:
    global _drive_t
    _drive_t += dt


def drive_scene_draw() -> None:
    cls(0)
    print("DRIVE", 104, 30, 12)
    print("mode=" + _drive_mode, 86, 50, 12)
    print("t=" + str(round(_drive_t, 2)), 92, 60, 12)
    print("A = ARRIVE", 80, 100, 12)


def drive_scene_exit() -> None:
    pass
