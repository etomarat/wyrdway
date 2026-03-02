from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import cls, line, print, rect, time

    from ..contracts import SceneEnterParams, SceneNavigator
    from ..core.controls.actions import Action
    from ..core.palette import Color
    from ..core.scene_ids import SceneId
    from ..core.ui.footer_slots import (
        ui_footer_slots_confirm_cancel,
        ui_footer_slots_single_action
    )
    from ..core.text_layout import text_center_x, text_width
    from ..core.ui.meter import (
        ui_meter_draw_bar,
        ui_meter_draw_labeled,
        ui_meter_fill_ratio
    )
    from ..core.ui.overlay_footer import ui_overlay_footer_draw
    from ..core.ui.overlay_layout import (
        OverlayLayout,
        ui_overlay_layout_centered
    )
    from ..core.ui.overlay_runtime import UiOverlayRuntime
    from ..core.ui.overlay_modal import (
        ui_overlay_modal_draw_centered_lines,
        ui_overlay_modal_draw_chrome
    )
    from ..core.ui.panel import ui_panel_draw, ui_panel_draw_split_actions
    from ..core.ui.prompts import ui_prompt_for_action
    from ..core.ui.prompts import ui_prompt_with_text
    from ..core.ui.rich_text import ui_rich_print, ui_rich_text_center_x
    from ..data.tuning import TUNING
else:
    OverlayLayout = dict


