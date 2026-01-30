from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from tic80 import *
    from ..types import ResultEnterParams

DEFAULT_RESULT_TEXT: str = "RESULT: OK"

_result_text: str = DEFAULT_RESULT_TEXT


def result_scene_enter(params: Optional[ResultEnterParams] = None) -> None:
    global _result_text
    _result_text = DEFAULT_RESULT_TEXT
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
