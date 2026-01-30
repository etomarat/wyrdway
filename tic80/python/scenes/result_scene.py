from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import btnp, cls, print

    from ..contracts import ResultEnterParams
    from ..core.input_buttons import Button
    from ..core.scene_ids import SceneId
    from ..core.scene_manager import SceneNavigator


class ResultScene:
    def __init__(self, nav: "SceneNavigator") -> None:
        self._nav = nav
        self.text = "RESULT: OK"

    def enter(self, params: object | None = None) -> None:
        if not isinstance(params, ResultEnterParams):
            raise TypeError("ResultScene.enter expects ResultEnterParams")
        self.text = params.text

    def update(self, dt: float) -> None:
        if btnp(Button.A):
            self._nav.go(SceneId.GARAGE)

    def draw(self) -> None:
        cls(0)
        print("RESULT", 100, 40, 12)
        print(self.text, 72, 60, 12)
        print("A = BACK", 90, 80, 12)

    def exit(self) -> None:
        pass


def make_result_scene(nav: "SceneNavigator") -> "ResultScene":
    return ResultScene(nav)
