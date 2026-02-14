from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...data.tuning import TUNING


TUNING.PURSUER.enabled = True

TUNING.PURSUER.grace_meters = 90.0
TUNING.PURSUER.grace_seconds_cap = 4.0
TUNING.PURSUER.start_gap_s = 140.0

TUNING.PURSUER.base_speed = 72.0
TUNING.PURSUER.slow_catchup = 55.0
TUNING.PURSUER.offroad_catchup = 35.0

TUNING.PURSUER.show_dist_s = 120.0
TUNING.PURSUER.near_dist_s = 55.0

TUNING.PURSUER.strike_cooldown_sec = 1.35
TUNING.PURSUER.strike_drain_amount = 2
TUNING.PURSUER.center_window_d = 6.0

TUNING.PURSUER.boost_pushback_s = 28.0

TUNING.PURSUER.strike_shake_intensity = 0.9
TUNING.PURSUER.near_vignette = 0.25
TUNING.PURSUER.near_noise = 0.35
TUNING.PURSUER.strike_flash_seconds = 0.22
