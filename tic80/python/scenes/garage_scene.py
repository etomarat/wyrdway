from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import cls, line, print, rect, time

    from ..contracts import SceneEnterParams, SceneNavigator
    from ..core.controls.actions import Action
    from ..core.palette import Color
    from ..core.scene_ids import SceneId
    from ..core.text_layout import text_center_x, text_width
    from ..core.ui.action_bar import (
        ui_action_bar_build_standard,
        ui_action_bar_make_mouse_states,
        ui_action_bar_panel_height,
        ui_action_bar_reset_mouse_states,
        ui_action_bar_rows_draw_with_style,
        ui_action_bar_rows_poll_release_with_style,
        ui_action_bar_style_merge,
        ui_action_bar_style_with_border,
        ui_action_bar_style_with_panel
    )
    from ..core.ui.meter import (
        ui_meter_draw_bar,
        ui_meter_draw_labeled,
        ui_meter_fill_ratio
    )
    from ..core.ui.overlay_flow import (
        ui_overlay_flow_single_action
    )
    from ..core.ui.overlay_runtime import UiOverlayRuntime
    from ..core.ui.overlay_screen import ui_overlay_screen_draw
    from ..core.ui.overlay_theme import ui_overlay_theme_warning
    from ..core.ui.panel import ui_panel_draw
    from ..core.ui.prompts import ui_prompt_for_action, ui_prompt_with_text
    from ..data.tuning import TUNING


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
    MODAL_LAYOUT_SPEC = (
        MODAL_W,
        MODAL_H,
        MODAL_HEADER_TEXT_OFFSET_Y,
        MODAL_BODY_TOP_OFFSET_Y
    )
    ACTION_BAR_PANEL_X = 8
    ACTION_BAR_SCREEN_H = 136
    ACTION_BAR_BOTTOM_PAD = 2
    ACTION_BAR_PANEL_W = 224
    ACTION_BAR_ROW_GAP = 1
    ACTION_BAR_PANEL_PAD_Y = 1
    ACTION_BAR_ROW_SPECS = (
        (2, (1, 1)),
        (1, (1,))
    )
    ACTION_BAR_PANEL_Y = (
        ACTION_BAR_SCREEN_H
        - ui_action_bar_panel_height(
            len(ACTION_BAR_ROW_SPECS),
            row_gap=ACTION_BAR_ROW_GAP,
            pad_y=ACTION_BAR_PANEL_PAD_Y
        )
        - ACTION_BAR_BOTTOM_PAD
    )
    ACTION_BAR_PANEL_H, ACTION_BAR_LAYOUTS = ui_action_bar_build_standard(
        ACTION_BAR_PANEL_X,
        ACTION_BAR_PANEL_Y,
        ACTION_BAR_PANEL_W,
        ACTION_BAR_ROW_SPECS,
        row_gap=ACTION_BAR_ROW_GAP,
        pad_y=ACTION_BAR_PANEL_PAD_Y
    )
    ACTION_BAR_STYLE_BASE = ui_action_bar_style_merge(
        {
            "button_bg_color": Color.BLACK,
            "divider_color": Color.LIGHT_GREY,
            "footer_line_color": Color.LIGHT_GREY,
            "slot_text_color": Color.LIGHT_GREY,
            "slot_active_bg_color": Color.DARK_BLUE,
            "slot_hover_bg_color": Color.DARK_GREY,
            "slot_active_text_color": Color.WHITE,
            "slot_hover_text_color": Color.WHITE
        }
    )
    ACTION_BAR_STYLE_BASE = ui_action_bar_style_with_panel(
        ACTION_BAR_STYLE_BASE,
        ACTION_BAR_PANEL_X,
        ACTION_BAR_PANEL_Y,
        ACTION_BAR_PANEL_W,
        ACTION_BAR_PANEL_H,
        panel_outer_color=Color.BLACK,
        panel_inner_color=Color.BLACK,
        panel_border_outset=0
    )
    ACTION_BAR_STYLE_HOME = ui_action_bar_style_with_border(
        ACTION_BAR_STYLE_BASE,
        Color.LIGHT_GREY
    )
    ACTION_BAR_STYLE_SERVICE = ui_action_bar_style_with_border(
        ACTION_BAR_STYLE_BASE,
        Color.LIGHT_GREY
    )

    def __init__(self, nav: SceneNavigator) -> None:
        self._nav = nav
        self._state = nav.state
        self._ui = UiOverlayRuntime()
        self._profile = nav.state.profile
        self._action_row_mouse = ui_action_bar_make_mouse_states(
            len(self.ACTION_BAR_LAYOUTS)
        )
        self._service_open = False
        self._upgrades_modal_open = False
        self._rollback_modal_open = False
        self._rollback_modal_reason = ""
        self._rollback_modal_gain = 0
        self._header_text = self.HOME_HEADER_TEXT
        self._header_roll = 0

    def enter(self, params: SceneEnterParams = None) -> None:
        self._state.drive_preset_runtime.apply_by_id(self._state.drive_preset_id)
        self._ui.sync_actions(
            self._state.controls,
            [
                Action.CONFIRM,
                Action.CANCEL,
                Action.SECONDARY,
                Action.HELP
            ]
        )
        self._ui.reset_footer()
        self._reset_action_bar_mouse()
        self._service_open = False
        self._upgrades_modal_open = False
        reason, gain = self._state.consume_rollback_notice()
        self._rollback_modal_open = reason is not None
        self._rollback_modal_reason = "" if reason is None else str(reason)
        self._rollback_modal_gain = int(gain)
        self._pick_header_text()

    def _reset_action_bar_mouse(self) -> None:
        ui_action_bar_reset_mouse_states(self._action_row_mouse)

    def _pick_header_text(self) -> None:
        if self._state.run_index <= 0:
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
        divider_h = 96
        rect(0, 0, 240, divider_h, Color.DARK_GREY)
        rect(0, divider_h, 240, 90, Color.DARK_GREEN)
        y = 20
        while y < divider_h+1:
            line(0, y, 239, y, Color.BLACK)
            y += 11
        line(0, divider_h, 239, divider_h, Color.LIGHT_GREY)
        line(0, divider_h+1, 239, divider_h+1, Color.GREY)

    def _draw_header(self) -> None:
        rect(0, 0, 240, 15, Color.BLACK)
        line(0, 15, 239, 15, Color.LIGHT_GREY)
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

        ui_panel_draw(8, 77, 224, 14, Color.GREY,
                      Color.BLACK, Color.DARK_GREY)
        print("THESEUS", 16, 81, Color.LIGHT_GREY)

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

    def _home_action_slots_top(self) -> list[str]:
        return [
            ui_prompt_with_text(ui_prompt_for_action(
                self._state, Action.SECONDARY), "SERVICE"),
            ui_prompt_with_text(ui_prompt_for_action(
                self._state, Action.HELP), "MAIN MENU")
        ]

    def _home_action_slots_bottom(self) -> list[str]:
        return [
            ui_prompt_with_text(ui_prompt_for_action(
                self._state, Action.CONFIRM), "NEXT RUN")
        ]

    def _service_action_slots_top(self) -> list[str]:
        return [
            ui_prompt_with_text(ui_prompt_for_action(
                self._state, Action.SECONDARY), "REPAIR"),
            ui_prompt_with_text(ui_prompt_for_action(
                self._state, Action.HELP), "UPGRADES")
        ]

    def _service_action_slots_bottom(self) -> list[str]:
        return [
            ui_prompt_with_text(ui_prompt_for_action(
                self._state, Action.CANCEL), "BACK")
        ]

    def _active_action_slots_rows(self) -> list[list[str]]:
        if self._service_open:
            return [
                self._service_action_slots_top(),
                self._service_action_slots_bottom()
            ]
        return [
            self._home_action_slots_top(),
            self._home_action_slots_bottom()
        ]

    def _active_action_keyboard_rows(self) -> list[list[bool]]:
        top = [
            self._state.controls.down(Action.SECONDARY),
            self._state.controls.down(Action.HELP)
        ]
        if self._service_open:
            return [
                top,
                [self._state.controls.down(Action.CANCEL)]
            ]
        return [
            top,
            [self._state.controls.down(Action.CONFIRM)]
        ]

    def _draw_action_bar(self) -> None:
        slot_rows = self._active_action_slots_rows()
        keyboard_rows = self._active_action_keyboard_rows()
        style = self.ACTION_BAR_STYLE_HOME
        if self._service_open:
            style = self.ACTION_BAR_STYLE_SERVICE
        ui_action_bar_rows_draw_with_style(
            self.ACTION_BAR_LAYOUTS,
            slot_rows,
            keyboard_rows,
            self._ui.mouse,
            self._action_row_mouse,
            style
        )

    def _draw_rollback_popup(self) -> None:
        if not self._rollback_modal_open:
            return
        layout, slots, _slot_confirm = ui_overlay_flow_single_action(
            self.MODAL_LAYOUT_SPEC,
            self._state,
            Action.CANCEL,
            "CLOSE"
        )
        reason_line = self._rollback_modal_reason
        if reason_line == "":
            reason_line = "PROFILE RECOVERY APPLIED"
        body_lines: list[tuple[str, int]] = [
            (reason_line, Color.LIGHT_GREY),
            ("THESEUS +" + str(self._rollback_modal_gain), Color.RED)
        ]
        ui_overlay_screen_draw(
            self._ui,
            layout,
            "ROLLBACK RECOVERED",
            body_lines,
            slots,
            [self._state.controls.down(Action.CANCEL)],
            theme=ui_overlay_theme_warning(),
            body_line_step=10
        )

    def _draw_upgrades_modal(self) -> None:
        if not self._upgrades_modal_open:
            return
        layout, slots, _slot_confirm = ui_overlay_flow_single_action(
            self.MODAL_LAYOUT_SPEC,
            self._state,
            Action.CANCEL,
            "CLOSE"
        )
        body_lines: list[tuple[str, int]] = [
            ("UPGRADES ARE NOT IMPLEMENTED YET", Color.LIGHT_GREY),
            ("COMING SOON", Color.YELLOW)
        ]
        ui_overlay_screen_draw(
            self._ui,
            layout,
            "UPGRADES",
            body_lines,
            slots,
            [self._state.controls.down(Action.CANCEL)],
            body_line_step=10
        )

    def update(self, dt: float) -> None:
        self._ui.poll_mouse()
        confirm_released = self._ui.poll_confirm(
            self._state, self._state.controls)
        cancel_released = self._ui.poll_cancel(
            self._state, self._state.controls)
        secondary_released = self._ui.poll_action(
            self._state.controls, Action.SECONDARY)
        help_released = self._ui.poll_action(self._state.controls, Action.HELP)

        if self._rollback_modal_open:
            layout, slots, slot_confirm = ui_overlay_flow_single_action(
                self.MODAL_LAYOUT_SPEC,
                self._state,
                Action.CANCEL,
                "CLOSE"
            )
            released_slot = self._ui.poll_footer_release(layout, slots)
            if cancel_released or self._ui.footer_button_released(self._state, released_slot, slot_confirm):
                self._rollback_modal_open = False
                self._ui.reset_footer()
            return

        if self._upgrades_modal_open:
            layout, slots, slot_confirm = ui_overlay_flow_single_action(
                self.MODAL_LAYOUT_SPEC,
                self._state,
                Action.CANCEL,
                "CLOSE"
            )
            released_slot = self._ui.poll_footer_release(layout, slots)
            if cancel_released or confirm_released or self._ui.footer_button_released(self._state, released_slot, slot_confirm):
                self._upgrades_modal_open = False
                self._ui.reset_footer()
                self._reset_action_bar_mouse()
                return

        slot_rows = self._active_action_slots_rows()
        released_rows = ui_action_bar_rows_poll_release_with_style(
            self.ACTION_BAR_LAYOUTS,
            slot_rows,
            self._ui.mouse,
            self._action_row_mouse,
            self.ACTION_BAR_STYLE_BASE
        )
        released_top = -1
        released_bottom = -1
        if len(released_rows) > 0:
            released_top = int(released_rows[0])
        if len(released_rows) > 1:
            released_bottom = int(released_rows[1])

        if self._service_open:
            if secondary_released or released_top == 0:
                repaired = self._profile.repair(
                    TUNING.PROFILE.repair_cost,
                    TUNING.PROFILE.repair_hp,
                    TUNING.PROFILE.start_garage_hp
                )
                if repaired:
                    self._state.vibe_success()
                    self._state.save_profile()
                else:
                    self._state.vibe_fail()
                return
            if help_released or released_top == 1:
                self._state.vibe_ui_button()
                self._upgrades_modal_open = True
                self._ui.reset_footer()
                self._reset_action_bar_mouse()
                return
            if cancel_released or released_bottom == 0:
                self._state.vibe_ui_button()
                self._service_open = False
                self._ui.reset_footer()
                self._reset_action_bar_mouse()
                return

        if confirm_released or released_bottom == 0:
            self._state.vibe_ui_button()
            self._state.start_run()
            self._nav.go(SceneId.REGION_MAP)
        elif secondary_released or released_top == 0:
            self._state.vibe_ui_button()
            self._service_open = True
            self._ui.reset_footer()
            self._reset_action_bar_mouse()
        elif help_released or released_top == 1:
            self._state.vibe_ui_button()
            self._state.save_profile()
            self._ui.reset_footer()
            self._reset_action_bar_mouse()
            self._nav.go(SceneId.MAIN_MENU)

    def draw(self) -> None:
        cls(Color.BLACK)
        self._draw_background()
        self._draw_header()
        self._draw_vehicle_panel()
        self._draw_theseus_panel()
        self._draw_action_bar()
        self._draw_rollback_popup()
        self._draw_upgrades_modal()

    def exit(self) -> None:
        pass


def make_garage_scene(nav: SceneNavigator) -> GarageScene:
    return GarageScene(nav)
