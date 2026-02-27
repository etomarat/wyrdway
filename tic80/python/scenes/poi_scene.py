from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import cls, print

    from ..contracts import (
        DriveEnterParams,
        ResultEnterParams,
        SceneEnterParams,
        SceneNavigator
    )
    from ..core.controls.actions import Action
    from ..core.palette import Color
    from ..core.poi_text import poi_type_label
    from ..core.run_state import PoiAction
    from ..core.scene_ids import SceneId
    from ..core.text_layout import text_center_x, text_width
    from ..core.ui.panel import ui_panel_draw, ui_panel_draw_split_actions
    from ..core.ui.prompts import ui_prompt_for_action
    from ..core.ui.prompts import ui_prompt_with_text
    from ..core.ui.text import ui_text_center
    from ..data.tuning import TUNING
    from ..systems.drive.pursuers.registry import (
        active_pursuer_name,
        active_pursuer_name_color
    )


class PoiScene:
    SCENE_ID = SceneId.POI
    MODE_INTERACT = "interact"
    MODE_LOOT_SUMMARY = "loot_summary"
    MODE_LEAVE_SUMMARY = "leave_summary"
    INFO_PANEL_X = 8
    INFO_PANEL_Y = 18
    INFO_PANEL_W = 224
    INFO_PANEL_H = 86
    ACTION_PANEL_X = 8
    ACTION_PANEL_Y = 108
    ACTION_PANEL_W = 224
    ACTION_PANEL_H = 20

    def __init__(self, nav: SceneNavigator) -> None:
        self._nav = nav
        self._state = nav.state
        self.timer = TUNING.POI.timer_seconds
        self._loot_scrap = 0
        self._loot_fuel = 0
        self._pursuer_name = active_pursuer_name()
        self._pursuer_name_color = active_pursuer_name_color()
        self._mode = self.MODE_INTERACT

    def enter(self, params: SceneEnterParams = None) -> None:
        self.timer = TUNING.POI.timer_seconds
        self._loot_scrap = 0
        self._loot_fuel = 0
        self._pursuer_name = active_pursuer_name()
        self._pursuer_name_color = active_pursuer_name_color()
        self._mode = self.MODE_INTERACT

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
        self._mode = self.MODE_LEAVE_SUMMARY

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

        self._mode = self.MODE_LOOT_SUMMARY

    def _draw_summary(
        self,
        title: str,
        subtitle: str,
        scrap_line: str,
        fuel_line: str,
        pursuit_suffix: str
    ) -> None:
        ui_text_center(title, 24, Color.WHITE, margin_x=2)
        ui_text_center(subtitle, 40, Color.LIGHT_GREY, margin_x=2)
        ui_text_center(scrap_line, 56, Color.LIGHT_GREEN, margin_x=2)
        ui_text_center(fuel_line, 64, Color.YELLOW, margin_x=2)
        self._draw_pursuit_line(82, pursuit_suffix)
        ui_text_center("return to base immediately", 90, Color.WHITE, margin_x=2)
        prompt = ui_prompt_for_action(self._state, Action.CONFIRM)
        ui_text_center(ui_prompt_with_text(prompt, "BEGIN RETURN"), 112, Color.WHITE, margin_x=2)

    def _draw_pursuit_line(self, y: int, suffix: str) -> None:
        name = str(self._pursuer_name)
        line = name + suffix
        x = text_center_x(line, margin_x=2)
        print(name, x, y, self._pursuer_name_color, True)
        print(suffix, x + text_width(name), y, Color.RED, True)

    def _draw_interact(self) -> None:
        ui_panel_draw(
            self.INFO_PANEL_X,
            self.INFO_PANEL_Y,
            self.INFO_PANEL_W,
            self.INFO_PANEL_H,
            Color.GREY,
            Color.BLACK,
            Color.DARK_GREY
        )

        ui_text_center("ROADSIDE STOP // POI TEMP SCENE", 30, Color.WHITE, margin_x=2)
        ui_text_center("THIS IS A TEMP PLACEHOLDER", 42, Color.LIGHT_GREY, margin_x=2)
        ui_text_center("FINAL POI GAMEPLAY COMING LATER", 50, Color.LIGHT_GREY, margin_x=2)

        timer_line = "TIME LEFT: " + f"{self.timer:.1f}" + "s"
        ui_text_center(timer_line, 60, Color.YELLOW, margin_x=2)

        poi_line = "SITE: UNKNOWN"
        reward_line = "+0 SCRAP / +0 FUEL"
        run = self._state.run
        if run is not None:
            segment = run.active_segment
            if segment is not None:
                rewards = segment.rewards
                poi_line = "SITE: " + poi_type_label(segment.poi_type).upper()
                reward_line = (
                    "+"
                    + str(rewards.scrap)
                    + " SCRAP / +"
                    + str(rewards.fuel)
                    + " FUEL"
                )
        ui_text_center(poi_line, 72, Color.WHITE, margin_x=2)
        ui_text_center("POTENTIAL LOOT", 82, Color.LIGHT_GREY, margin_x=2)
        ui_text_center(reward_line, 90, Color.LIGHT_GREY, margin_x=2)

        ui_panel_draw_split_actions(
            self.ACTION_PANEL_X,
            self.ACTION_PANEL_Y,
            self.ACTION_PANEL_W,
            self.ACTION_PANEL_H,
            ui_prompt_with_text(ui_prompt_for_action(self._state, Action.CONFIRM), "LOOT (TEMP)"),
            ui_prompt_with_text(ui_prompt_for_action(self._state, Action.CANCEL), "LEAVE"),
            Color.GREY,
            Color.WHITE,
            Color.BLACK,
            Color.BLACK
        )

    def _update_interact(self, dt: float) -> None:
        self.timer = max(0.0, self.timer - dt)
        if self._state.controls.pressed(Action.CONFIRM):
            self._start_loot_summary()
            return
        if self._state.controls.pressed(Action.CANCEL):
            self._start_leave_summary()
            return
        if self.timer <= 0.0:
            self._leave("timeout", True, "POI TIMEOUT")

    def update(self, dt: float) -> None:
        if self._mode == self.MODE_LOOT_SUMMARY:
            if self._state.controls.pressed(Action.CONFIRM):
                self._leave("loot")
            return
        if self._mode == self.MODE_LEAVE_SUMMARY:
            if self._state.controls.pressed(Action.CONFIRM):
                self._leave("leave")
            return

        self._update_interact(dt)

    def draw(self) -> None:
        cls(Color.BLACK)
        if self._mode == self.MODE_LEAVE_SUMMARY:
            self._draw_summary(
                "RETREAT CONFIRMED",
                "no loot collected",
                "scrap: +" + str(self._loot_scrap),
                "fuel: +" + str(self._loot_fuel),
                " is still tracking you"
            )
            return
        if self._mode == self.MODE_LOOT_SUMMARY:
            self._draw_summary(
                "LOOT SECURED",
                "you took what wasn't yours",
                "stolen scrap: +" + str(self._loot_scrap),
                "stolen fuel: +" + str(self._loot_fuel),
                " is in pursuit"
            )
            return
        self._draw_interact()

    def exit(self) -> None:
        pass


def make_poi_scene(nav: SceneNavigator) -> PoiScene:
    return PoiScene(nav)
