from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..tuning import TUNING


# Initial debug overlay state on boot.
# Master debug switch for release/dev builds.
TUNING.DEBUG.debug_enabled = False

DEBUG_OVERLAY_DEFAULT = False
PERF_OVERLAY_DEFAULT = True
DRIVE_PRESET_CHASE_TEST_ENABLED = True

TUNING.DEBUG.overlay_default = (
    TUNING.DEBUG.debug_enabled and DEBUG_OVERLAY_DEFAULT
)

# Performance overlay (FPS + frame/cpu ms). Toggle in-game with Button.X.
TUNING.DEBUG.perf_overlay_default = (
    TUNING.DEBUG.debug_enabled and PERF_OVERLAY_DEFAULT
)

# Drive preset "CHASE TEST" button:
# - never available when debug is disabled
# - can be disabled separately even in debug builds.
TUNING.DEBUG.drive_preset_chase_test_enabled = (
    TUNING.DEBUG.debug_enabled and DRIVE_PRESET_CHASE_TEST_ENABLED
)
