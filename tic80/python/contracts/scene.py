from typing import TYPE_CHECKING, Callable, Literal, Protocol, overload

if TYPE_CHECKING:
    from ..core.game_state import GameState


DriveMode = Literal["travel", "extract"]


class DriveEnterParams:
    __slots__ = ("_mode",)

    def __init__(self, mode: DriveMode) -> None:
        self._mode: DriveMode = mode

    @property
    def mode(self) -> DriveMode:
        return self._mode


class ResultEnterParams:
    __slots__ = ["_text"]

    def __init__(self, text: str) -> None:
        self._text = text

    @property
    def text(self) -> str:
        return self._text


SceneEnterParams = DriveEnterParams | ResultEnterParams | None


class Scene(Protocol):
    """Контракт сцены в режиме Replace: одна активная сцена за кадр."""

    def enter(self, params: SceneEnterParams = None) -> None: ...

    def update(self, dt: float) -> None: ...

    def draw(self) -> None: ...

    def exit(self) -> None: ...


SceneKeyNoParams = Literal["GARAGE", "REGION_MAP", "POI", "DRIVE_PRESET"]
SceneKeyDrive = Literal["DRIVE"]
SceneKeyResult = Literal["RESULT"]


class SceneNavigator(Protocol):
    @property
    def state(self) -> GameState: ...

    @overload
    def go(self, scene_id: SceneKeyDrive, params: DriveEnterParams) -> None: ...

    @overload
    def go(self, scene_id: SceneKeyResult, params: ResultEnterParams) -> None: ...

    @overload
    def go(self, scene_id: SceneKeyNoParams, params: None = None) -> None: ...

    def go(self, scene_id: str, params: SceneEnterParams = None) -> None: ...


SceneFactory = Callable[[SceneNavigator], Scene]
