from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....contracts import PursuerVariantTuning
    from ....core.palette import Color
    from .common import (
        apply_common_pursuer_profile as apply_common_pursuer_profile
    )


PRIME_ENTITY_PURSUER_PROFILE = PursuerVariantTuning()

p = PRIME_ENTITY_PURSUER_PROFILE

# Display name in HUD/briefing.
p.name = "The Prime Entity"
p.name_color = Color.PURPLE

apply_common_pursuer_profile(p)

# Chase kinematics overrides.
p.base_speed = 107.0
# Prime entity should be pushed back less by anti-chase boosters.
p.boost_pushback_s = 10.0

# Visual alignment.
# contact_offset_s: shifts visual body behind logical contact point.
p.contact_offset_s = 32.0
# intro_entry_screen_y: initial off-screen Y for intro arrival animation (px).
# intro_entry_seconds: intro arrival duration (sec).
p.intro_entry_screen_y = 164.0
p.intro_entry_seconds = 0.75

# Strike cadence and damage model.
# strike_drain_amount: resource loss per strike tick.
p.strike_drain_amount = 4

# Strike gate.
# strike_begin_dist_s: desired strike start distance.
# follow_gap_s: hard minimum distance between pursuer and player.
# NOTE: keep strike_begin_dist_s >= follow_gap_s to avoid unreachable strike range.
p.strike_begin_dist_s = 12.0
p.follow_gap_s = 11.0

# Body size in glitch renderer.
p.body_radius_chase = 9.0
p.body_radius_near = 13.0

# Glitch shard cloud around Prime body (visual only).
p.code_shard_radius_inner = 24.0
p.code_shard_radius_outer = 50.0
p.code_shard_up_bias = 0.0
p.code_shard_count_chase = 4
p.code_shard_count_near = 8

# Hit FX intensity.
p.strike_shake_intensity = 24.0

# Screen FX.
p.near_vignette = 0.25
p.near_noise = 0.5
p.contact_noise_mult = 10.0
p.strike_noise_boost = 20.0
p.strike_meltdown_intensity = 1.0
