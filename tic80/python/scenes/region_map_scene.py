from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from tic80 import *
    from ..core.input_buttons import Button
    from ..types import RegionMapEnterParams

DEFAULT_SELECTED_NODE: int = 1
DEFAULT_NODE_COUNT: int = 5

_selected_node: int = DEFAULT_SELECTED_NODE
_node_count: int = DEFAULT_NODE_COUNT


def region_map_scene_enter(params: Optional[RegionMapEnterParams] = None) -> None:
    global _selected_node
    _selected_node = DEFAULT_SELECTED_NODE


def region_map_scene_update(dt: float) -> None:
    global _selected_node
    if btnp(Button.UP):
        _selected_node = max(1, _selected_node - 1)
    if btnp(Button.DOWN):
        _selected_node = min(_node_count, _selected_node + 1)


def region_map_scene_draw() -> None:
    cls(0)
    print("REGION MAP", 84, 30, 12)
    for i in range(_node_count):
        node_id = i + 1
        marker = ">" if node_id == _selected_node else " "
        print(marker + " NODE " + str(node_id), 70, 50 + i * 8, 12)
    print("A = GO", 96, 100, 12)


def region_map_scene_exit() -> None:
    pass
