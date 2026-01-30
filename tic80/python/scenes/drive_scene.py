from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from tic80 import cls, print
    from ..types import DriveEnterParams


_drive_t: float
_drive_mode: str


def drive_scene_reset_state() -> None:
    global _drive_t, _drive_mode
    _drive_t = 0.0
    _drive_mode = "travel"

drive_scene_reset_state()


def drive_scene_enter(params: Optional[DriveEnterParams] = None) -> None:
    drive_scene_reset_state()
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
