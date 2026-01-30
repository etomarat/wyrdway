from typing import TYPE_CHECKING, Optional, Dict, Any

if TYPE_CHECKING:
    from tic80 import *

_result_text: str = "RESULT: OK"


def result_scene_enter(params: Optional[Dict[str, Any]] = None) -> None:
    global _result_text
    _result_text = "RESULT: OK"
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
