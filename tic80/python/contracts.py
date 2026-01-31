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
    __slots__ = ("start_money", "start_garage_hp", "start_garage_fuel")

    def __init__(self) -> None:
        self.start_money = 0
        self.start_garage_hp = 0
        self.start_garage_fuel = 0.0


class DriveTuning:
    __slots__ = ("fuel_per_sec",)

    def __init__(self) -> None:
        self.fuel_per_sec = 0.0


class PoiTuning:
    __slots__ = ("timer_seconds",)

    def __init__(self) -> None:
        self.timer_seconds = 0.0


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
    __slots__ = ("mode",)

    def __init__(self, mode: DriveMode) -> None:
        self.mode = mode


class ResultEnterParams:
    __slots__ = ("text",)

    def __init__(self, text: str) -> None:
        self.text = text


PoiAction = Literal["loot", "leave", "timeout"]
EscapeOutcome = Literal["ok", "fail"]


class RunItem:
    __slots__ = ("id", "qty")

    def __init__(self, item_id: str, qty: int) -> None:
        self.id = item_id
        self.qty = qty


class SegmentDelta:
    __slots__ = ("node_id", "poi_action", "items_gained", "escape_outcome")

    def __init__(self, node_id: int | None) -> None:
        self.node_id = node_id
        self.poi_action: PoiAction | None = None
        self.items_gained: list[RunItem] = []
        self.escape_outcome: EscapeOutcome | None = None


class Profile:
    __slots__ = ("money", "garage_hp", "garage_fuel", "upgrades")

    def __init__(self, money: int, garage_hp: int, garage_fuel: float) -> None:
        self.money = money
        self.garage_hp = garage_hp
        self.garage_fuel = garage_fuel
        self.upgrades: list[str] = []


class RunState:
    __slots__ = ("seed", "node_id", "car_hp", "car_fuel", "inventory", "delta")

    def __init__(self, seed: int, car_hp: int, car_fuel: float) -> None:
        self.seed = seed
        self.node_id: int | None = None
        self.car_hp = car_hp
        self.car_fuel = car_fuel
        self.inventory: list[RunItem] = []
        self.delta: SegmentDelta | None = None


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
    state: GameState

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
