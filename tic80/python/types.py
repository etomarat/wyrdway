from typing import Callable, Dict, Optional, TypedDict, Any


class CoreTuning(TypedDict):
    dt: float


class DebugTuning(TypedDict):
    overlay_default: bool


class TuningDict(TypedDict):
    tuning_version: int
    CORE: CoreTuning
    DEBUG: DebugTuning


class SceneDict(TypedDict):
    enter: Callable[[Optional[Dict[str, Any]]], None]
    update: Callable[[float], None]
    draw: Callable[[], None]
    exit: Callable[[], None]
