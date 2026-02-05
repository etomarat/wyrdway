from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..tuning import TUNING


# Fixed timestep in seconds (TIC-80 runs at 60 FPS by default).
TUNING.CORE.dt = 1 / 60
