from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import btnp, cls, print

    from ..contracts import DriveEnterParams, SceneNavigator
    from ..core.input_buttons import Button
    from ..core.run_state import PoiAction
    from ..core.scene_ids import SceneId
    from ..data.tuning import TUNING


class PoiScene:
    SCENE_ID = SceneId.POI

    def __init__(self, nav: "SceneNavigator") -> None:
        self._nav = nav
        self._state = nav.state
        self.timer = TUNING.POI.timer_seconds

    def enter(self, params: object | None = None) -> None:
        self.timer = TUNING.POI.timer_seconds

    def _leave(self, action: PoiAction) -> None:
        run = self._state.require_run()
        delta = run.ensure_delta(run.node_id)
        delta.set_poi_action(action)
        if action == "loot":
            item = run.add_item("scrap", TUNING.POI.scrap_per_loot)
            delta.add_item_gained(item)

        self._nav.go(SceneId.DRIVE, DriveEnterParams("extract"))

    def update(self, dt: float) -> None:
        self.timer = max(0.0, self.timer - dt)
        if btnp(Button.A):
            self._leave("loot")
        elif btnp(Button.B):
            self._leave("leave")
        elif self.timer <= 0.0:
            self._leave("timeout")

    def draw(self) -> None:
        cls(0)
        print("POI", 112, 30, 12)
        print("timer=" + str(round(self.timer, 1)), 82, 50, 12)
        run = self._state.run
        if run is not None:
            print("inv=" + str(run.inventory_count()), 98, 60, 12)
        print("A = LOOT", 90, 70, 12)
        print("B = LEAVE", 88, 80, 12)

    def exit(self) -> None:
        pass


def make_poi_scene(nav: "SceneNavigator") -> "PoiScene":
    return PoiScene(nav)
