from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import btnp, cls, print

    from ..contracts import ResultEnterParams, SceneEnterParams, SceneNavigator
    from ..core.input_buttons import Button
    from ..core.palette import Color
    from ..core.scene_ids import SceneId


class ResultScene:
    SCENE_ID = SceneId.RESULT

    def __init__(self, nav: SceneNavigator) -> None:
        self._nav = nav
        self._state = nav.state
        self._lines: list[str] = ["RESULT: OK"]

    def enter(self, params: SceneEnterParams = None) -> None:
        fallback = None
        if params is not None:
            if not isinstance(params, ResultEnterParams):
                raise TypeError("ResultScene.enter expects ResultEnterParams")
            fallback = params.text

        run = self._state.run
        if run is None:
            reason, theseus_gain = self._state.consume_rollback_notice()
            if reason is not None:
                lines = [
                    "status: FAIL",
                    "reason: " + str(reason),
                    "state: rolled back to last save",
                    "theseus gained: +" + str(theseus_gain)
                ]
                self._lines = lines
                return
            if fallback is None:
                self._lines = ["RESULT", "no active run"]
            else:
                self._lines = [str(fallback)]
            return

        gained_scrap = 0
        for item in run.inventory_items():
            if item.id == "scrap":
                gained_scrap += item.qty

        gained_fuel = 0
        poi_action = "-"
        poi_type = "-"
        escaped = "-"
        segment = run.active_segment
        if segment is not None:
            poi_type = str(segment.poi_type)
        if run.delta is not None:
            delta = run.delta
            gained_fuel = delta.fuel_gained
            if delta.poi_action is not None:
                poi_action = str(delta.poi_action)
            if delta.escape_outcome is not None:
                escaped = str(delta.escape_outcome)

        status = "OK"
        if fallback is not None:
            status = str(fallback)
        elif escaped == "fail":
            status = "FAIL"

        lines: list[str] = [
            "status: " + status,
            "poi type: " + poi_type,
            "scrap gained: +" + str(gained_scrap),
            "fuel gained: +" + str(gained_fuel),
            "poi action: " + poi_action
        ]
        if escaped == "fail":
            lines[2] = "scrap gained: +0 (lost)"
            lines.append("scrap lost: " + str(gained_scrap))

        self._lines = lines

    def update(self, dt: float) -> None:
        if btnp(Button.A):
            self._state.apply_run_results()
            self._nav.go(SceneId.GARAGE)

    def draw(self) -> None:
        cls(Color.BLACK)
        print("RESULT", 100, 40, Color.WHITE)
        y = 50
        for line in self._lines:
            print(line, 60, y, Color.WHITE)
            y += 8
        print("Z = CONTINUE", 76, 120, Color.WHITE)

    def exit(self) -> None:
        pass


def make_result_scene(nav: SceneNavigator) -> ResultScene:
    return ResultScene(nav)
