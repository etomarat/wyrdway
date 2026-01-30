from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import *

_stub_t: float = 0.0


def stub_scene_update(dt: float) -> None:
    global _stub_t
    _stub_t += dt


def stub_scene_draw() -> None:
    cls(0)
    print("WYRDWAY M1", 84, 40, 12)
    print("STUB SCENE", 80, 50, 12)
