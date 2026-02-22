from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....contracts import PursuerVariantTuning
    from .common import apply_common_pursuer_profile as apply_common_pursuer_profile


ENTITY_PURSUER_PROFILE = PursuerVariantTuning()

p = ENTITY_PURSUER_PROFILE

# Display name in HUD/briefing.
p.name = "The Entity"

apply_common_pursuer_profile(p)

# Visual alignment.
# contact_offset_s: shifts visual body behind logical contact point.
p.contact_offset_s = 0.0
# intro_entry_screen_y: initial off-screen Y for intro arrival animation (px).
# intro_entry_seconds: intro arrival duration (sec).
p.intro_entry_screen_y = 146.0
p.intro_entry_seconds = 0.45

# Strike cadence and damage model.
# strike_drain_amount: resource loss per strike tick.
p.strike_drain_amount = 2

# Strike gate.
# strike_begin_dist_s: desired strike start distance.
# follow_gap_s: hard minimum distance between pursuer and player.
# NOTE: keep strike_begin_dist_s >= follow_gap_s to avoid unreachable strike range.
p.strike_begin_dist_s = 11.0
p.follow_gap_s = 10.0

# Body size (Entity uses dedicated compact renderer).
p.body_radius_chase = 6.0
p.body_radius_near = 8.0

# Hit FX intensity.
p.strike_shake_intensity = 12.0

# Screen FX.
p.near_vignette = 0.12
p.near_noise = 0.25
p.contact_noise_mult = 5.0
p.strike_noise_boost = 10.0
p.strike_meltdown_intensity = 0.5
