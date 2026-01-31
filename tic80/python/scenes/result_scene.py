from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import btnp, cls, print

    from ..contracts import ResultEnterParams
    from ..contracts import SceneNavigator
    from ..core.input_buttons import Button
    from ..core.scene_ids import SceneId


class ResultScene:
    def __init__(self, nav: SceneNavigator) -> None:
        self._nav = nav
        self._state = nav.state
        self._lines: list[str] = ["RESULT: OK"]

    def enter(self, params: object | None = None) -> None:
        fallback = None
        if params is not None:
            if not isinstance(params, ResultEnterParams):
                raise TypeError("ResultScene.enter expects ResultEnterParams")
            fallback = params.text

        run = self._state.run
        if run is None:
            self._lines = ["no run", "msg=" + str(fallback)]
            return

        lines: list[str] = [
            "seed=" + str(run.seed),
            "node=" + str(run.node_id),
            "fuel=" + str(round(run.car_fuel, 1)),
            "inv=" + str(len(run.inventory)),
        ]
        if run.delta is not None:
            lines.append("poi=" + str(run.delta.poi_action))
            lines.append("gained=" + str(len(run.delta.items_gained)))
            lines.append("escape=" + str(run.delta.escape_outcome))
        if fallback is not None:
            lines.append("msg=" + str(fallback))

        self._lines = lines

    def update(self, dt: float) -> None:
        if btnp(Button.A):
            self._state.end_run()
            self._nav.go(SceneId.GARAGE)

    def draw(self) -> None:
        cls(0)
        print("RESULT", 100, 40, 12)
        y = 50
        for line in self._lines:
            print(line, 60, y, 12)
            y += 8
        print("A = BACK", 90, 120, 12)

    def exit(self) -> None:
        pass


def make_result_scene(nav: SceneNavigator) -> "ResultScene":
    return ResultScene(nav)
