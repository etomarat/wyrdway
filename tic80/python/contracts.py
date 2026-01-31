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
        "ramp_fraction",
        "max_speed",
        "accel",
        "brake",
        "steer_rate",
        "grip",
        "handbrake_grip_mult",
        "offroad_grip_mult",
        "offroad_slowdown",
        "fuel_per_sec_idle",
        "fuel_per_sec_throttle"
    )

    def __init__(self) -> None:
        self.segment_total_length = 0.0
        self.safe_start_length = 0.0
        self.road_width = 0.0
        self.ds = 0.0
        self.min_piece_length = 0.0
        self.max_piece_length = 0.0
        self.max_curvature = 0.0
        self.ramp_fraction = 0.0
        self.max_speed = 0.0
        self.accel = 0.0
        self.brake = 0.0
        self.steer_rate = 0.0
        self.grip = 0.0
        self.handbrake_grip_mult = 0.0
        self.offroad_grip_mult = 0.0
        self.offroad_slowdown = 0.0
        self.fuel_per_sec_idle = 0.0
        self.fuel_per_sec_throttle = 0.0


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
