from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from tic80 import btnp, cls, print
    from ..core.input_buttons import Button
    from ..types import RegionMapEnterParams


_selected_node: int
_node_count: int


def region_map_scene_reset_state() -> None:
    global _selected_node, _node_count
    _selected_node = 1
    _node_count = 5

region_map_scene_reset_state()


def region_map_scene_enter(params: Optional[RegionMapEnterParams] = None) -> None:
    region_map_scene_reset_state()


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
