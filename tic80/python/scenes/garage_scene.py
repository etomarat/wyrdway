from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from tic80 import cls, print
    from ..types import GarageEnterParams


def garage_scene_reset_state() -> None:
    pass


garage_scene_reset_state()


def garage_scene_enter(params: Optional[GarageEnterParams] = None) -> None:
    garage_scene_reset_state()


def garage_scene_update(dt: float) -> None:
    pass


def garage_scene_draw() -> None:
    cls(0)
    print("GARAGE", 98, 40, 12)
    print("Press A to start run", 56, 60, 12)


def garage_scene_exit() -> None:
    pass
