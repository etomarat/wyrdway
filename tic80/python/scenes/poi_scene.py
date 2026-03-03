from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import cls

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
    from ..core.ui.overlay_flow import (
        ui_overlay_flow_confirm_cancel,
        ui_overlay_flow_single_action
    )
    from ..core.ui.overlay_layout import ui_overlay_layout_centered_by_spec
    from ..core.ui.overlay_runtime import UiOverlayRuntime
    from ..core.ui.overlay_screen import ui_overlay_screen_draw
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
    OVERLAY_W = 220
    OVERLAY_H = 112
    OVERLAY_HEADER_TEXT_OFFSET_Y = 9
    OVERLAY_BODY_TOP_OFFSET_Y = 24
    OVERLAY_LAYOUT_SPEC = (
        OVERLAY_W,
        OVERLAY_H,
        OVERLAY_HEADER_TEXT_OFFSET_Y,
        OVERLAY_BODY_TOP_OFFSET_Y
    )

    def __init__(self, nav: SceneNavigator) -> None:
        self._nav = nav
        self._state = nav.state
        self._ui = UiOverlayRuntime()
        self.timer = TUNING.POI.timer_seconds
        self._loot_scrap = 0
        self._loot_fuel = 0
        self._pursuer_name = active_pursuer_name()
        self._pursuer_name_color = active_pursuer_name_color()
        self._mode = self.MODE_INTERACT

    def enter(self, params: SceneEnterParams = None) -> None:
        self._ui.sync_actions(
            self._state.controls,
            [Action.CONFIRM, Action.CANCEL]
        )
        self._ui.reset_footer()
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

    def _interact_lines(self) -> list[tuple[str, int]]:
        timer_line = "TIME LEFT: " + f"{self.timer:.1f}" + "s"
        poi_line = "SITE: UNKNOWN"
        reward_line = "LOOT: +0 SCRAP / +0 FUEL"
        run = self._state.run
        if run is not None:
            segment = run.active_segment
            if segment is not None:
                rewards = segment.rewards
                poi_line = "SITE: " + poi_type_label(segment.poi_type).upper()
                reward_line = (
                    "LOOT: +"
                    + str(rewards.scrap)
                    + " SCRAP / +"
                    + str(rewards.fuel)
                    + " FUEL"
                )
        pursuer_line = "PURSUER: " + str(self._pursuer_name)
        return [
            ("ROADSIDE STOP // TEMP", Color.WHITE),
            ("FINAL POI GAMEPLAY COMING LATER", Color.LIGHT_GREY),
            ("", Color.WHITE),
            (timer_line, Color.YELLOW),
            (poi_line, Color.WHITE),
            (reward_line, Color.LIGHT_GREY),
            (pursuer_line, self._pursuer_name_color),
            ("TIMER EXPIRY FAILS THE RUN", Color.ORANGE)
        ]

    def _summary_lines(
        self,
        subtitle: str,
        scrap_line: str,
        fuel_line: str,
        pursuit_suffix: str
    ) -> list[tuple[str, int]]:
        pursuit_line = str(self._pursuer_name) + pursuit_suffix
        return [
            (subtitle, Color.LIGHT_GREY),
            ("", Color.WHITE),
            (scrap_line, Color.LIGHT_GREEN),
            (fuel_line, Color.YELLOW),
            (pursuit_line, Color.RED),
            ("RETURN TO BASE IMMEDIATELY", Color.WHITE)
        ]

    def _draw_overlay(
        self,
        title: str,
        title_color: int,
        lines: list[tuple[str, int]],
        slots: list[str],
        keyboard_active: list[bool]
    ) -> None:
        layout = ui_overlay_layout_centered_by_spec(
            self.OVERLAY_LAYOUT_SPEC,
            len(slots),
            tuple([1] * len(slots)),
            0,
            0,
            len(slots) - 1
        )
        ui_overlay_screen_draw(
            self._ui,
            layout,
            title,
            lines,
            slots,
            keyboard_active,
            title_color=title_color
        )

    def _update_interact(self, dt: float, confirm_released: bool, cancel_released: bool) -> None:
        self.timer = max(0.0, self.timer - dt)
        if confirm_released:
            self._start_loot_summary()
            self._ui.reset_footer()
            return
        if cancel_released:
            self._start_leave_summary()
            self._ui.reset_footer()
            return
        if self.timer <= 0.0:
            self._ui.reset_footer()
            self._leave("timeout", True, "POI TIMEOUT")

    def update(self, dt: float) -> None:
        self._ui.poll_mouse()
        confirm_released = self._ui.poll_action(self._state.controls, Action.CONFIRM)
        cancel_released = self._ui.poll_action(self._state.controls, Action.CANCEL)
        if self._mode == self.MODE_LOOT_SUMMARY:
            layout, slots, slot_confirm = ui_overlay_flow_single_action(
                self.OVERLAY_LAYOUT_SPEC,
                self._state,
                Action.CONFIRM,
                "BEGIN RETURN"
            )
            released_slot = self._ui.poll_footer_release(layout, slots)
            if confirm_released or released_slot == slot_confirm:
                self._ui.reset_footer()
                self._leave("loot")
            return
        if self._mode == self.MODE_LEAVE_SUMMARY:
            layout, slots, slot_confirm = ui_overlay_flow_single_action(
                self.OVERLAY_LAYOUT_SPEC,
                self._state,
                Action.CONFIRM,
                "BEGIN RETURN"
            )
            released_slot = self._ui.poll_footer_release(layout, slots)
            if confirm_released or released_slot == slot_confirm:
                self._ui.reset_footer()
                self._leave("leave")
            return

        layout, slots, slot_confirm, slot_cancel = ui_overlay_flow_confirm_cancel(
            self.OVERLAY_LAYOUT_SPEC,
            self._state,
            Action.CONFIRM,
            Action.CANCEL,
            "LOOT",
            "LEAVE"
        )
        released_slot = self._ui.poll_footer_release(layout, slots)
        self._update_interact(
            dt,
            confirm_released or released_slot == slot_confirm,
            cancel_released or released_slot == slot_cancel
        )

    def draw(self) -> None:
        cls(Color.BLACK)
        if self._mode == self.MODE_LEAVE_SUMMARY:
            _layout, slots, _slot_confirm = ui_overlay_flow_single_action(
                self.OVERLAY_LAYOUT_SPEC,
                self._state,
                Action.CONFIRM,
                "BEGIN RETURN"
            )
            self._draw_overlay(
                "RETREAT CONFIRMED",
                Color.YELLOW,
                self._summary_lines(
                    "NO LOOT COLLECTED",
                    "SCRAP: +" + str(self._loot_scrap),
                    "FUEL: +" + str(self._loot_fuel),
                    " IS STILL TRACKING YOU"
                ),
                slots,
                [self._state.controls.down(Action.CONFIRM)]
            )
            return
        if self._mode == self.MODE_LOOT_SUMMARY:
            _layout, slots, _slot_confirm = ui_overlay_flow_single_action(
                self.OVERLAY_LAYOUT_SPEC,
                self._state,
                Action.CONFIRM,
                "BEGIN RETURN"
            )
            self._draw_overlay(
                "LOOT SECURED",
                Color.LIGHT_GREEN,
                self._summary_lines(
                    "YOU TOOK WHAT WASN'T YOURS",
                    "STOLEN SCRAP: +" + str(self._loot_scrap),
                    "STOLEN FUEL: +" + str(self._loot_fuel),
                    " IS IN PURSUIT"
                ),
                slots,
                [self._state.controls.down(Action.CONFIRM)]
            )
            return
        _layout, slots, slot_confirm, slot_cancel = ui_overlay_flow_confirm_cancel(
            self.OVERLAY_LAYOUT_SPEC,
            self._state,
            Action.CONFIRM,
            Action.CANCEL,
            "LOOT",
            "LEAVE"
        )
        keyboard_active = [False, False]
        keyboard_active[slot_confirm] = self._state.controls.down(Action.CONFIRM)
        keyboard_active[slot_cancel] = self._state.controls.down(Action.CANCEL)
        self._draw_overlay(
            "POI INTERACTION",
            Color.WHITE,
            self._interact_lines(),
            slots,
            keyboard_active
        )

    def exit(self) -> None:
        pass


def make_poi_scene(nav: SceneNavigator) -> PoiScene:
    return PoiScene(nav)
