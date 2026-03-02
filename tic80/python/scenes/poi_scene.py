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
    from ..core.ui.overlay_footer import ui_overlay_footer_draw
    from ..core.ui.overlay_layout import OverlayLayout, ui_overlay_layout_centered
    from ..core.ui.overlay_modal import (
        ui_overlay_modal_draw_centered_lines,
        ui_overlay_modal_draw_chrome
    )
    from ..core.ui.prompts import ui_prompt_for_action
    from ..core.ui.prompts import ui_prompt_with_text
    from ..core.ui.release_latch import UiReleaseLatch
    from ..data.tuning import TUNING
    from ..systems.drive.pursuers.registry import (
        active_pursuer_name,
        active_pursuer_name_color
    )
else:
    OverlayLayout = dict


class PoiScene:
    SCENE_ID = SceneId.POI
    MODE_INTERACT = "interact"
    MODE_LOOT_SUMMARY = "loot_summary"
    MODE_LEAVE_SUMMARY = "leave_summary"
    OVERLAY_W = 220
    OVERLAY_H = 112
    OVERLAY_HEADER_TEXT_OFFSET_Y = 9
    OVERLAY_BODY_TOP_OFFSET_Y = 24
    OVERLAY_FOOTER_LINE_OFFSET_Y = 92
    OVERLAY_FOOTER_TEXT_OFFSET_Y = 96

    def __init__(self, nav: SceneNavigator) -> None:
        self._nav = nav
        self._state = nav.state
        self._release = UiReleaseLatch()
        self.timer = TUNING.POI.timer_seconds
        self._loot_scrap = 0
        self._loot_fuel = 0
        self._pursuer_name = active_pursuer_name()
        self._pursuer_name_color = active_pursuer_name_color()
        self._mode = self.MODE_INTERACT

    def enter(self, params: SceneEnterParams = None) -> None:
        self._release.sync_actions_from_controls(
            self._state.controls,
            [Action.CONFIRM, Action.CANCEL]
        )
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

    def _overlay_layout(
        self,
        slot_count: int,
        slot_weights: tuple[int, ...],
        slot_nav: int,
        slot_confirm: int,
        slot_cancel: int
    ) -> OverlayLayout:
        return ui_overlay_layout_centered(
            self.OVERLAY_W,
            self.OVERLAY_H,
            self.OVERLAY_HEADER_TEXT_OFFSET_Y,
            self.OVERLAY_BODY_TOP_OFFSET_Y,
            self.OVERLAY_FOOTER_LINE_OFFSET_Y,
            self.OVERLAY_FOOTER_TEXT_OFFSET_Y,
            slot_count,
            slot_weights,
            slot_nav,
            slot_confirm,
            slot_cancel
        )

    def _draw_overlay(
        self,
        title: str,
        title_color: int,
        lines: list[tuple[str, int]],
        slots: list[str],
        slot_active: list[bool]
    ) -> None:
        layout = self._overlay_layout(
            len(slots),
            tuple([1] * len(slots)),
            0,
            0,
            len(slots) - 1
        )
        box_x, _box_y, box_w, _box_h, body_top, footer_line_y, footer_text_y = ui_overlay_modal_draw_chrome(
            layout,
            title,
            title_color,
            Color.BLACK,
            Color.DARK_GREY,
            Color.BLACK,
            Color.GREY
        )
        ui_overlay_modal_draw_centered_lines(lines, box_x, box_w, body_top, 8)
        ui_overlay_footer_draw(
            layout,
            slots,
            slot_active,
            [False] * len(slots),
            footer_line_y,
            footer_text_y,
            Color.BLACK,
            Color.GREY
        )

    def _update_interact(self, dt: float) -> None:
        confirm_released = self._release.poll(self._state.controls, Action.CONFIRM)
        cancel_released = self._release.poll(self._state.controls, Action.CANCEL)
        self.timer = max(0.0, self.timer - dt)
        if confirm_released:
            self._start_loot_summary()
            return
        if cancel_released:
            self._start_leave_summary()
            return
        if self.timer <= 0.0:
            self._leave("timeout", True, "POI TIMEOUT")

    def update(self, dt: float) -> None:
        if self._mode == self.MODE_LOOT_SUMMARY:
            if self._release.poll(self._state.controls, Action.CONFIRM):
                self._leave("loot")
            return
        if self._mode == self.MODE_LEAVE_SUMMARY:
            if self._release.poll(self._state.controls, Action.CONFIRM):
                self._leave("leave")
            return

        self._update_interact(dt)

    def draw(self) -> None:
        cls(Color.BLACK)
        if self._mode == self.MODE_LEAVE_SUMMARY:
            self._draw_overlay(
                "RETREAT CONFIRMED",
                Color.YELLOW,
                self._summary_lines(
                    "NO LOOT COLLECTED",
                    "SCRAP: +" + str(self._loot_scrap),
                    "FUEL: +" + str(self._loot_fuel),
                    " IS STILL TRACKING YOU"
                ),
                [
                    ui_prompt_with_text(ui_prompt_for_action(self._state, Action.CONFIRM), "BEGIN RETURN")
                ],
                [self._state.controls.down(Action.CONFIRM)]
            )
            return
        if self._mode == self.MODE_LOOT_SUMMARY:
            self._draw_overlay(
                "LOOT SECURED",
                Color.LIGHT_GREEN,
                self._summary_lines(
                    "YOU TOOK WHAT WASN'T YOURS",
                    "STOLEN SCRAP: +" + str(self._loot_scrap),
                    "STOLEN FUEL: +" + str(self._loot_fuel),
                    " IS IN PURSUIT"
                ),
                [
                    ui_prompt_with_text(ui_prompt_for_action(self._state, Action.CONFIRM), "BEGIN RETURN")
                ],
                [self._state.controls.down(Action.CONFIRM)]
            )
            return
        self._draw_overlay(
            "POI INTERACTION",
            Color.WHITE,
            self._interact_lines(),
            [
                ui_prompt_with_text(ui_prompt_for_action(self._state, Action.CONFIRM), "LOOT"),
                ui_prompt_with_text(ui_prompt_for_action(self._state, Action.CANCEL), "LEAVE")
            ],
            [
                self._state.controls.down(Action.CONFIRM),
                self._state.controls.down(Action.CANCEL)
            ]
        )

    def exit(self) -> None:
        pass


def make_poi_scene(nav: SceneNavigator) -> PoiScene:
    return PoiScene(nav)
