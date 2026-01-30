from typing import TypedDict


class CoreTuning(TypedDict):
    dt: float


class DebugTuning(TypedDict):
    overlay_default: bool


class TuningDict(TypedDict):
    tuning_version: int
    CORE: CoreTuning
    DEBUG: DebugTuning
