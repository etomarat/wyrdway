from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.palette import ColorId

class DriveTuning:
    __slots__ = (
        "segment_total_length",
        "safe_start_length",
        "road_width",
        "ds",
        "min_piece_length",
        "max_piece_length",
        "max_curvature",
        "straight_piece_chance",
        "straight_max_curvature",
        "ramp_fraction",
        "max_speed",
        "feedback_speed_ref",
        "speed_cap",
        "max_reverse_speed",
        "accel",
        "brake",
        "coast_decel",
        "steer_rate",
        "steer_scale_max",
        "steer_scale_min",
        "steer_min_speed",
        "steer_reverse_mult",
        "handbrake_decel",
        "handbrake_decel_min_speed_factor",
        "handbrake_decel_throttle_turn_mult",
        "handbrake_decel_throttle_straight_mult",
        "handbrake_steer_mult",
        "handbrake_steer_min_speed_factor",
        "dash_impulse",
        "dash_cooldown",
        "offroad_steer_mult",
        "grip",
        "side_friction",
        "side_slip_speed_mult",
        "handbrake_grip_mult",
        "offroad_grip_mult",
        "side_recovery_mult",
        "side_recovery_max_add",
        "side_recovery_min_speed_factor",
        "offroad_drag_lin",
        "offroad_drag_quad",
        "offroad_fuel_mult",
        "offroad_damage_per_sec",
        "offroad_damage_min_speed",
        "drag_lin",
        "drag_quad",
        "fuel_per_sec_idle",
        "fuel_per_sec_throttle",
        "view_center_y",
        "view_center_y_min",
        "view_center_y_max",
        "cam_vel_min_speed",
        "cam_vel_full_speed",
        "cam_vel_dir_lerp",
        "cam_spring_freq_hz",
        "cam_spring_damping",
        "cam_low_speed_cap_blend_max",
        "cam_low_speed_yaw_rate_min_deg",
        "cam_low_speed_yaw_rate_max_deg",
        "shake_max_px",
        "shake_offroad_strength",
        "shake_offroad_ramp_up",
        "shake_offroad_ramp_down",
        "shake_offroad_freq_hz",
        "shake_hit_strength",
        "shake_hit_impact_mult",
        "shake_hit_trauma_max",
        "shake_hit_decay_per_sec",
        "shake_hit_freq_hz",
        "shake_hit_smooth_rate",
        "shake_exhaust_strength",
        "shake_exhaust_ramp_up",
        "shake_exhaust_ramp_down",
        "shake_exhaust_freq_hz",
        "shake_exhaust_smooth_rate",
        "shake_exhaust_pulse_strength",
        "shake_exhaust_pulse_chance_per_sec",
        "shake_exhaust_pulse_decay_per_sec",
        "shake_exhaust_pulse_freq_hz",
        "shake_exhaust_pulse_smooth_rate",
        "car_sprite_anchor_x",
        "car_sprite_anchor_y",
        "debug_vectors_enabled",
        "debug_vectors_heading_len",
        "debug_vectors_vel_scale",
        "debug_vectors_accel_scale",
        "debug_hitboxes_enabled",
        "hitbox_rear_px",
        "hitbox_rear_py",
        "hitbox_rear_radius",
        "hitbox_front_px",
        "hitbox_front_py",
        "hitbox_front_radius",
        "render_back_s",
        "render_forward_s",
        "telemetry_enabled",
        "telemetry_every_frames",
        "telemetry_max_lines",
        "obstacles_per_100m",
        "zones_per_100m",
        "spawn_min_distance_between",
        "spawn_min_distance_from_edges",
        "obstacle_radius_min",
        "obstacle_radius_max",
        "obstacle_radius_weights",
        "obstacle_render_range_s",
        "obstacle_damage_base",
        "obstacle_damage_impact_mult",
        "obstacle_damage_min_impact",
        "obstacle_damage_max",
        "zone_radius",
        "zone_length",
        "zone_chevron_length",
        "zone_chevron_gap",
        "zone_grip_mult",
        "zone_grip_floor",
        "zone_boost_forward_accel",
        "zone_boost_center_accel",
        "zone_antislip",
        "slip_eps_speed",
        "skid_slip_threshold",
        "skid_min_speed",
        "skid_back_px",
        "skid_wheel_dx_px",
        "skid_seg_len_px",
        "skid_life_frames",
        "skid_light_after_frames",
        "skid_slant_scale",
        "skid_slant_max",
        "fx_start_id",
        "fx_hit_id",
        "fx_particles_max",
        "fx_start_dust_color_a",
        "fx_start_dust_color_b",
        "fx_offroad_dust_color_a",
        "fx_offroad_dust_color_b",
        "fx_start_dust_seconds",
        "start_skid_seconds",
        "fx_dust_life_frames",
        "fx_dust_len_px",
        "fx_dust_rate_start",
        "fx_dust_rate_offroad",
        "fx_dust_min_speed",
        "fx_dust_wheel_dx_px",
        "fx_dust_back_px",
        "fx_transition_sparks_wheel_dx_px",
        "fx_transition_sparks_back_px",
        "fx_transition_sparks_wheelbase_px",
        "fx_transition_sparks_min_speed",
        "fx_transition_sparks_ramp_speed",
        "fx_transition_cooldown_seconds",
        "fx_dust_jitter_x_px",
        "fx_dust_jitter_y_px",
        "fx_dust_spread_vx",
        "fx_dust_spread_vy",
        "fx_start_move_min_speed",
        "fx_exhaust_min_speed_factor",
        "fx_exhaust_ramp_speed_factor",
        "fx_exhaust_rate",
        "fx_exhaust_dx_px",
        "fx_exhaust_dy_px",
        "fx_exhaust_r_min",
        "fx_exhaust_r_max",
        "fx_exhaust_color_a",
        "fx_exhaust_color_b"
    )

    def __init__(self) -> None:
        self.segment_total_length = 0.0
        self.safe_start_length = 0.0
        self.road_width = 0.0
        self.ds = 0.0
        self.min_piece_length = 0.0
        self.max_piece_length = 0.0
        self.max_curvature = 0.0
        self.straight_piece_chance = 0.0
        self.straight_max_curvature = 0.0
        self.ramp_fraction = 0.0
        self.max_speed = 0.0
        self.feedback_speed_ref = 0.0
        self.speed_cap = 0.0
        self.max_reverse_speed = 0.0
        self.accel = 0.0
        self.brake = 0.0
        self.coast_decel = 0.0
        self.steer_rate = 0.0
        self.steer_scale_max = 0.0
        self.steer_scale_min = 0.0
        self.steer_min_speed = 0.0
        self.steer_reverse_mult = 0.0
        self.handbrake_decel = 0.0
        self.handbrake_decel_min_speed_factor = 0.0
        self.handbrake_decel_throttle_turn_mult = 0.0
        self.handbrake_decel_throttle_straight_mult = 0.0
        self.handbrake_steer_mult = 0.0
        self.handbrake_steer_min_speed_factor = 0.0
        self.dash_impulse = 0.0
        self.dash_cooldown = 0.0
        self.offroad_steer_mult = 0.0
        self.grip = 0.0
        self.side_friction = 0.0
        self.side_slip_speed_mult = 0.0
        self.handbrake_grip_mult = 0.0
        self.offroad_grip_mult = 0.0
        self.side_recovery_mult = 0.0
        self.side_recovery_max_add = 0.0
        self.side_recovery_min_speed_factor = 0.0
        self.offroad_drag_lin = 0.0
        self.offroad_drag_quad = 0.0
        self.offroad_fuel_mult = 0.0
        self.offroad_damage_per_sec = 0.0
        self.offroad_damage_min_speed = 0.0
        self.drag_lin = 0.0
        self.drag_quad = 0.0
        self.fuel_per_sec_idle = 0.0
        self.fuel_per_sec_throttle = 0.0
        self.view_center_y = 0.0
        self.view_center_y_min = 0.0
        self.view_center_y_max = 0.0
        self.cam_vel_min_speed = 0.0
        self.cam_vel_full_speed = 0.0
        self.cam_vel_dir_lerp = 0.0
        self.cam_spring_freq_hz = 0.0
        self.cam_spring_damping = 0.0
        self.cam_low_speed_cap_blend_max = 0.0
        self.cam_low_speed_yaw_rate_min_deg = 0.0
        self.cam_low_speed_yaw_rate_max_deg = 0.0
        self.shake_max_px = 0.0
        self.shake_offroad_strength = 0.0
        self.shake_offroad_ramp_up = 0.0
        self.shake_offroad_ramp_down = 0.0
        self.shake_offroad_freq_hz = 0.0
        self.shake_hit_strength = 0.0
        self.shake_hit_impact_mult = 0.0
        self.shake_hit_trauma_max = 0.0
        self.shake_hit_decay_per_sec = 0.0
        self.shake_hit_freq_hz = 0.0
        self.shake_hit_smooth_rate = 0.0
        self.shake_exhaust_strength = 0.0
        self.shake_exhaust_ramp_up = 0.0
        self.shake_exhaust_ramp_down = 0.0
        self.shake_exhaust_freq_hz = 0.0
        self.shake_exhaust_smooth_rate = 0.0
        self.shake_exhaust_pulse_strength = 0.0
        self.shake_exhaust_pulse_chance_per_sec = 0.0
        self.shake_exhaust_pulse_decay_per_sec = 0.0
        self.shake_exhaust_pulse_freq_hz = 0.0
        self.shake_exhaust_pulse_smooth_rate = 0.0
        self.car_sprite_anchor_x = 0.0
        self.car_sprite_anchor_y = 0.0
        self.debug_vectors_enabled = False
        self.debug_vectors_heading_len = 0.0
        self.debug_vectors_vel_scale = 0.0
        self.debug_vectors_accel_scale = 0.0
        self.debug_hitboxes_enabled = False
        self.hitbox_rear_px = 0.0
        self.hitbox_rear_py = 0.0
        self.hitbox_rear_radius = 0.0
        self.hitbox_front_px = 0.0
        self.hitbox_front_py = 0.0
        self.hitbox_front_radius = 0.0
        self.render_back_s = 0.0
        self.render_forward_s = 0.0
        self.telemetry_enabled = False
        self.telemetry_every_frames = 0
        self.telemetry_max_lines = 0
        self.obstacles_per_100m = 0.0
        self.zones_per_100m = 0.0
        self.spawn_min_distance_between = 0.0
        self.spawn_min_distance_from_edges = 0.0
        self.obstacle_radius_min = 0.0
        self.obstacle_radius_max = 0.0
        self.obstacle_radius_weights: list[float] = []
        self.obstacle_render_range_s = 0.0
        self.obstacle_damage_base = 0.0
        self.obstacle_damage_impact_mult = 0.0
        self.obstacle_damage_min_impact = 0.0
        self.obstacle_damage_max = 0.0
        self.zone_radius = 0.0
        self.zone_length = 0.0
        self.zone_chevron_length = 0.0
        self.zone_chevron_gap = 0.0
        self.zone_grip_mult = 0.0
        self.zone_grip_floor = 0.0
        self.zone_boost_forward_accel = 0.0
        self.zone_boost_center_accel = 0.0
        self.zone_antislip = 0.0
        self.slip_eps_speed = 0.0
        self.skid_slip_threshold = 0.0
        self.skid_min_speed = 0.0
        self.skid_back_px = 0.0
        self.skid_wheel_dx_px = 0.0
        self.skid_seg_len_px = 0.0
        self.skid_life_frames = 0
        self.skid_light_after_frames = 0
        self.skid_slant_scale = 0.0
        self.skid_slant_max = 0.0
        self.fx_start_id = 0
        self.fx_hit_id = 0
        self.fx_particles_max = 0
        self.fx_start_dust_color_a: ColorId = 0
        self.fx_start_dust_color_b: ColorId = 0
        self.fx_offroad_dust_color_a: ColorId = 0
        self.fx_offroad_dust_color_b: ColorId = 0
        self.fx_start_dust_seconds = 0.0
        self.start_skid_seconds = 0.0
        self.fx_dust_life_frames = 0
        self.fx_dust_len_px = 0.0
        self.fx_dust_rate_start = 0.0
        self.fx_dust_rate_offroad = 0.0
        self.fx_dust_min_speed = 0.0
        self.fx_dust_wheel_dx_px = 0.0
        self.fx_dust_back_px = 0.0
        self.fx_transition_sparks_wheel_dx_px = 0.0
        self.fx_transition_sparks_back_px = 0.0
        self.fx_transition_sparks_wheelbase_px = 0.0
        self.fx_transition_sparks_min_speed = 0.0
        self.fx_transition_sparks_ramp_speed = 0.0
        self.fx_transition_cooldown_seconds = 0.0
        self.fx_dust_jitter_x_px = 0.0
        self.fx_dust_jitter_y_px = 0.0
        self.fx_dust_spread_vx = 0.0
        self.fx_dust_spread_vy = 0.0
        self.fx_start_move_min_speed = 0.0
        self.fx_exhaust_min_speed_factor = 0.0
        self.fx_exhaust_ramp_speed_factor = 0.0
        self.fx_exhaust_rate = 0.0
        self.fx_exhaust_dx_px = 0.0
        self.fx_exhaust_dy_px = 0.0
        self.fx_exhaust_r_min = 0.0
        self.fx_exhaust_r_max = 0.0
        self.fx_exhaust_color_a: ColorId = 0
        self.fx_exhaust_color_b: ColorId = 0
