from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import include

    from .tuning_core import CoreTuning
    from .tuning_core import DebugTuning
    from .tuning_core import ProfileTuning
    from .tuning_drive import DriveTuning
    from .tuning_poi import PoiTuning
    from .tuning_pursuer import PursuerTuning

include("contracts.tuning_core")
include("contracts.tuning_drive")
include("contracts.tuning_poi")
include("contracts.tuning_pursuer")


class Tuning:
    tuning_version: int
    __slots__ = ("tuning_version", "CORE", "DEBUG", "PROFILE", "DRIVE", "POI", "PURSUER")

    def __init__(self) -> None:
        self.tuning_version = 0
        self.CORE = CoreTuning()
        self.DEBUG = DebugTuning()
        self.PROFILE = ProfileTuning()
        self.DRIVE = DriveTuning()
        self.POI = PoiTuning()
        self.PURSUER = PursuerTuning()
