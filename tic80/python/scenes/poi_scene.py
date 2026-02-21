from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import btnp, cls, print

    from ..contracts import (
        DriveEnterParams,
        ResultEnterParams,
        SceneEnterParams,
        SceneNavigator
    )
    from ..core.input_buttons import Button
    from ..core.palette import Color
    from ..core.run_state import EscapeOutcome, PoiAction
    from ..core.scene_ids import SceneId
    from ..data.tuning import TUNING
    from ..systems.drive.pursuers.registry import active_pursuer_name


class PoiScene:
    SCENE_ID = SceneId.POI

    def __init__(self, nav: SceneNavigator) -> None:
        self._nav = nav
        self._state = nav.state
        self.timer = TUNING.POI.timer_seconds
        self._loot_summary_active = False
        self._loot_scrap = 0
        self._loot_fuel = 0
        self._pursuer_name = active_pursuer_name()

    def enter(self, params: SceneEnterParams = None) -> None:
        self.timer = TUNING.POI.timer_seconds
        self._loot_summary_active = False
        self._loot_scrap = 0
        self._loot_fuel = 0
        self._pursuer_name = active_pursuer_name()

    def _poi_type_label(self, poi_type: str) -> str:
        if poi_type == "gas_station":
            return "GAS STATION"
        if poi_type == "scrapyard":
            return "SCRAPYARD"
        if poi_type == "depot":
            return "DEPOT"
        return str(poi_type).upper()

    def _leave(
        self,
        action: PoiAction,
        escape_outcome: EscapeOutcome | None = None,
        go_result: bool = False,
        message: str | None = None
    ) -> None:
        run = self._state.require_run()
        delta = run.ensure_delta(run.node_id)
        delta.set_poi_action(action)
        if escape_outcome is not None:
            delta.set_escape_outcome(escape_outcome)

        if go_result:
            if message is None:
                message = "POI FAILED"
            self._nav.go(SceneId.RESULT, ResultEnterParams(message))
            return

        run.ensure_return_from_active_outbound()
        self._nav.go(SceneId.DRIVE, DriveEnterParams("extract"))

    def _start_loot_summary(self) -> None:
        run = self._state.require_run()
        delta = run.ensure_delta(run.node_id)
        delta.set_poi_action("loot")

        self._loot_scrap = 0
        self._loot_fuel = 0
        segment = run.active_segment
        if segment is not None:
            rewards = segment.rewards
            self._loot_scrap = max(0, int(rewards.scrap))
            self._loot_fuel = max(0, int(rewards.fuel))
            if self._loot_scrap > 0:
                item = run.add_item("scrap", self._loot_scrap)
                delta.add_item_gained(item)
            if self._loot_fuel > 0:
                run.add_fuel(self._loot_fuel)
                delta.add_fuel_gained(self._loot_fuel)

        self._loot_summary_active = True

    def update(self, dt: float) -> None:
        if self._loot_summary_active:
            if btnp(Button.A):
                self._leave("loot")
            return

        self.timer = max(0.0, self.timer - dt)
        if btnp(Button.A):
            self._start_loot_summary()
        elif btnp(Button.B):
            self._leave("leave")
        elif self.timer <= 0.0:
            self._leave("timeout", "fail", True, "POI TIMEOUT")

    def draw(self) -> None:
        cls(Color.BLACK)
        if self._loot_summary_active:
            print("LOOT SECURED", 78, 24, Color.WHITE)
            print("you took what wasn't yours", 42, 40, Color.LIGHT_GREY)
            print("stolen scrap +" + str(self._loot_scrap),
                  58, 56, Color.LIGHT_GREEN)
            print("stolen fuel  +" + str(self._loot_fuel), 58, 64, Color.YELLOW)
            print(self._pursuer_name + " is in pursuit", 44, 82, Color.RED)
            print("return to base immediately", 46, 90, Color.WHITE)
            print("Z = BEGIN RETURN", 74, 112, Color.WHITE)
            return

        print("POI", 112, 30, Color.WHITE)
        print("timer=" + f"{self.timer:.2f}", 82, 50, Color.WHITE)
        run = self._state.run
        if run is not None:
            print("inv=" + str(run.inventory_count()), 98, 60, Color.WHITE)
            segment = run.active_segment
            if segment is not None:
                rewards = segment.rewards
                print("type=" + self._poi_type_label(segment.poi_type),
                      74, 68, Color.WHITE)
                print("reward: +" + str(rewards.scrap) + " scrap, +" +
                      str(rewards.fuel) + " fuel", 40, 76, Color.WHITE)
        print("Z = LOOT", 90, 96, Color.WHITE)
        print("X = LEAVE", 88, 104, Color.WHITE)

    def exit(self) -> None:
        pass


def make_poi_scene(nav: SceneNavigator) -> PoiScene:
    return PoiScene(nav)
