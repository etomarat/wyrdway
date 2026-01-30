from typing import Callable, Dict, Optional, TypedDict, Any, Literal


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


class GarageEnterParams(TypedDict, total=False):
    pass


class RegionMapEnterParams(TypedDict, total=False):
    pass


class DriveEnterParams(TypedDict):
    mode: Literal["travel", "extract"]


class PoiEnterParams(TypedDict, total=False):
    pass


class ResultEnterParams(TypedDict, total=False):
    text: str
