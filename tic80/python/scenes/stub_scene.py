from typing import TYPE_CHECKING, Optional, Dict, Any

if TYPE_CHECKING:
    from tic80 import cls, print

_stub_t: float = 0.0


def stub_scene_enter(params: Optional[Dict[str, Any]] = None) -> None:
    global _stub_t
    _stub_t = 0.0


def stub_scene_update(dt: float) -> None:
    global _stub_t
    _stub_t += dt


def stub_scene_draw() -> None:
    cls(0)
    print("WYRDWAY M1", 84, 40, 12)
    print("STUB SCENE", 82, 50, 12)
    print("t=" + str(round(_stub_t, 2)), 82, 60, 12)


def stub_scene_exit() -> None:
    pass
