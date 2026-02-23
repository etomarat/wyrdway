from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import btnp, cls, print, rect, rectb

    from ..contracts import (
        DriveEnterParams,
        ResultEnterParams,
        SceneEnterParams,
        SceneNavigator
    )
    from ..core.input_buttons import Button
    from ..core.palette import Color
    from ..core.run_state import PoiAction
    from ..core.scene_ids import SceneId
    from ..core.text_layout import text_center_x, text_width
    from ..data.tuning import TUNING
    from ..systems.drive.pursuers.registry import active_pursuer_name


class PoiScene:
    SCENE_ID = SceneId.POI

    def __init__(self, nav: SceneNavigator) -> None:
        self._nav = nav
        self._state = nav.state
        self.timer = TUNING.POI.timer_seconds
        self._loot_summary_active = False
        self._leave_summary_active = False
        self._loot_scrap = 0
        self._loot_fuel = 0
        self._pursuer_name = active_pursuer_name()

    def enter(self, params: SceneEnterParams = None) -> None:
        self.timer = TUNING.POI.timer_seconds
        self._loot_summary_active = False
        self._leave_summary_active = False
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
        go_result: bool = False,
        message: str | None = None
    ) -> None:
        run = self._state.require_run()
        delta = run.ensure_delta(run.node_id)
        delta.set_poi_action(action)

        if go_result:
            if message is None:
                message = "POI FAILED"
            self._state.rollback_to_last_save(message, False)
            self._nav.go(SceneId.RESULT, ResultEnterParams("RUN FAILED"))
            return

        run.ensure_return_from_active_outbound()
        self._nav.go(SceneId.DRIVE, DriveEnterParams("extract"))

    def _start_leave_summary(self) -> None:
        run = self._state.require_run()
        delta = run.ensure_delta(run.node_id)
        delta.set_poi_action("leave")
        self._leave_summary_active = True

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
        if self._leave_summary_active:
            if btnp(Button.A):
                self._leave("leave")
            return

        self.timer = max(0.0, self.timer - dt)
        if btnp(Button.A):
            self._start_loot_summary()
        elif btnp(Button.B):
            self._start_leave_summary()
        elif self.timer <= 0.0:
            self._leave("timeout", True, "POI TIMEOUT")

    def draw(self) -> None:
        cls(Color.BLACK)
        if self._leave_summary_active:
            line = "RETREAT CONFIRMED"
            print(line, text_center_x(line, margin_x=2), 24, Color.WHITE, True)
            line = "no loot collected"
            print(line, text_center_x(line, margin_x=2),
                  40, Color.LIGHT_GREY, True)
            line = "scrap: +" + str(self._loot_scrap)
            print(line, text_center_x(line, margin_x=2),
                  56, Color.LIGHT_GREEN, True)
            line = "fuel: +" + str(self._loot_fuel)
            print(line, text_center_x(line, margin_x=2), 64, Color.YELLOW, True)
            pursuit_text = self._pursuer_name + " is still tracking you"
            print(pursuit_text, text_center_x(
                pursuit_text, margin_x=2), 82, Color.RED, True)
            line = "return to base immediately"
            print(line, text_center_x(line, margin_x=2), 90, Color.WHITE, True)
            line = "Z = BEGIN RETURN"
            print(line, text_center_x(line, margin_x=2), 112, Color.WHITE, True)
            return
        if self._loot_summary_active:
            line = "LOOT SECURED"
            print(line, text_center_x(line, margin_x=2), 24, Color.WHITE, True)
            line = "you took what wasn't yours"
            print(line, text_center_x(line, margin_x=2),
                  40, Color.LIGHT_GREY, True)
            line = "stolen scrap: +" + str(self._loot_scrap)
            print(line, text_center_x(line, margin_x=2),
                  56, Color.LIGHT_GREEN, True)
            line = "stolen fuel: +" + str(self._loot_fuel)
            print(line, text_center_x(line, margin_x=2), 64, Color.YELLOW, True)
            pursuit_text = self._pursuer_name + " is in pursuit"
            print(pursuit_text, text_center_x(
                pursuit_text, margin_x=2), 82, Color.RED, True)
            line = "return to base immediately"
            print(line, text_center_x(line, margin_x=2), 90, Color.WHITE, True)
            line = "Z = BEGIN RETURN"
            print(line, text_center_x(line, margin_x=2), 112, Color.WHITE, True)
            return

        panel_x = 8
        panel_y = 18
        panel_w = 224
        panel_h = 86
        rect(panel_x, panel_y, panel_w, panel_h, Color.BLACK)
        rect(panel_x + 1, panel_y + 1, panel_w -
             2, panel_h - 2, Color.DARK_GREY)
        rectb(panel_x, panel_y, panel_w, panel_h, Color.GREY)

        line = "ROADSIDE STOP // POI TEMP SCENE"
        print(line, text_center_x(line, margin_x=2), 30, Color.WHITE, True)
        line = "THIS IS A TEMP PLACEHOLDER"
        print(line, text_center_x(line, margin_x=2), 42, Color.LIGHT_GREY, True)
        line = "FINAL POI GAMEPLAY COMING LATER"
        print(line, text_center_x(line, margin_x=2), 50, Color.LIGHT_GREY, True)

        timer_line = "TIME LEFT: " + f"{self.timer:.1f}" + "s"
        print(timer_line, text_center_x(
            timer_line, margin_x=2), 60, Color.YELLOW, True)

        run = self._state.run
        poi_line = "SITE: UNKNOWN"
        reward_line = "+0 SCRAP / +0 FUEL"
        if run is not None:
            segment = run.active_segment
            if segment is not None:
                rewards = segment.rewards
                poi_line = "SITE: " + self._poi_type_label(segment.poi_type)
                reward_line = (
                    "+"
                    + str(rewards.scrap)
                    + " SCRAP / +"
                    + str(rewards.fuel)
                    + " FUEL"
                )
        print(poi_line, text_center_x(
            poi_line, margin_x=2), 72, Color.WHITE, True)
        line = "POTENTIAL LOOT"
        print(line, text_center_x(line, margin_x=2), 82, Color.LIGHT_GREY, True)
        print(reward_line, text_center_x(reward_line,
              margin_x=2), 90, Color.LIGHT_GREY, True)

        rect(8, 108, 224, 20, Color.BLACK)
        rect(9, 109, 222, 18, Color.DARK_GREY)
        rectb(8, 108, 224, 20, Color.GREY)
        rect(120, 109, 1, 18, Color.GREY)
        left_action = "Z: LOOT (TEMP)"
        right_action = "X: LEAVE"
        left_x = 8 + int((112 - text_width(left_action)) * 0.5)
        right_x = 120 + int((112 - text_width(right_action)) * 0.5)
        print(left_action, left_x, 116, Color.WHITE, True)
        print(right_action, right_x, 116, Color.WHITE, True)

    def exit(self) -> None:
        pass


def make_poi_scene(nav: SceneNavigator) -> PoiScene:
    return PoiScene(nav)
