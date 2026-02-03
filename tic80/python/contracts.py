from typing import TYPE_CHECKING, Callable, Literal, Protocol, overload

if TYPE_CHECKING:
    from .core.game_state import GameState


class CoreTuning:
    __slots__ = ["dt"]

    def __init__(self) -> None:
        self.dt = 0.0


class DebugTuning:
    __slots__ = ["overlay_default"]

    def __init__(self) -> None:
        self.overlay_default = False


class ProfileTuning:
    __slots__ = (
        "start_scrap",
        "start_garage_hp",
        "start_garage_fuel",
        "repair_cost",
        "repair_hp",
        "evac_fuel_pct",
        "evac_fuel_min",
        "evac_scrap_loss"
    )

    def __init__(self) -> None:
        self.start_scrap = 0
        self.start_garage_hp = 0.0
        self.start_garage_fuel = 0.0
        self.repair_cost = 0
        self.repair_hp = 0.0
        self.evac_fuel_pct = 0.0
        self.evac_fuel_min = 0.0
        self.evac_scrap_loss = 0


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
        "handbrake_decel_throttle_mult",
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
        "offroad_drag_lin",
        "offroad_drag_quad",
        "offroad_fuel_mult",
        "drag_lin",
        "drag_quad",
        "fuel_per_sec_idle",
        "fuel_per_sec_throttle",
        "view_center_y",
        "view_center_y_min",
        "view_center_y_max",
        "car_sprite_anchor_x",
        "car_sprite_anchor_y",
        "car_turn_pose_enabled",
        "debug_vectors_enabled",
        "debug_vectors_heading_len",
        "debug_vectors_vel_scale",
        "debug_vectors_accel_scale",
        "debug_zones_enabled",
        "debug_hitboxes_enabled",
        "hitbox_rear_px",
        "hitbox_rear_py",
        "hitbox_rear_radius",
        "hitbox_front_px",
        "hitbox_front_py",
        "hitbox_front_radius",
        "hitbox_turn_rear_dx",
        "hitbox_turn_rear_dy",
        "hitbox_turn_front_dx",
        "hitbox_turn_front_dy",
        "render_back_s",
        "render_forward_s",
        "telemetry_enabled",
        "telemetry_every_frames",
        "telemetry_max_lines",
        "obstacles_per_100m",
        "zones_per_100m",
        "spawn_min_distance_between",
        "spawn_min_distance_from_edges",
        "obstacle_radius",
        "obstacle_render_range_s",
        "obstacle_hit_damage",
        "zone_radius",
        "zone_length",
        "zone_grip_mult",
        "zone_grip_floor",
        "zone_boost_forward_accel",
        "zone_boost_center_accel",
        "zone_antislip"
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
        self.handbrake_decel_throttle_mult = 0.0
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
        self.offroad_drag_lin = 0.0
        self.offroad_drag_quad = 0.0
        self.offroad_fuel_mult = 0.0
        self.drag_lin = 0.0
        self.drag_quad = 0.0
        self.fuel_per_sec_idle = 0.0
        self.fuel_per_sec_throttle = 0.0
        self.view_center_y = 0.0
        self.view_center_y_min = 0.0
        self.view_center_y_max = 0.0
        self.car_sprite_anchor_x = 0.0
        self.car_sprite_anchor_y = 0.0
        self.car_turn_pose_enabled = False
        self.debug_vectors_enabled = False
        self.debug_vectors_heading_len = 0.0
        self.debug_vectors_vel_scale = 0.0
        self.debug_vectors_accel_scale = 0.0
        self.debug_zones_enabled = False
        self.debug_hitboxes_enabled = False
        self.hitbox_rear_px = 0.0
        self.hitbox_rear_py = 0.0
        self.hitbox_rear_radius = 0.0
        self.hitbox_front_px = 0.0
        self.hitbox_front_py = 0.0
        self.hitbox_front_radius = 0.0
        self.hitbox_turn_rear_dx = 0.0
        self.hitbox_turn_rear_dy = 0.0
        self.hitbox_turn_front_dx = 0.0
        self.hitbox_turn_front_dy = 0.0
        self.render_back_s = 0.0
        self.render_forward_s = 0.0
        self.telemetry_enabled = False
        self.telemetry_every_frames = 0
        self.telemetry_max_lines = 0
        self.obstacles_per_100m = 0.0
        self.zones_per_100m = 0.0
        self.spawn_min_distance_between = 0.0
        self.spawn_min_distance_from_edges = 0.0
        self.obstacle_radius = 0.0
        self.obstacle_render_range_s = 0.0
        self.obstacle_hit_damage = 0.0
        self.zone_radius = 0.0
        self.zone_length = 0.0
        self.zone_grip_mult = 0.0
        self.zone_grip_floor = 0.0
        self.zone_boost_forward_accel = 0.0
        self.zone_boost_center_accel = 0.0
        self.zone_antislip = 0.0


class PoiTuning:
    __slots__ = ("timer_seconds", "scrap_per_loot")

    def __init__(self) -> None:
        self.timer_seconds = 0.0
        self.scrap_per_loot = 0


class Tuning:
    __slots__ = ("tuning_version", "CORE", "DEBUG", "PROFILE", "DRIVE", "POI")

    def __init__(self) -> None:
        self.tuning_version = 0
        self.CORE = CoreTuning()
        self.DEBUG = DebugTuning()
        self.PROFILE = ProfileTuning()
        self.DRIVE = DriveTuning()
        self.POI = PoiTuning()


DriveMode = Literal["travel", "extract"]
DriveVariant = Literal["topdown", "cockpit"]


class DriveEnterParams:
    __slots__ = ("_mode", "_variant")

    def __init__(self, mode: DriveMode, variant: DriveVariant = "topdown") -> None:
        self._mode: DriveMode = mode
        self._variant: DriveVariant = variant

    @property
    def mode(self) -> DriveMode:
        return self._mode

    @property
    def variant(self) -> DriveVariant:
        return self._variant


class ResultEnterParams:
    __slots__ = ["_text"]

    def __init__(self, text: str) -> None:
        self._text = text

    @property
    def text(self) -> str:
        return self._text


class Scene(Protocol):
    """Контракт сцены в режиме Replace: одна активная сцена за кадр."""

    def enter(self, params: object | None = None) -> None: ...

    def update(self, dt: float) -> None: ...

    def draw(self) -> None: ...

    def exit(self) -> None: ...


SceneKeyNoParams = Literal["GARAGE", "REGION_MAP", "POI"]
SceneKeyDrive = Literal["DRIVE"]
SceneKeyResult = Literal["RESULT"]


class SceneNavigator(Protocol):
    @property
    def state(self) -> GameState: ...

    @overload
    def go(self, scene_id: SceneKeyDrive,
           params: DriveEnterParams) -> None: ...

    @overload
    def go(self, scene_id: SceneKeyResult,
           params: ResultEnterParams) -> None: ...

    @overload
    def go(self, scene_id: SceneKeyNoParams, params: None = None) -> None: ...

    def go(self, scene_id: str, params: object | None = None) -> None: ...


SceneFactory = Callable[[SceneNavigator], Scene]
