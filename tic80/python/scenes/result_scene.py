from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from tic80 import cls, print
    from ..types import ResultEnterParams

_result_text: str


def result_scene_reset_state() -> None:
    global _result_text
    _result_text = "RESULT: OK"


def result_scene_enter(params: Optional[ResultEnterParams] = None) -> None:
    result_scene_reset_state()
    if params is not None and "text" in params:
        _result_text = str(params["text"])


def result_scene_update(dt: float) -> None:
    pass


def result_scene_draw() -> None:
    cls(0)
    print("RESULT", 100, 40, 12)
    print(_result_text, 72, 60, 12)
    print("A = BACK", 90, 80, 12)


def result_scene_exit() -> None:
    pass


result_scene_reset_state()
