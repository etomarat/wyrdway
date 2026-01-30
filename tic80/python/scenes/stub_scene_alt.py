from typing import TYPE_CHECKING, Optional, Dict, Any

if TYPE_CHECKING:
    from tic80 import *

_stub_t: float = 0.0


def stub_scene_alt_enter(params: Optional[Dict[str, Any]] = None) -> None:
    global _stub_t
    _stub_t = 0.0


def stub_scene_alt_update(dt: float) -> None:
    global _stub_t
    _stub_t += dt


def stub_scene_alt_draw() -> None:
    cls(1)
    print("WYRDWAY M1", 84, 40, 11)
    print("ALT STUB", 88, 50, 11)
    print("t=" + str(round(_stub_t, 2)), 86, 60, 11)


def stub_scene_alt_exit() -> None:
    pass
