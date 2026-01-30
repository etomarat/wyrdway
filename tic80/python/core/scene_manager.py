from typing import TYPE_CHECKING, Dict, Optional, Any

if TYPE_CHECKING:
    from tic80 import *
    from ..types import SceneDict

_scenes: Dict[str, SceneDict] = {}
_current_scene_id: Optional[str] = None
_current_scene: Optional[SceneDict] = None


def scene_manager_register(scene_id: str, scene: SceneDict) -> None:
    _scenes[scene_id] = scene


def scene_manager_go(scene_id: str, params: Optional[Dict[str, Any]] = None) -> None:
    global _current_scene_id, _current_scene
    if scene_id not in _scenes:
        return
    if _current_scene is not None:
        _current_scene["exit"]()
    _current_scene_id = scene_id
    _current_scene = _scenes[scene_id]
    _current_scene["enter"](params)


def scene_manager_update(dt: float) -> None:
    if _current_scene is None:
        return
    _current_scene["update"](dt)


def scene_manager_draw() -> None:
    if _current_scene is None:
        return
    _current_scene["draw"]()


def scene_manager_get_current_id() -> Optional[str]:
    return _current_scene_id
