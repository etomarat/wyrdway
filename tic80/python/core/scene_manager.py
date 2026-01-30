from typing import (
    TYPE_CHECKING,
    Callable,
    Dict,
    Literal,
    Optional,
    Protocol,
    overload
)

if TYPE_CHECKING:
    from tic80 import *  # noqa: F403

    from ..contracts import DriveEnterParams, ResultEnterParams
    from .game_state import GameState
    from .scene_base import Scene
    from .scene_ids import SceneId


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


class SceneManager(SceneNavigator):
    """Replace-mode менеджер сцен: в каждый момент активна одна сцена."""

    def __init__(self) -> None:
        self.state = GameState()
        self._scenes: Dict[str, SceneFactory] = {}
        self._current_scene_id: Optional[str] = None
        self._current_scene: Optional[Scene] = None

    def register(self, scene_id: str, factory: SceneFactory) -> None:
        self._scenes[scene_id] = factory

    @overload
    def go(self, scene_id: SceneKeyDrive,
           params: DriveEnterParams) -> None: ...

    @overload
    def go(self, scene_id: SceneKeyResult,
           params: ResultEnterParams) -> None: ...

    @overload
    def go(self, scene_id: SceneKeyNoParams, params: None = None) -> None: ...

    def go(self, scene_id: str, params: object | None = None) -> None:
        if scene_id not in self._scenes:
            return

        if scene_id == SceneId.DRIVE:
            if not isinstance(params, DriveEnterParams):
                raise TypeError("DRIVE scene requires DriveEnterParams")
        elif scene_id == SceneId.RESULT:
            if not isinstance(params, ResultEnterParams):
                raise TypeError("RESULT scene requires ResultEnterParams")
        else:
            if params is not None:
                raise TypeError(f"{scene_id} does not accept params")

        next_scene = self._scenes[scene_id](self)

        if self._current_scene is not None:
            self._current_scene.exit()

        self._current_scene_id = scene_id
        self._current_scene = next_scene
        next_scene.enter(params)

    def update(self, dt: float) -> None:
        if self._current_scene is None:
            return
        self._current_scene.update(dt)

    def draw(self) -> None:
        if self._current_scene is None:
            return
        self._current_scene.draw()

    @property
    def current_id(self) -> Optional[str]:
        return self._current_scene_id
