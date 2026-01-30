from typing import Literal, TypedDict


class CoreTuning(TypedDict):
    dt: float


class DebugTuning(TypedDict):
    overlay_default: bool


class TuningDict(TypedDict):
    tuning_version: int
    CORE: CoreTuning
    DEBUG: DebugTuning


DriveMode = Literal["travel", "extract"]


class DriveEnterParams:
    __slots__ = ("mode",)

    def __init__(self, mode: DriveMode) -> None:
        self.mode = mode


class ResultEnterParams:
    __slots__ = ("text",)

    def __init__(self, text: str) -> None:
        self.text = text

