from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....contracts import PursuerVariantTuning


ENTITY_PURSUER_PROFILE = PursuerVariantTuning()

p = ENTITY_PURSUER_PROFILE

# Display name in HUD/briefing.
p.name = "The Entity"

# Chase kinematics.
# start_gap_s: initial spawn distance behind player (meters along road).
# base_speed: base pursuer speed (units/sec).
# slow_catchup: extra speed when player is slow.
# offroad_catchup: extra speed when player is offroad.
p.start_gap_s = 150.0
p.base_speed = 100.0
p.slow_catchup = 0.0
p.offroad_catchup = 0.0

# Distance thresholds.
# show_dist_s: FAR/CHASE boundary; above this distance pursuer is FAR.
# near_dist_s: CHASE/NEAR boundary.
p.show_dist_s = 240.0
p.near_dist_s = 24.0

# Visual alignment.
# contact_offset_s: shifts visual body behind logical contact point.
p.contact_offset_s = 0.0
# intro_entry_screen_y: initial off-screen Y for intro arrival animation (px).
# intro_entry_seconds: intro arrival duration (sec).
p.intro_entry_screen_y = 146.0
p.intro_entry_seconds = 0.45

# Strike cadence and damage model.
# strike_cooldown_sec: delay between consecutive strikes.
# strike_drain_amount: resource loss per strike tick.
# strike_enable_fuel_phase: alternate SCRAP/HP and FUEL phases if True.
# strike_drain_hp_after_scrap: when scrap is empty, remaining damage goes to HP.
p.strike_cooldown_sec = 1.35
p.strike_drain_amount = 2
p.strike_enable_fuel_phase = False
p.strike_drain_hp_after_scrap = True

# Strike gate.
# strike_begin_dist_s: desired strike start distance.
# strike_min_speed: minimal player speed required for strikes (0 = always).
# follow_gap_s: hard minimum distance between pursuer and player.
# NOTE: keep strike_begin_dist_s >= follow_gap_s to avoid unreachable strike range.
p.strike_begin_dist_s = 11.0
p.strike_min_speed = 0.0
p.follow_gap_s = 10.0

# Anti-chase event pushback (used after boost-zone transition).
p.boost_pushback_s = 22.0

# Body size (Entity uses dedicated compact renderer).
p.body_radius_chase = 6.0
p.body_radius_near = 8.0

# Debug.
# Shows logical contact point marker to tune contact_offset_s.
p.debug_contact_marker = True

# Hit FX intensity.
p.strike_shake_intensity = 12.0

# Screen FX.
p.near_vignette = 0.12
p.near_noise = 0.25
p.contact_noise_mult = 5.0
p.strike_noise_boost = 10.0
p.strike_meltdown_intensity = 0.5
p.strike_flash_seconds = 0.22
