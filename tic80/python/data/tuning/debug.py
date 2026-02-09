from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..tuning import TUNING


# Initial debug overlay state on boot.
TUNING.DEBUG.overlay_default = False

# Performance overlay (FPS + frame/cpu ms). Toggle in-game with Button.X.
TUNING.DEBUG.perf_overlay_default = True
