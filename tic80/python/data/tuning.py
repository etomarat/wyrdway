from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..contracts import Tuning

TUNING: Tuning = Tuning()
TUNING.tuning_version = 2

# Fixed timestep in seconds (TIC-80 runs at 60 FPS by default).
TUNING.CORE.dt = 1 / 60

# Initial debug overlay state on boot.
TUNING.DEBUG.overlay_default = True

TUNING.PROFILE.start_scrap = 0
TUNING.PROFILE.start_garage_hp = 100
TUNING.PROFILE.start_garage_fuel = 50.0
TUNING.PROFILE.repair_cost = 10
TUNING.PROFILE.repair_hp = 20

TUNING.DRIVE.fuel_per_sec = 1.0
TUNING.DRIVE.damage_per_sec = 0.5
TUNING.POI.timer_seconds = 10.0
TUNING.POI.scrap_per_loot = 1