class GarageScene:
    SCENE_ID = SceneId.GARAGE
    RETURN_HEADER_OPTIONS = [
        "WELCOME BACK // GARAGE LIGHTS ON",
        "WELCOME BACK // HOME GARAGE",
        "WELCOME BACK // YOU MADE IT",
        "WELCOME HOME // SAFEHOUSE",
        "BACK HOME // GARAGE LIGHTS ON"
    ]
    HOME_HEADER_TEXT = RETURN_HEADER_OPTIONS[0]
    VEHICLE_PANEL_X = 8
    VEHICLE_PANEL_Y = 24
    VEHICLE_PANEL_W = 224
    VEHICLE_PANEL_H = 50
    VEHICLE_DIVIDER_X = 154
    VEHICLE_DIVIDER_TOP = 30
    VEHICLE_DIVIDER_BOTTOM = 68
    VEHICLE_LEFT_X = 16
    VEHICLE_RIGHT_X = 162
    VEHICLE_NAME_Y = 29
    VEHICLE_HP_LABEL_Y = 37
    VEHICLE_HP_BAR_Y = 45
    VEHICLE_FUEL_LABEL_Y = 56
    VEHICLE_FUEL_BAR_Y = 63
    VEHICLE_BAR_W = 132
    VEHICLE_METER_BAR_H = 7
    MODAL_W = 188
    MODAL_H = 64
    MODAL_HEADER_TEXT_OFFSET_Y = 9
    MODAL_BODY_TOP_OFFSET_Y = 24
    MODAL_FOOTER_LINE_OFFSET_Y = 50
    MODAL_FOOTER_TEXT_OFFSET_Y = 54

    def __init__(self, nav: SceneNavigator) -> None:
        self._nav = nav
        self._state = nav.state
        self._ui = UiOverlayRuntime()
        self._profile = nav.state.profile
        self._confirm_new_game = False
        self._rollback_modal_open = False
        self._rollback_modal_reason = ""
        self._rollback_modal_gain = 0
        self._header_text = self.HOME_HEADER_TEXT
        self._header_roll = 0

    def enter(self, params: SceneEnterParams = None) -> None:
        self._ui.sync_actions(
            self._state.controls,
            [Action.CONFIRM, Action.CANCEL, Action.SECONDARY, Action.HELP]
        )
        self._ui.reset_footer()
        self._confirm_new_game = False
        reason, gain = self._state.consume_rollback_notice()
        self._rollback_modal_open = reason is not None
        self._rollback_modal_reason = "" if reason is None else str(reason)
        self._rollback_modal_gain = int(gain)
        self._pick_header_text()

    def _pick_header_text(self) -> None:
        if self._state.seed_counter <= 0:
            self._header_text = self.HOME_HEADER_TEXT
            return
        options = self.RETURN_HEADER_OPTIONS
        n = len(options)
        if n <= 0:
            self._header_text = self.HOME_HEADER_TEXT
            return
        self._header_roll += 1
        entropy = (
            int(time())
            + self._header_roll * 17
            + int(self._profile.scrap) * 7
            + int(self._profile.theseus) * 11
        )
        idx = entropy % n
        candidate = options[idx]
        if candidate == self._header_text and n > 1:
            idx = (idx + 1) % n
            candidate = options[idx]
        self._header_text = candidate

    def _repair_hint(self) -> tuple[str, int]:
        hp_max = float(TUNING.PROFILE.start_garage_hp)
        cost = int(TUNING.PROFILE.repair_cost)
        hp = float(self._profile.garage_hp)
        if hp >= hp_max:
            return "HP FULL", Color.LIGHT_GREY
        if self._profile.scrap < cost:
            return "NO SCRAP", Color.ORANGE
        return "READY", Color.LIGHT_GREEN

    def _draw_header_text(self, text: str, y: int, color: int) -> None:
        print(text, text_center_x(text, margin_x=4), y, color, True)

    def _draw_background(self) -> None:
        rect(0, 0, 240, 88, Color.DARK_GREY)
        rect(0, 88, 240, 48, Color.DARK_GREEN)
        y = 20
        while y < 89:
            line(0, y, 239, y, Color.BLACK)
            y += 12
        line(0, 88, 239, 88, Color.GREY)

    def _draw_header(self) -> None:
        rect(0, 0, 240, 15, Color.BLACK)
        line(0, 15, 239, 15, Color.GREY)
        self._draw_header_text(self._header_text, 5, Color.WHITE)

    def _draw_vehicle_panel(self) -> None:
        profile = self._profile
        hp_max = float(TUNING.PROFILE.start_garage_hp)
        fuel_cap = float(TUNING.PROFILE.start_garage_fuel)
        hp = float(profile.garage_hp)
        fuel = float(profile.garage_fuel)
        scrap = int(profile.scrap)
        repair_status, repair_color = self._repair_hint()

        ui_panel_draw(
            self.VEHICLE_PANEL_X,
            self.VEHICLE_PANEL_Y,
            self.VEHICLE_PANEL_W,
            self.VEHICLE_PANEL_H,
            Color.GREY,
            Color.BLACK,
            Color.DARK_GREY
        )
        line(self.VEHICLE_DIVIDER_X, self.VEHICLE_DIVIDER_TOP,
             self.VEHICLE_DIVIDER_X, self.VEHICLE_DIVIDER_BOTTOM, Color.GREY)

        name_x = self.VEHICLE_LEFT_X
        name_y = self.VEHICLE_NAME_Y
        name = "LADA NIVA 4x4"
        trim = " 3-DOOR"
        print(name, name_x, name_y, Color.WHITE)
        print(trim, name_x + text_width(name), name_y, Color.LIGHT_GREY)
        ui_meter_draw_labeled(
            "HP",
            hp,
            hp_max,
            self.VEHICLE_LEFT_X,
            self.VEHICLE_HP_BAR_Y,
            self.VEHICLE_BAR_W,
            self.VEHICLE_METER_BAR_H,
            Color.RED,
            Color.LIGHT_GREY,
            Color.GREY,
            Color.BLACK,
            Color.DARK_GREY
        )
        ui_meter_draw_labeled(
            "FUEL",
            fuel,
            fuel_cap,
            self.VEHICLE_LEFT_X,
            self.VEHICLE_FUEL_BAR_Y,
            self.VEHICLE_BAR_W,
            self.VEHICLE_METER_BAR_H,
            Color.YELLOW,
            Color.LIGHT_GREY,
            Color.GREY,
            Color.BLACK,
            Color.DARK_GREY
        )

        print("SCRAP:", self.VEHICLE_RIGHT_X,
              self.VEHICLE_HP_LABEL_Y, Color.LIGHT_GREY)
        print(str(scrap), self.VEHICLE_RIGHT_X,
              self.VEHICLE_HP_BAR_Y + 1, Color.WHITE)
        print("REPAIR:", self.VEHICLE_RIGHT_X,
              self.VEHICLE_FUEL_LABEL_Y, Color.LIGHT_GREY)
        print(repair_status, self.VEHICLE_RIGHT_X,
              self.VEHICLE_FUEL_BAR_Y + 1, repair_color)

    def _draw_theseus_panel(self) -> None:
        theseus = int(self._profile.theseus)
        cap = 12.0
        ratio = ui_meter_fill_ratio(float(theseus), cap)

        ui_panel_draw(8, 77, 224, 14, Color.LIGHT_BLUE,
                      Color.BLACK, Color.DARK_GREY)
        print("THESEUS", 16, 81, Color.LIGHT_BLUE)

        bar_x = 144
        bar_y = 80
        bar_w = 60
        bar_h = 7
        ui_meter_draw_bar(
            bar_x,
            bar_y,
            bar_w,
            bar_h,
            ratio,
            Color.LIGHT_BLUE,
            Color.GREY,
            Color.BLACK,
            Color.DARK_BLUE
        )
        print(str(theseus), 208, 81, Color.WHITE)

    def _draw_secondary_actions(self) -> None:
        repair_cost = int(TUNING.PROFILE.repair_cost)
        left_label = "REPAIR (-" + str(repair_cost) + " SCRAP)"
        left = ui_prompt_with_text(ui_prompt_for_action(self._state, Action.SECONDARY), left_label)
        right = ui_prompt_with_text(ui_prompt_for_action(self._state, Action.HELP), "NEW GAME")
        ui_panel_draw_split_actions(
            8,
            103,
            224,
            14,
            left,
            right,
            Color.GREY,
            Color.WHITE,
            Color.BLACK,
            Color.BLACK,
            left_width=140,
            left_text_color=Color.YELLOW,
            right_text_color=Color.ORANGE
        )

    def _draw_start_cta(self) -> None:
        # Prompts live on black panels for consistent contrast with glyph sprites.
        ui_panel_draw(6, 119, 228, 14, Color.WHITE, Color.BLACK, Color.BLACK)
        text = ui_prompt_with_text(ui_prompt_for_action(self._state, Action.CONFIRM), "START RUN")
        ui_rich_print(text, ui_rich_text_center_x(text, margin_x=6), 124, Color.WHITE)

    def _draw_rollback_popup(self) -> None:
        if not self._rollback_modal_open:
            return
        layout = self._modal_layout(
            1,
            (1,),
            0,
            0,
            0
        )
        box_x, _box_y, box_w, _box_h, body_top, footer_line_y, footer_text_y = ui_overlay_modal_draw_chrome(
            layout,
            "ROLLBACK RECOVERED",
            Color.ORANGE,
            Color.ORANGE,
            Color.BLACK,
            Color.BLACK,
            Color.GREY
        )
        reason_line = self._rollback_modal_reason
        if reason_line == "":
            reason_line = "PROFILE RECOVERY APPLIED"
        body_lines: list[tuple[str, int]] = [
            (reason_line, Color.LIGHT_GREY),
            ("THESEUS +" + str(self._rollback_modal_gain), Color.RED)
        ]
        ui_overlay_modal_draw_centered_lines(
            body_lines,
            box_x,
            box_w,
            body_top,
            10
        )
        slots, _slot_confirm = ui_footer_slots_single_action(
            layout,
            self._state,
            Action.CANCEL,
            "CLOSE"
        )
        slot_active, slot_hover = self._ui.slot_states(
            1,
            [self._state.controls.down(Action.CANCEL)]
        )
        ui_overlay_footer_draw(
            layout,
            slots,
            slot_active,
            slot_hover,
            footer_line_y,
            footer_text_y,
            Color.BLACK,
            Color.GREY
        )

    def _draw_new_game_confirm(self) -> None:
        layout = self._modal_layout(
            2,
            (1, 1),
            0,
            0,
            1
        )
        box_x, _box_y, box_w, _box_h, body_top, footer_line_y, footer_text_y = ui_overlay_modal_draw_chrome(
            layout,
            "CONFIRM RESET",
            Color.WHITE,
            Color.WHITE,
            Color.BLACK,
            Color.BLACK,
            Color.GREY
        )
        body_lines: list[tuple[str, int]] = [
            ("START NEW GAME?", Color.WHITE),
            ("THIS RESETS PROFILE PROGRESS", Color.LIGHT_GREY)
        ]
        ui_overlay_modal_draw_centered_lines(
            body_lines,
            box_x,
            box_w,
            body_top,
            10
        )
        slots, _slot_confirm, _slot_cancel = ui_footer_slots_confirm_cancel(
            layout,
            self._state,
            Action.CONFIRM,
            Action.CANCEL,
            "CONFIRM RESET",
            "CANCEL"
        )
        slot_active, slot_hover = self._ui.slot_states(
            2,
            [
                self._state.controls.down(Action.CONFIRM),
                self._state.controls.down(Action.CANCEL)
            ]
        )
        ui_overlay_footer_draw(
            layout,
            slots,
            slot_active,
            slot_hover,
            footer_line_y,
            footer_text_y,
            Color.BLACK,
            Color.GREY
        )

    def _modal_layout(
        self,
        slot_count: int,
        slot_weights: tuple[int, ...],
        slot_nav: int,
        slot_confirm: int,
        slot_cancel: int
    ) -> OverlayLayout:
        return ui_overlay_layout_centered(
            self.MODAL_W,
            self.MODAL_H,
            self.MODAL_HEADER_TEXT_OFFSET_Y,
            self.MODAL_BODY_TOP_OFFSET_Y,
            self.MODAL_FOOTER_LINE_OFFSET_Y,
            self.MODAL_FOOTER_TEXT_OFFSET_Y,
            slot_count,
            slot_weights,
            slot_nav,
            slot_confirm,
            slot_cancel
        )

    def update(self, dt: float) -> None:
        self._ui.poll_mouse()
        confirm_released = self._ui.poll_action(self._state.controls, Action.CONFIRM)
        cancel_released = self._ui.poll_action(self._state.controls, Action.CANCEL)
        secondary_released = self._ui.poll_action(self._state.controls, Action.SECONDARY)
        help_released = self._ui.poll_action(self._state.controls, Action.HELP)

        if self._rollback_modal_open:
            layout = self._modal_layout(1, (1,), 0, 0, 0)
            slots, slot_confirm = ui_footer_slots_single_action(
                layout,
                self._state,
                Action.CANCEL,
                "CLOSE"
            )
            released_slot = self._ui.poll_footer_release(layout, slots)
            if cancel_released or released_slot == slot_confirm:
                self._rollback_modal_open = False
                self._ui.reset_footer()
            return

        if self._confirm_new_game:
            layout = self._modal_layout(2, (1, 1), 0, 0, 1)
            slots, slot_confirm, slot_cancel = ui_footer_slots_confirm_cancel(
                layout,
                self._state,
                Action.CONFIRM,
                Action.CANCEL,
                "CONFIRM RESET",
                "CANCEL"
            )
            released_slot = self._ui.poll_footer_release(layout, slots)
            if confirm_released or released_slot == slot_confirm:
                self._state.start_new_game()
                self._confirm_new_game = False
                self._pick_header_text()
                self._ui.reset_footer()
            elif cancel_released or released_slot == slot_cancel:
                self._confirm_new_game = False
                self._ui.reset_footer()
            return

        self._ui.reset_footer()
        if confirm_released:
            self._state.start_run()
            self._nav.go(SceneId.REGION_MAP)
        elif secondary_released:
            repaired = self._profile.repair(
                TUNING.PROFILE.repair_cost,
                TUNING.PROFILE.repair_hp,
                TUNING.PROFILE.start_garage_hp
            )
            if repaired:
                self._state.save_profile()
        elif help_released:
            self._confirm_new_game = True

    def draw(self) -> None:
        cls(Color.BLACK)
        self._draw_background()
        self._draw_header()
        self._draw_vehicle_panel()
        self._draw_theseus_panel()
        self._draw_secondary_actions()
        self._draw_start_cta()
        self._draw_rollback_popup()
        if self._confirm_new_game:
            self._draw_new_game_confirm()

    def exit(self) -> None:
        pass


def make_garage_scene(nav: SceneNavigator) -> GarageScene:
    return GarageScene(nav)
