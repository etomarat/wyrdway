from typing import TYPE_CHECKING, Callable, Literal, Protocol, overload

if TYPE_CHECKING:
    from .core.game_state import GameState


class CoreTuning:
    __slots__ = ("dt",)

    def __init__(self) -> None:
        self.dt = 0.0


class DebugTuning:
    __slots__ = ("overlay_default",)

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
        "evac_scrap_loss",
    )

    def __init__(self) -> None:
        self.start_scrap = 0
        self.start_garage_hp = 0
        self.start_garage_fuel = 0.0
        self.repair_cost = 0
        self.repair_hp = 0
        self.evac_fuel_pct = 0.0
        self.evac_fuel_min = 0.0
        self.evac_scrap_loss = 0


class DriveTuning:
    __slots__ = ("fuel_per_sec", "damage_per_sec", "move_speed", "segment_length")

    def __init__(self) -> None:
        self.fuel_per_sec = 0.0
        self.damage_per_sec = 0.0
        self.move_speed = 0.0
        self.segment_length = 0.0


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


class DriveEnterParams:
    __slots__ = ("_mode",)

    def __init__(self, mode: DriveMode) -> None:
        self._mode: DriveMode = mode

    @property
    def mode(self) -> DriveMode:
        return self._mode


class ResultEnterParams:
    __slots__ = ("_text",)

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
