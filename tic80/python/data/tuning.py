from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import *
    from ..types import TuningDict

TUNING: "TuningDict" = {
    "tuning_version": 1,
    "CORE": {
        "dt": 1 / 60,
    },
    "DEBUG": {
        "overlay_default": True,
    },
}
