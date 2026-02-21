from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import include

    from .tuning_core import CoreTuning as CoreTuning
    from .tuning_core import DebugTuning as DebugTuning
    from .tuning_core import ProfileTuning as ProfileTuning
    from .tuning_drive import DriveTuning as DriveTuning
    from .tuning_poi import PoiTuning as PoiTuning
    from .tuning_pursuer import PursuerVariantId as PursuerVariantId
    from .tuning_pursuer import PursuerVariantTuning as PursuerVariantTuning
    from .tuning_pursuer import PursuerTuning as PursuerTuning
    from .tuning_root import Tuning as Tuning

include("contracts.tuning_root")
