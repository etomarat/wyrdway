from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import btnp, cls, print

    from ..contracts import DriveEnterParams, ResultEnterParams, SceneNavigator
    from ..core.input_buttons import Button
    from ..core.palette import Color
    from ..core.scene_ids import SceneId


class ResultScene:
    SCENE_ID = SceneId.RESULT

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

        if self._state.playtest_enabled:
            segments, seconds = self._state.playtest_stats()
            playtest_lines: list[str] = [
                "PLAYTEST",
                "segments=" + str(segments),
                "time=" + str(round(seconds, 2)),
                "fuel=" + str(round(run.car_fuel, 2)),
                "hp=" + str(round(run.car_hp, 2))
            ]
            if fallback is not None:
                playtest_lines.append("msg=" + str(fallback))
            self._lines = playtest_lines
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

        self._lines = lines

    def update(self, dt: float) -> None:
        if btnp(Button.A):
            if self._state.playtest_enabled:
                run = self._state.run
                if run is None:
                    return
                # Продолжаем плейтест: переносим текущие значения hp/fuel и стартуем новую дорогу.
                self._state.profile.set_garage_stats(run.car_hp, run.car_fuel)
                self._state.end_run()
                self._state.start_run()
                self._nav.go("DRIVE", DriveEnterParams("travel", "topdown"))
                return
            self._state.apply_run_results()
            self._nav.go(SceneId.GARAGE)

    def draw(self) -> None:
        cls(Color.BLACK)
        print("RESULT", 100, 40, Color.WHITE)
        y = 50
        for line in self._lines:
            print(line, 60, y, Color.WHITE)
            y += 8
        if self._state.playtest_enabled:
            print("Z = NEXT", 92, 120, Color.WHITE)
        else:
            print("Z = CONTINUE", 76, 120, Color.WHITE)

    def exit(self) -> None:
        pass


def make_result_scene(nav: SceneNavigator) -> "ResultScene":
    return ResultScene(nav)
