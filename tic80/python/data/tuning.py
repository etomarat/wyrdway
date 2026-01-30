from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import *
    from ..types import TuningDict

TUNING: "TuningDict" = {
    "tuning_version": 1,
    "CORE": {
        # Fixed timestep in seconds (TIC-80 runs at 60 FPS by default).
        "dt": 1 / 60,
    },
    "DEBUG": {
        # Initial debug overlay state on boot.
        "overlay_default": True,
    },
}
