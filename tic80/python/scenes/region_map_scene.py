from typing import TYPE_CHECKING, Optional, Dict, Any

if TYPE_CHECKING:
    from tic80 import *

_selected_node: int = 1
_node_count: int = 5


def region_map_scene_enter(params: Optional[Dict[str, Any]] = None) -> None:
    global _selected_node
    _selected_node = 1


def region_map_scene_update(dt: float) -> None:
    global _selected_node
    if btnp(2):
        _selected_node = max(1, _selected_node - 1)
    if btnp(3):
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
