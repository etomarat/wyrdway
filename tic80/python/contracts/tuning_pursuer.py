class PursuerTuning:
    __slots__ = (
        "enabled",
        "grace_meters",
        "grace_seconds_cap",
        "start_gap_s",
        "base_speed",
        "slow_catchup",
        "offroad_catchup",
        "show_dist_s",
        "near_dist_s",
        "contact_offset_s",
        "strike_cooldown_sec",
        "strike_drain_amount",
        "strike_begin_dist_s",
        "strike_min_speed",
        "follow_gap_s",
        "boost_pushback_s",
        "body_radius_chase",
        "body_radius_near",
        "debug_contact_marker",
        "strike_shake_intensity",
        "near_vignette",
        "near_noise",
        "contact_noise_mult",
        "strike_noise_boost",
        "strike_meltdown_intensity",
        "strike_flash_seconds"
    )

    def __init__(self) -> None:
        self.enabled = False
        self.grace_meters = 0.0
        self.grace_seconds_cap = 0.0
        self.start_gap_s = 0.0
        self.base_speed = 0.0
        self.slow_catchup = 0.0
        self.offroad_catchup = 0.0
        self.show_dist_s = 0.0
        self.near_dist_s = 0.0
        self.contact_offset_s = 0.0
        self.strike_cooldown_sec = 0.0
        self.strike_drain_amount = 0
        self.strike_begin_dist_s = 0.0
        self.strike_min_speed = 0.0
        self.follow_gap_s = 0.0
        self.boost_pushback_s = 0.0
        self.body_radius_chase = 0.0
        self.body_radius_near = 0.0
        self.debug_contact_marker = False
        self.strike_shake_intensity = 0.0
        self.near_vignette = 0.0
        self.near_noise = 0.0
        self.contact_noise_mult = 0.0
        self.strike_noise_boost = 0.0
        self.strike_meltdown_intensity = 0.0
        self.strike_flash_seconds = 0.0
