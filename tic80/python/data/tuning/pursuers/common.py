from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....contracts import PursuerVariantTuning


def apply_common_pursuer_profile(profile: PursuerVariantTuning) -> None:
    p = profile

    # Chase kinematics.
    p.start_gap_s = 150.0
    p.base_speed = 106.0
    p.slow_catchup = 0.0
    p.offroad_catchup = 0.0

    # Distance thresholds.
    p.show_dist_s = 240.0
    p.near_dist_s = 24.0

    # Strike cadence and damage model.
    p.strike_cooldown_sec = 1.35
    p.strike_enable_fuel_phase = False
    p.strike_drain_hp_after_scrap = True

    # Strike gate.
    p.strike_min_speed = 0.0

    # Anti-chase event pushback.
    p.boost_pushback_s = 22.0

    # Debug.
    p.debug_contact_marker = False

    # Screen FX.
    p.strike_flash_seconds = 0.22
