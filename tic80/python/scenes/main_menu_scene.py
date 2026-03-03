from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import circ, cls, line, pix, print, rect

    from ..contracts import SceneEnterParams, SceneNavigator
    from ..core.controls.actions import Action
    from ..core.controls.modes import InputDeviceMode
    from ..core.controls.prompts import (
        PromptGlyph,
        filter_prompt_glyphs,
        format_prompt,
        prompt_glyphs_for_action,
        prompt_glyphs_for_nav_hint
    )
    from ..core.palette import Color
    from ..core.scene_ids import SceneId
    from ..core.text_layout import text_right_x, text_width
    from ..core.ui.footer_slots import (
        ui_footer_slot_indices,
        ui_footer_slots_standard
    )
    from ..core.ui.options_bindings_table import ui_options_bindings_table_draw
    from ..core.ui.options_overlay_state import UiOptionsOverlayState
    from ..core.ui.options_settings import (
        ui_options_settings_dir_at,
        ui_options_settings_draw,
        ui_options_settings_row_at
    )
    from ..core.ui.overlay_layout import (
        FOOTER_PAD_PROFILE_DEFAULT,
        FOOTER_PAD_PROFILE_INVERTED,
        OverlayLayout,
        ui_overlay_footer_positions,
        ui_overlay_layout_int,
        ui_overlay_layout_slot_count
    )
    from ..core.ui.overlay_runtime import UiOverlayRuntime
    from ..core.ui.overlay_screen import ui_overlay_screen_draw
    from ..core.ui.overlay_theme import ui_overlay_theme_inverted
    from ..core.ui.prompts import ui_prompt_gap_join, ui_prompt_with_text
    from ..core.version import game_version_label
    from .drive.pursuer_text_bank import PursuerTextBank
    from .main_menu_backdrop import MainMenuBackdrop, make_main_menu_backdrop
else:
    OverlayLayout = dict


class MainMenuScene:
    SCENE_ID = SceneId.MAIN_MENU
    _LEFT_X = 4
    _LEFT_Y = 20
    _LEFT_W = 88
    _LEFT_H = 114
    _RIGHT_X = 96
    _RIGHT_Y = 20
    _RIGHT_W = 140
    _RIGHT_H = 114
    _LEFT_HEADER_TEXT = "MAIN MENU"

    _ITEM_CONTINUE = 0
    _ITEM_NEW_GAME = 1
    _ITEM_CONTROLS = 2
    _ITEM_CREDITS = 3

    _MENU_ITEMS: list[tuple[int, str]] = [
        (_ITEM_CONTINUE, "CONTINUE"),
        (_ITEM_NEW_GAME, "NEW GAME"),
        (_ITEM_CONTROLS, "OPTIONS"),
        (_ITEM_CREDITS, "CREDITS")
    ]

    _OVERLAY_NONE = 0
    _OVERLAY_CONTROLS = 1
    _OVERLAY_CREDITS = 2
    _OVERLAY_NEW_GAME_CONFIRM = 3
    _OVERLAY_BODY_X_PAD = 8
    _OVERLAY_BODY_LINE_STEP = 8
    _OVERLAY_LAYOUT_DEFAULT: OverlayLayout = {
        "box_x": 20,
        "box_y": 28,
        "box_w": 200,
        "box_h": 90,
        "header_text_y": 37,
        "body_top": 54,
        "footer_pad_profile": FOOTER_PAD_PROFILE_DEFAULT,
        "footer_line_gap": 4,
        "footer_bg_color": 0,
        "slot_count": 4,
        "slot_weights": (1, 1, 1, 1),
        "slot_nav": 0,
        "slot_confirm": 2,
        "slot_cancel": 3
    }
    _OVERLAY_LAYOUTS: dict[int, OverlayLayout] = {
        _OVERLAY_CONTROLS: {
            "box_x": 4,
            "box_y": 4,
            "box_w": 232,
            "box_h": 130,
            "header_text_y": 13,
            "body_top": 25,
            "footer_pad_profile": FOOTER_PAD_PROFILE_INVERTED,
            "footer_line_gap": 4,
            "footer_button_top_pad": 2,
            "footer_bg_color": 0,
            "slot_count": 3,
            "slot_weights": (1, 1, 1),
            "slot_nav": 0,
            "slot_confirm": 1,
            "slot_cancel": 2
        },
        _OVERLAY_CREDITS: {
            "box_x": 20,
            "box_y": 28,
            "box_w": 200,
            "box_h": 90,
            "header_text_y": 37,
            "body_top": 54,
            "footer_pad_profile": FOOTER_PAD_PROFILE_DEFAULT,
            "footer_line_gap": 4,
            "footer_bg_color": 0,
            "slot_count": 4,
            "slot_weights": (1, 1, 1, 1),
            "slot_nav": 0,
            "slot_confirm": 2,
            "slot_cancel": 3
        },
        _OVERLAY_NEW_GAME_CONFIRM: {
            "box_x": 20,
            "box_y": 28,
            "box_w": 200,
            "box_h": 90,
            "header_text_y": 37,
            "body_top": 54,
            "footer_pad_profile": FOOTER_PAD_PROFILE_DEFAULT,
            "footer_line_gap": 4,
            "footer_bg_color": 0,
            "slot_count": 2,
            "slot_weights": (1, 1),
            "slot_nav": 0,
            "slot_confirm": 0,
            "slot_cancel": 1
        }
    }
    _WATCH_PULSE_SECONDS = 4.8
    _WATCH_GLITCH_SECONDS = 0.18
    _WATCH_ERROR_HOLD_SECONDS = 0.18
    _WATCH_REC_BLINK_HZ = 2.0
    _WATCH_STATIC_DOTS = 0
    _WATCH_STATIC_DOTS_PULSE = 4

    def __init__(self, nav: SceneNavigator) -> None:
        self._nav = nav
        self._state = nav.state
        self._ui = UiOverlayRuntime()
        self._options = UiOptionsOverlayState()
        self._selected = 0
        self._overlay = self._OVERLAY_NONE
        self._overlay_scroll = 0
        self._controls_mouse_hover_row = -1
        self._controls_mouse_hover_dir = 0
        self._controls_mouse_down_row = -1
        self._controls_mouse_down_dir = 0
        self._controls_mouse_right_down_row = -1
        self._controls_mouse_right_down_dir = 0
        self._mouse_x = 0
        self._mouse_y = 0
        self._mouse_left_down = False
        self._mouse_left_pressed = False
        self._mouse_left_released = False
        self._mouse_right_down = False
        self._mouse_right_pressed = False
        self._mouse_right_released = False
        self._mouse_scroll_y = 0
        self._menu_mouse_hover_index = -1
        self._menu_mouse_down_index = -1
        self._backdrop: MainMenuBackdrop = make_main_menu_backdrop()
        self._watch_text_bank = PursuerTextBank()
        self._watch_seed = 0x13579BDF
        self._watch_event_t = 0.0
        self._watch_glitch_t = 0.0
        self._watch_error_t = 0.0
        self._watch_error_text = ""
        self._watch_rec_t = 0.0

    def enter(self, params: SceneEnterParams = None) -> None:
        self._selected = 0
        self._overlay = self._OVERLAY_NONE
        self._overlay_scroll = 0
        self._menu_mouse_hover_index = -1
        self._menu_mouse_down_index = -1
        self._ui.reset_footer()
        self._reset_menu_input_latches()
        self._init_controls_overlay_draft()
        self._reset_controls_overlay_mouse_state()
        self._reset_overlay_input_latches()
        self._backdrop.enter()
        self._watch_seed = (0x13579BDF ^ (
            (int(self._state.seed_counter) + 1) * 97)) & 0xFFFFFFFF
        if self._watch_seed == 0:
            self._watch_seed = 1
        self._watch_event_t = 0.0
        self._watch_glitch_t = 0.0
        self._watch_error_t = 0.0
        self._watch_error_text = ""
        self._watch_rec_t = 0.0

    def update(self, dt: float) -> None:
        self._poll_mouse_state()
        self._backdrop.update(dt)
        self._update_entity_watch(dt)
        if self._overlay != self._OVERLAY_NONE:
            self._update_overlay_input()
            return

        nav_up_released, nav_down_released = self._poll_menu_nav_release_events()
        if nav_up_released:
            self._selected -= 1
        elif nav_down_released:
            self._selected += 1

        item_count = len(self._MENU_ITEMS)
        if item_count > 0:
            while self._selected < 0:
                self._selected += item_count
            while self._selected >= item_count:
                self._selected -= item_count

        self._menu_mouse_hover_index = self._menu_item_at(
            self._mouse_x,
            self._mouse_y
        )
        if self._menu_mouse_hover_index >= 0:
            self._selected = self._menu_mouse_hover_index

        mouse_confirm_released = self._poll_menu_mouse_confirm_release()
        keyboard_confirm_released = self._poll_menu_confirm_release()
        if mouse_confirm_released or keyboard_confirm_released:
            self._activate_selected_item()

    def draw(self) -> None:
        cls(Color.BLACK)
        self._draw_title()
        self._draw_gameplay_panel()
        self._draw_left_column()
        self._draw_footer()
        self._draw_overlay()

    def exit(self) -> None:
        pass

    def _has_continue(self) -> bool:
        return bool(self._state.profile_loaded)

    def _update_overlay_input(self) -> None:
        nav_up_released, nav_down_released, nav_left_released, nav_right_released, confirm_released, cancel_released = self._poll_overlay_release_events()
        mouse_nav_released, mouse_confirm_released, mouse_cancel_released = self._poll_overlay_footer_mouse_release()
        if mouse_confirm_released:
            confirm_released = True
        if mouse_cancel_released:
            cancel_released = True
        if self._overlay == self._OVERLAY_CONTROLS:
            self._update_controls_overlay_mouse_state()
            self._update_controls_overlay_settings(
                nav_up_released,
                nav_down_released,
                nav_left_released,
                nav_right_released
            )
            if mouse_nav_released:
                nav_down_released = True
                self._update_controls_overlay_settings(
                    False,
                    nav_down_released,
                    False,
                    False
                )
            self._poll_controls_overlay_mouse_setting_release()
            if cancel_released:
                self._close_overlay()
                return
            if confirm_released:
                self._apply_controls_overlay_settings()
                self._close_overlay()
            return

        if mouse_nav_released:
            nav_down_released = True
        if self._overlay == self._OVERLAY_NEW_GAME_CONFIRM:
            if cancel_released:
                self._close_overlay()
                return
            if confirm_released:
                self._state.start_new_game()
                self._nav.go(SceneId.DRIVE_PRESET)
            return

        body_lines = self._overlay_body_lines_for(self._overlay)
        self._clamp_overlay_scroll(body_lines)
        if nav_up_released:
            self._overlay_scroll -= 1
            self._clamp_overlay_scroll(body_lines)
        elif nav_down_released:
            self._overlay_scroll += 1
            self._clamp_overlay_scroll(body_lines)

        if cancel_released or confirm_released:
            self._close_overlay()

    def _activate_selected_item(self) -> None:
        item_id, _ = self._MENU_ITEMS[self._selected]
        if item_id == self._ITEM_CONTINUE:
            if not self._has_continue():
                return
            self._nav.go(SceneId.DRIVE_PRESET)
            return
        if item_id == self._ITEM_NEW_GAME:
            if self._has_continue():
                self._open_overlay(self._OVERLAY_NEW_GAME_CONFIRM)
                return
            self._state.start_new_game()
            self._nav.go(SceneId.DRIVE_PRESET)
            return
        if item_id == self._ITEM_CONTROLS:
            self._open_overlay(self._OVERLAY_CONTROLS)
            return
        if item_id == self._ITEM_CREDITS:
            self._open_overlay(self._OVERLAY_CREDITS)
            return

    def _open_overlay(self, overlay_id: int) -> None:
        self._overlay = int(overlay_id)
        self._overlay_scroll = 0
        self._menu_mouse_down_index = -1
        self._ui.reset_footer()
        self._reset_controls_overlay_mouse_state()
        if self._overlay == self._OVERLAY_CONTROLS:
            self._init_controls_overlay_draft()
        self._reset_menu_input_latches()
        self._reset_overlay_input_latches()

    def _close_overlay(self) -> None:
        self._overlay = self._OVERLAY_NONE
        self._overlay_scroll = 0
        self._ui.reset_footer()
        self._reset_controls_overlay_mouse_state()
        self._reset_menu_input_latches()
        self._reset_overlay_input_latches()

    def _poll_mouse_state(self) -> None:
        self._ui.poll_mouse()
        self._mouse_left_pressed = self._ui.mouse.left_pressed
        self._mouse_left_released = self._ui.mouse.left_released
        self._mouse_left_down = self._ui.mouse.left_down
        self._mouse_right_pressed = self._ui.mouse.right_pressed
        self._mouse_right_released = self._ui.mouse.right_released
        self._mouse_right_down = self._ui.mouse.right_down
        self._mouse_x = self._ui.mouse.x
        self._mouse_y = self._ui.mouse.y
        self._mouse_scroll_y = self._ui.mouse.scroll_y

    def _poll_menu_confirm_release(self) -> bool:
        return self._ui.poll_action(self._state.controls, Action.CONFIRM)

    def _poll_menu_nav_release_events(self) -> tuple[bool, bool]:
        return (
            self._ui.poll_action(self._state.controls, Action.NAV_UP),
            self._ui.poll_action(self._state.controls, Action.NAV_DOWN)
        )

    def _poll_menu_mouse_confirm_release(self) -> bool:
        hover_idx = self._menu_mouse_hover_index
        if self._mouse_left_pressed:
            self._menu_mouse_down_index = hover_idx
        if not self._mouse_left_down and not self._mouse_left_released:
            self._menu_mouse_down_index = -1
        if not self._mouse_left_released:
            return False
        activated = (
            self._menu_mouse_down_index >= 0
            and self._menu_mouse_down_index == hover_idx
        )
        self._menu_mouse_down_index = -1
        return activated

    def _poll_overlay_footer_mouse_release(self) -> tuple[bool, bool, bool]:
        if self._overlay == self._OVERLAY_NONE:
            self._ui.reset_footer()
            return False, False, False
        layout = self._overlay_layout()
        nav_enabled = self._overlay_footer_nav_enabled(layout)
        slot_count = ui_overlay_layout_slot_count(layout)
        slots = self._overlay_footer_slots(layout, slot_count)
        released_slot = self._ui.poll_footer_release(layout, slots)
        slot_nav, slot_confirm, slot_cancel = ui_footer_slot_indices(
            layout, slot_count)
        return (
            nav_enabled and released_slot == slot_nav,
            released_slot == slot_confirm,
            released_slot == slot_cancel
        )

    def _sync_release_menu_actions(self) -> None:
        self._ui.sync_actions(
            self._state.controls,
            [Action.NAV_UP, Action.NAV_DOWN, Action.CONFIRM]
        )

    def _sync_release_overlay_actions(self) -> None:
        self._ui.sync_actions(
            self._state.controls,
            [
                Action.NAV_UP,
                Action.NAV_DOWN,
                Action.NAV_LEFT,
                Action.NAV_RIGHT,
                Action.CONFIRM,
                Action.CANCEL
            ]
        )

    def _reset_overlay_input_latches(self) -> None:
        self._sync_release_overlay_actions()

    def _reset_menu_input_latches(self) -> None:
        self._sync_release_menu_actions()

    def _poll_overlay_release_events(self) -> tuple[bool, bool, bool, bool, bool, bool]:
        return (
            self._ui.poll_action(self._state.controls, Action.NAV_UP),
            self._ui.poll_action(self._state.controls, Action.NAV_DOWN),
            self._ui.poll_action(self._state.controls, Action.NAV_LEFT),
            self._ui.poll_action(self._state.controls, Action.NAV_RIGHT),
            self._ui.poll_action(self._state.controls, Action.CONFIRM),
            self._ui.poll_action(self._state.controls, Action.CANCEL)
        )

    def _overlay_nav_any_down(self) -> bool:
        return bool(
            self._state.controls.down(Action.NAV_UP)
            or self._state.controls.down(Action.NAV_DOWN)
            or self._state.controls.down(Action.NAV_LEFT)
            or self._state.controls.down(Action.NAV_RIGHT)
        )

    def _init_controls_overlay_draft(self) -> None:
        self._options.reset_draft(
            self._state.input_device_mode,
            self._state.drive_preset_id,
            bool(self._state.prompt_show_shoulders),
            bool(self._state.vibration_enabled)
        )
        self._reset_controls_overlay_mouse_state()

    def _reset_controls_overlay_mouse_state(self) -> None:
        self._controls_mouse_hover_row = -1
        self._controls_mouse_hover_dir = 0
        self._controls_mouse_down_row = -1
        self._controls_mouse_down_dir = 0
        self._controls_mouse_right_down_row = -1
        self._controls_mouse_right_down_dir = 0

    def _controls_shoulders_enabled(self) -> bool:
        return self._options.shoulders_enabled()

    def _controls_vibration_enabled(self) -> bool:
        return self._options.vibration_enabled()

    def _update_controls_overlay_settings(
        self,
        nav_up_released: bool,
        nav_down_released: bool,
        nav_left_released: bool,
        nav_right_released: bool
    ) -> None:
        self._options.update_from_nav(
            nav_up_released,
            nav_down_released,
            nav_left_released,
            nav_right_released
        )

    def _controls_apply_setting_change(self, row: int, forward: bool) -> None:
        self._options.apply_setting_change(row, forward)

    def _update_controls_overlay_mouse_state(self) -> None:
        layout = self._overlay_layout()
        hover_row = self._controls_setting_row_at(
            layout,
            self._mouse_x,
            self._mouse_y
        )
        hover_dir = 0
        if hover_row >= 0:
            self._options.focus_row = hover_row
            hover_dir = self._controls_setting_dir_at(
                layout,
                hover_row,
                self._mouse_x,
                self._mouse_y
            )
        self._controls_mouse_hover_row = hover_row
        self._controls_mouse_hover_dir = hover_dir
        if self._mouse_left_pressed:
            self._controls_mouse_down_row = hover_row
            self._controls_mouse_down_dir = hover_dir
        if self._mouse_right_pressed:
            self._controls_mouse_right_down_row = hover_row
            self._controls_mouse_right_down_dir = hover_dir
        if not self._mouse_left_down and not self._mouse_left_released:
            self._controls_mouse_down_row = -1
            self._controls_mouse_down_dir = 0
        if not self._mouse_right_down and not self._mouse_right_released:
            self._controls_mouse_right_down_row = -1
            self._controls_mouse_right_down_dir = 0

    def _poll_controls_overlay_mouse_setting_release(self) -> None:
        hover_row = self._controls_mouse_hover_row
        hover_dir = self._controls_mouse_hover_dir
        if self._mouse_left_released:
            down_row = self._controls_mouse_down_row
            down_dir = self._controls_mouse_down_dir
            self._controls_mouse_down_row = -1
            self._controls_mouse_down_dir = 0
            if down_row >= 0 and down_row == hover_row:
                self._options.focus_row = down_row
                if down_dir != 0:
                    if down_dir == hover_dir:
                        self._controls_apply_setting_change(
                            down_row, down_dir < 0)
                    return
                if hover_dir != 0:
                    self._controls_apply_setting_change(
                        down_row, hover_dir < 0)
                    return
                self._controls_apply_setting_change(down_row, True)
                return
        if self._mouse_right_released:
            down_row = self._controls_mouse_right_down_row
            self._controls_mouse_right_down_row = -1
            self._controls_mouse_right_down_dir = 0
            if down_row < 0 or down_row != hover_row:
                return
            self._options.focus_row = down_row
            # RMB is always "backward" for setting cycles/toggles.
            self._controls_apply_setting_change(down_row, False)
            return

    def _apply_controls_overlay_settings(self) -> None:
        self._state.set_input_device_mode(self._options.mode_draft)
        self._state.set_drive_preset_id(self._options.drive_preset_draft)
        show_shoulders = self._options.shoulders_draft and self._controls_shoulders_enabled()
        self._state.set_prompt_show_shoulders(show_shoulders)
        vibration_enabled = self._options.vibration_draft and self._controls_vibration_enabled()
        self._state.set_vibration_enabled(vibration_enabled)
        self._state.save_options()

    def _draw_title(self) -> None:
        rect(0, 0, 240, 18, Color.BLACK)
        line(0, 17, 239, 17, Color.GREY)
        title = "W Y R D W A Y"
        tx = 6
        ty = 3
        print(title, tx + 1, ty + 1, Color.RED, True, 2)
        print(title, tx, ty, Color.YELLOW, True, 2)
        ver = game_version_label()
        ver_x = tx + text_width(title, 12) + 6
        ver_y = ty + 6
        print(ver, ver_x, ver_y, Color.GREY, fixed=True, alt=True)

    def _draw_gameplay_panel(self) -> None:
        x = self._RIGHT_X
        y = self._RIGHT_Y
        w = self._RIGHT_W
        h = self._RIGHT_H
        rect(x - 1, y - 1, w + 2, h + 2, Color.GREY)
        rect(x, y, w, h, Color.BLACK)
        self._backdrop.draw(x, y, w, h)
        self._draw_entity_watch_static_noise(x, y, w, h)
        self._draw_entity_watch_glitch(x, y, w, h)
        self._draw_entity_watch_header(x, y)
        self._draw_entity_watch_error(x, y, w, h)

    def _draw_left_column(self) -> None:
        x = self._LEFT_X
        y = self._LEFT_Y
        w = self._LEFT_W
        h = self._LEFT_H
        rect(x - 1, y - 1, w + 2, h + 2, Color.GREY)
        rect(x, y, w, h, Color.BLACK)
        line(x, y + 11, x + w - 1, y + 11, Color.DARK_GREY)
        print(self._LEFT_HEADER_TEXT, x + 3, y + 3, Color.LIGHT_GREY)
        self._draw_menu_items(x + 4, y + 16)
        self._draw_left_save_info(x, y, w, h)

    def _draw_menu_items(self, x: int, y: int) -> None:
        i = 0
        while i < len(self._MENU_ITEMS):
            item_id, label = self._MENU_ITEMS[i]
            enabled = True
            if item_id == self._ITEM_CONTINUE:
                enabled = self._has_continue()
            selected = i == self._selected
            color = Color.WHITE
            if not enabled:
                color = Color.GREY
            if selected and enabled:
                color = Color.YELLOW
            active = self._menu_item_active(i, enabled, selected)
            if active:
                rect(self._LEFT_X + 2, y - 1,
                     self._LEFT_W - 4, 8, Color.DARK_GREY)
                if enabled:
                    color = Color.WHITE
            marker = "  "
            if selected:
                marker = "> "
            print(marker + label, x, y, color)
            y += 10
            i += 1

    def _menu_item_active(self, index: int, enabled: bool, selected: bool) -> bool:
        # UI rule: when a modal/overlay is open, background UI must not react.
        # Keep this behavior when moving modals to a shared UI layer.
        if self._overlay != self._OVERLAY_NONE:
            return False
        if not enabled:
            return False
        keyboard_active = (
            selected
            and self._overlay == self._OVERLAY_NONE
            and self._state.controls.down(Action.CONFIRM)
        )
        mouse_active = (
            self._mouse_left_down
            and self._menu_mouse_down_index == index
            and self._menu_mouse_hover_index == index
        )
        return keyboard_active or mouse_active

    def _menu_item_at(self, mx: int, my: int) -> int:
        row_x = self._LEFT_X + 2
        row_w = self._LEFT_W - 4
        if mx < row_x or mx >= row_x + row_w:
            return -1
        y0 = self._LEFT_Y + 16
        i = 0
        while i < len(self._MENU_ITEMS):
            row_y = y0 + i * 10
            if my >= row_y - 1 and my < row_y + 7:
                return i
            i += 1
        return -1

    def _draw_left_save_info(self, x: int, y: int, w: int, h: int) -> None:
        if not self._has_continue():
            return
        if self._overlay != self._OVERLAY_NONE:
            return
        selected_id, _ = self._MENU_ITEMS[self._selected]
        if selected_id != self._ITEM_CONTINUE:
            return

        split_y = y + 66
        line(x, split_y, x + w - 1, split_y, Color.DARK_GREY)
        print("ON CONTINUE", x + 3, split_y + 4, Color.LIGHT_GREY)
        profile = self._state.profile
        row_step = 8
        seed_row_y = y + h - 9
        row_y = seed_row_y - row_step * 3
        self._draw_kv_row(x, w, row_y, "HP", str(
            self._to_ui_int(profile.garage_hp)), Color.WHITE, Color.WHITE)
        self._draw_kv_row(x, w, row_y + row_step, "FUEL",
                          str(self._to_ui_int(profile.garage_fuel)), Color.WHITE, Color.WHITE)
        self._draw_kv_row(x, w, row_y + row_step * 2, "SCRAP",
                          str(profile.scrap), Color.LIGHT_GREY, Color.LIGHT_GREY)
        self._draw_kv_row(x, w, row_y + row_step * 3, "SEED",
                          str(self._state.seed_counter), Color.GREY, Color.GREY)

    @staticmethod
    def _to_ui_int(value: float) -> int:
        if value >= 0.0:
            return int(value + 0.5)
        return int(value - 0.5)

    @staticmethod
    def _draw_kv_row(
        x: int,
        w: int,
        y: int,
        label: str,
        value: str,
        label_color: int,
        value_color: int
    ) -> None:
        print(label, x + 3, y, label_color)
        value_x = text_right_x(value, x + w - 3, 6, x + 3)
        print(value, value_x, y, value_color, fixed=True)

    def _draw_footer(self) -> None:
        return

    def _update_entity_watch(self, dt: float) -> None:
        if dt < 0.0:
            dt = 0.0
        if self._watch_glitch_t > 0.0:
            self._watch_glitch_t -= dt
            if self._watch_glitch_t < 0.0:
                self._watch_glitch_t = 0.0
                self._watch_error_text = ""
                self._watch_error_t = 0.0
        if self._watch_error_t > 0.0:
            self._watch_error_t -= dt
            if self._watch_error_t <= 0.0:
                self._watch_error_t = 0.0
                self._watch_error_text = ""
        self._watch_rec_t += dt

        self._watch_event_t += dt
        if self._watch_event_t < self._WATCH_PULSE_SECONDS:
            return
        while self._watch_event_t >= self._WATCH_PULSE_SECONDS:
            self._watch_event_t -= self._WATCH_PULSE_SECONDS
        self._trigger_entity_watch_glitch()

    def _trigger_entity_watch_glitch(self) -> None:
        seed = self._next_watch_seed()
        txt = self._watch_text_bank.entity_error_text(seed)
        if txt == "":
            txt = "NULL PTR"
        self._watch_error_text = txt
        self._watch_glitch_t = self._WATCH_GLITCH_SECONDS
        self._watch_error_t = self._WATCH_ERROR_HOLD_SECONDS

    def _draw_entity_watch_header(self, x: int, y: int) -> None:
        rect(x + 2, y + 2, 84, 8, Color.BLACK)
        blink_on = (int(self._watch_rec_t * self._WATCH_REC_BLINK_HZ) & 1) == 0
        if self._watch_glitch_t > 0.0:
            blink_on = True
        if blink_on:
            circ(x + 6, y + 5, 2, Color.RED)
        print("ENTITY WATCH", x + 12, y + 3, Color.LIGHT_GREY)

    def _draw_entity_watch_error(self, x: int, y: int, w: int, h: int) -> None:
        if self._watch_glitch_t <= 0.0:
            return
        txt = self._watch_error_text
        if txt == "":
            return
        tx = text_right_x(txt, x + w - 4, 6, x + 4)
        ty = y + h - 9
        tw = len(txt) * 6 + 2
        rect(tx - 1, ty - 1, tw, 8, Color.BLACK)
        print(txt, tx, ty, Color.RED)

    def _draw_entity_watch_glitch(self, x: int, y: int, w: int, h: int) -> None:
        active_pulse = self._watch_glitch_t > 0.0
        line_count = 1
        if active_pulse:
            line_count = 5
        i = 0
        while i < line_count:
            s = self._next_watch_seed()
            gx = x + 3 + int(s % (w - 10))
            gy = y + 10 + int((s >> 8) % (h - 16))
            span = 6 + int((s >> 16) % 26)
            if not active_pulse:
                span = 4 + int((s >> 16) % 12)
            max_right = x + w - 3
            gx2 = gx + span
            if gx2 > max_right:
                gx2 = max_right
            color = Color.DARK_GREY
            if active_pulse and (s & 3) == 0:
                color = Color.LIGHT_GREY
            line(gx, gy, gx2, gy, color)
            i += 1
        if active_pulse:
            bseed = self._next_watch_seed()
            by = y + 12 + int((bseed >> 8) % (h - 20))
            rect(x + 2, by, w - 4, 2, Color.DARK_GREY)

    def _draw_entity_watch_static_noise(self, x: int, y: int, w: int, h: int) -> None:
        dots = self._WATCH_STATIC_DOTS
        if self._watch_glitch_t > 0.0:
            dots = self._WATCH_STATIC_DOTS_PULSE
        i = 0
        while i < dots:
            s = self._next_watch_seed()
            px = x + 2 + int(s % (w - 4))
            py = y + 10 + int((s >> 8) % (h - 12))
            c = Color.DARK_GREY
            if (s & 7) == 0:
                c = Color.GREY
            if self._watch_glitch_t > 0.0 and (s & 15) == 0:
                c = Color.LIGHT_GREY
            pix(px, py, c)
            i += 1

    def _next_watch_seed(self) -> int:
        self._watch_seed = (self._watch_seed * 1664525 +
                            1013904223) & 0xFFFFFFFF
        if self._watch_seed == 0:
            self._watch_seed = 1
        return int(self._watch_seed)

    def _draw_overlay(self) -> None:
        if self._overlay == self._OVERLAY_NONE:
            return
        if self._overlay == self._OVERLAY_CONTROLS:
            self._draw_controls_overlay()
            return
        if self._overlay == self._OVERLAY_CREDITS:
            self._draw_credits_overlay()
            return
        if self._overlay == self._OVERLAY_NEW_GAME_CONFIRM:
            self._draw_new_game_overlay()
            return

    def _draw_overlay_box(self, title: str, lines: list[str]) -> None:
        layout = self._overlay_layout()
        slots, keyboard_active, button_bg_color = self._overlay_footer_state(
            layout)
        x, _y, w, _h, body_top, _footer_line_y, _footer_text_y = ui_overlay_screen_draw(
            self._ui,
            layout,
            title,
            [],
            slots,
            keyboard_active,
            body_line_step=self._OVERLAY_BODY_LINE_STEP,
            button_bg_color=button_bg_color
        )
        wrapped = self._overlay_wrap_lines(lines, layout)
        self._clamp_overlay_scroll(lines, layout)
        visible_lines = self._overlay_visible_lines(layout)
        max_scroll = self._overlay_max_scroll(lines, layout)
        body_x = x + self._OVERLAY_BODY_X_PAD
        draw_y = body_top
        i = 0
        while i < visible_lines:
            src_i = self._overlay_scroll + i
            if src_i >= len(wrapped):
                break
            print(wrapped[src_i], body_x, draw_y, Color.LIGHT_GREY)
            draw_y += self._OVERLAY_BODY_LINE_STEP
            i += 1
        if max_scroll > 0:
            up_color = Color.DARK_GREY
            down_color = Color.DARK_GREY
            if self._overlay_scroll > 0:
                up_color = Color.LIGHT_GREY
            if self._overlay_scroll < max_scroll:
                down_color = Color.LIGHT_GREY
            print("^", x + w - 9, body_top, up_color)
            print("v", x + w - 9, body_top +
                  (visible_lines - 1) * self._OVERLAY_BODY_LINE_STEP, down_color)

    def _overlay_body_lines_for(self, overlay_id: int) -> list[str]:
        if overlay_id == self._OVERLAY_CONTROLS:
            lines, _ = self._controls_overlay_lines()
            return lines
        if overlay_id == self._OVERLAY_CREDITS:
            return self._credits_overlay_lines()
        if overlay_id == self._OVERLAY_NEW_GAME_CONFIRM:
            return self._new_game_overlay_lines()
        return []

    def _overlay_layout(self) -> OverlayLayout:
        layout = self._OVERLAY_LAYOUTS.get(self._overlay)
        if layout is None:
            return self._OVERLAY_LAYOUT_DEFAULT
        return layout

    def _overlay_footer_state(self, layout: OverlayLayout) -> tuple[list[str], list[bool], int]:
        button_bg_color = ui_overlay_layout_int(layout, "footer_bg_color", 0)
        nav_enabled = self._overlay_footer_nav_enabled(layout)
        slot_count = ui_overlay_layout_slot_count(layout)
        slot_nav, slot_confirm, slot_cancel = ui_footer_slot_indices(
            layout, slot_count)
        slots = self._overlay_footer_slots(layout, slot_count)
        keyboard_active: list[bool] = []
        i = 0
        while i < slot_count:
            keyboard_active.append(False)
            i += 1
        if nav_enabled:
            keyboard_active[slot_nav] = self._overlay_nav_any_down()
        keyboard_active[slot_confirm] = self._state.controls.down(
            Action.CONFIRM)
        keyboard_active[slot_cancel] = self._state.controls.down(Action.CANCEL)
        return slots, keyboard_active, button_bg_color

    def _overlay_footer_slots(self, layout: OverlayLayout, slot_count: int) -> list[str]:
        if self._overlay == self._OVERLAY_NEW_GAME_CONFIRM:
            return ui_footer_slots_standard(
                layout,
                slot_count,
                self._state,
                Action.CONFIRM,
                Action.CANCEL,
                False,
                "",
                "CONFIRM",
                "CANCEL"
            )
        if self._overlay == self._OVERLAY_CONTROLS:
            return ui_footer_slots_standard(
                layout,
                slot_count,
                self._state,
                Action.CONFIRM,
                Action.CANCEL,
                True,
                "NAV",
                "SAVE",
                "CANCEL"
            )
        nav_enabled = self._overlay_max_scroll(
            self._overlay_body_lines_for(self._overlay), layout) > 0
        return ui_footer_slots_standard(
            layout,
            slot_count,
            self._state,
            Action.CONFIRM,
            Action.CANCEL,
            nav_enabled,
            "NAV",
            "",
            "CLOSE"
        )

    def _overlay_footer_nav_enabled(self, layout: OverlayLayout) -> bool:
        if self._overlay == self._OVERLAY_CONTROLS:
            return True
        if self._overlay == self._OVERLAY_NONE:
            return False
        lines = self._overlay_body_lines_for(self._overlay)
        return self._overlay_max_scroll(lines, layout) > 0

    def _overlay_max_chars_per_line(self, layout: OverlayLayout | None = None) -> int:
        if layout is None:
            layout = self._overlay_layout()
        box_w = ui_overlay_layout_int(layout, "box_w", 200)
        chars = int((box_w - self._OVERLAY_BODY_X_PAD * 2) / 6)
        if chars < 8:
            return 8
        return chars

    def _overlay_visible_lines(self, layout: OverlayLayout | None = None) -> int:
        if layout is None:
            layout = self._overlay_layout()
        footer_line_y, _footer_text_y = ui_overlay_footer_positions(
            layout,
            104,
            108
        )
        body_top = ui_overlay_layout_int(layout, "body_top", 54)
        footer_cutoff = footer_line_y - 4
        body_h = footer_cutoff - body_top
        count = int(body_h / self._OVERLAY_BODY_LINE_STEP)
        if count < 1:
            return 1
        return count

    def _overlay_wrap_lines(
        self,
        lines: list[str],
        layout: OverlayLayout | None = None
    ) -> list[str]:
        max_chars = self._overlay_max_chars_per_line(layout)
        out: list[str] = []
        i = 0
        while i < len(lines):
            raw = str(lines[i])
            if raw == "":
                out.append("")
                i += 1
                continue
            rest = raw
            while len(rest) > max_chars:
                cut = max_chars
                probe = cut
                while probe > 0 and rest[probe - 1] != " ":
                    probe -= 1
                if probe < int(max_chars * 0.55):
                    probe = cut
                part = rest[:probe]
                part = part.strip()
                if part == "":
                    part = rest[:cut]
                    probe = cut
                out.append(part)
                rest = rest[probe:]
                rest = rest.lstrip()
            out.append(rest)
            i += 1
        return out

    def _overlay_max_scroll(
        self,
        lines: list[str],
        layout: OverlayLayout | None = None
    ) -> int:
        wrapped = self._overlay_wrap_lines(lines, layout)
        max_scroll = len(wrapped) - self._overlay_visible_lines(layout)
        if max_scroll < 0:
            return 0
        return max_scroll

    def _clamp_overlay_scroll(
        self,
        lines: list[str],
        layout: OverlayLayout | None = None
    ) -> None:
        max_scroll = self._overlay_max_scroll(lines, layout)
        if self._overlay_scroll < 0:
            self._overlay_scroll = 0
            return
        if self._overlay_scroll > max_scroll:
            self._overlay_scroll = max_scroll

    def _draw_controls_overlay(self) -> None:
        layout = self._overlay_layout()
        slots, keyboard_active, button_bg_color = self._overlay_footer_state(
            layout)
        x, _y, w, _h, body_top, footer_line_y, _footer_text_y = ui_overlay_screen_draw(
            self._ui,
            layout,
            "OPTIONS",
            [],
            slots,
            keyboard_active,
            theme=ui_overlay_theme_inverted(),
            body_line_step=self._OVERLAY_BODY_LINE_STEP,
            button_bg_color=button_bg_color
        )
        line_step = 7
        body_x = x + self._OVERLAY_BODY_X_PAD
        self._draw_controls_overlay_settings(
            layout, body_x, body_top, line_step)
        info_top = body_top + line_step * self._options.row_count() + 5
        line(body_x, info_top - 2, x + w - 9, info_top - 2, Color.DARK_GREY)
        self._draw_controls_overlay_bindings_table(
            layout, body_x, info_top, footer_line_y
        )

    def _draw_controls_overlay_settings(
        self,
        layout: OverlayLayout,
        body_x: int,
        body_top: int,
        line_step: int
    ) -> None:
        selected_row = self._options.focus_row
        row_count = self._options.row_count()
        if selected_row < 0 or selected_row >= row_count:
            selected_row = 0
        left_arrow = self._controls_keyboard_nav_arrow(Action.NAV_LEFT)
        right_arrow = self._controls_keyboard_nav_arrow(Action.NAV_RIGHT)
        right_gap_comp = -1
        labels: list[str] = []
        values: list[str] = []
        enabled_rows: list[bool] = []
        active_rows: list[bool] = []
        row = 0
        while row < row_count:
            enabled = self._controls_setting_enabled(row)
            selected = row == selected_row
            labels.append(self._controls_setting_label(row))
            values.append(self._controls_setting_value(row))
            enabled_rows.append(enabled)
            active_rows.append(
                self._controls_setting_row_active(row, selected, enabled)
            )
            row += 1
        ui_options_settings_draw(
            layout,
            body_x,
            body_top,
            line_step,
            self._OVERLAY_BODY_X_PAD,
            selected_row,
            labels,
            values,
            enabled_rows,
            active_rows,
            left_arrow,
            right_arrow,
            right_gap_comp,
            "CONTROL MODE:",
            Color.DARK_GREY,
            Color.LIGHT_GREY,
            Color.YELLOW,
            Color.WHITE
        )

    def _controls_setting_label(self, row: int) -> str:
        return self._options.setting_label(row)

    def _controls_setting_value(self, row: int) -> str:
        return self._options.setting_value(row)

    def _controls_setting_enabled(self, row: int) -> bool:
        return self._options.setting_enabled(row)

    def _controls_setting_row_active(self, row: int, selected: bool, enabled: bool) -> bool:
        if self._overlay != self._OVERLAY_CONTROLS:
            return False
        mouse_active = (
            self._mouse_left_down
            and self._controls_mouse_down_row == row
            and self._controls_mouse_hover_row == row
        )
        mouse_right_active = (
            self._mouse_right_down
            and self._controls_mouse_right_down_row == row
            and self._controls_mouse_hover_row == row
        )
        if mouse_active:
            return True
        if mouse_right_active:
            return True
        if not selected:
            return False
        if not enabled:
            return False
        return bool(
            self._state.controls.down(Action.NAV_LEFT)
            or self._state.controls.down(Action.NAV_RIGHT)
        )

    def _controls_setting_row_at(self, layout: OverlayLayout, mx: int, my: int) -> int:
        return ui_options_settings_row_at(
            layout,
            self._OVERLAY_BODY_X_PAD,
            7,
            self._options.row_count(),
            mx,
            my
        )

    def _controls_setting_dir_at(
        self,
        layout: OverlayLayout,
        row: int,
        mx: int,
        my: int
    ) -> int:
        left_arrow = self._controls_keyboard_nav_arrow(Action.NAV_LEFT)
        right_arrow = self._controls_keyboard_nav_arrow(Action.NAV_RIGHT)
        return ui_options_settings_dir_at(
            layout,
            self._OVERLAY_BODY_X_PAD,
            7,
            row,
            self._controls_setting_enabled(row),
            self._controls_setting_value(row),
            left_arrow,
            right_arrow,
            -1,
            "CONTROL MODE:",
            mx,
            my
        )

    def _draw_controls_overlay_bindings_table(
        self,
        layout: OverlayLayout,
        body_x: int,
        area_top: int,
        footer_line_y: int
    ) -> None:
        left_rows: list[tuple[str, str]] = [
            ("NAVIGATION", self._controls_prompt_nav()),
            ("CONFIRM", self._controls_prompt_for_action(Action.CONFIRM)),
            ("CANCEL", self._controls_prompt_for_action(Action.CANCEL))
        ]
        system_rows: list[tuple[str, str]] = [
            ("CRT TOGGLE", self._controls_prompt_for_crt_filter())
        ]
        right_rows: list[tuple[str, str]] = [
            ("STEER", self._controls_prompt_for_steer()),
            ("THROTTLE", self._controls_prompt_for_action(Action.THROTTLE)),
            ("BRAKE", self._controls_prompt_for_action(Action.BRAKE)),
            ("HANDBRAKE", self._controls_prompt_for_action(Action.HANDBRAKE)),
            ("SKILL", self._controls_prompt_for_action(Action.SKILL))
        ]
        left_sections: list[tuple[str, list[tuple[str, str]]]] = []
        if len(system_rows) > 0:
            left_sections.append(("SYSTEM", system_rows))
        left_sections.append(("MENU", left_rows))
        right_sections: list[tuple[str, list[tuple[str, str]]]] = [
            ("DRIVING", right_rows)
        ]
        ui_options_bindings_table_draw(
            layout,
            body_x,
            area_top,
            footer_line_y,
            left_sections,
            right_sections,
            Color.WHITE,
            Color.LIGHT_GREY,
            Color.DARK_GREY
        )

    def _draw_credits_overlay(self) -> None:
        self._draw_overlay_box("CREDITS", self._credits_overlay_lines())

    def _draw_new_game_overlay(self) -> None:
        self._draw_overlay_box("CONFIRM RESET", self._new_game_overlay_lines())

    def _controls_overlay_lines(self) -> tuple[list[str], list[int]]:
        menu_nav = ui_prompt_with_text(
            self._controls_prompt_nav(), "NAVIGATION")
        menu_ok = ui_prompt_with_text(
            self._controls_prompt_for_action(Action.CONFIRM), "CONFIRM")
        menu_back = ui_prompt_with_text(
            self._controls_prompt_for_action(Action.CANCEL), "CANCEL")

        drive_steer = ui_prompt_with_text(
            self._controls_prompt_for_steer(), "STEER")
        drive_gas = ui_prompt_with_text(
            self._controls_prompt_for_action(Action.THROTTLE), "THROTTLE")
        drive_brk = ui_prompt_with_text(
            self._controls_prompt_for_action(Action.BRAKE), "BRAKE")
        drive_aux = ui_prompt_gap_join([
            ui_prompt_with_text(self._controls_prompt_for_action(
                Action.HANDBRAKE), "HANDBRAKE"),
            ui_prompt_with_text(
                self._controls_prompt_for_action(Action.SKILL), "SKILL")
        ])

        lines = [
            "MENU",
            menu_nav,
            menu_ok,
            menu_back,
            "DRIVING",
            drive_steer,
            drive_gas,
            drive_brk,
            drive_aux
        ]
        colors: list[int] = [
            int(Color.WHITE),
            int(Color.LIGHT_GREY),
            int(Color.LIGHT_GREY),
            int(Color.LIGHT_GREY),
            int(Color.WHITE),
            int(Color.LIGHT_GREY),
            int(Color.LIGHT_GREY),
            int(Color.LIGHT_GREY),
            int(Color.LIGHT_GREY)
        ]
        return lines, colors

    def _controls_prompt_for_action(self, action_id: int) -> str:
        glyphs = prompt_glyphs_for_action(action_id, self._options.mode_draft)
        if not self._options.shoulders_draft:
            glyphs = filter_prompt_glyphs(glyphs, False)
        return format_prompt(glyphs, self._state.prompt_glyph_detail)

    def _controls_prompt_nav(self) -> str:
        glyphs = prompt_glyphs_for_nav_hint(self._options.mode_draft)
        return format_prompt(glyphs, self._state.prompt_glyph_detail)

    def _controls_prompt_for_steer(self) -> str:
        left = self._controls_prompt_for_action(Action.NAV_LEFT)
        right = self._controls_prompt_for_action(Action.NAV_RIGHT)
        return ui_prompt_gap_join([left, right])

    def _controls_keyboard_nav_arrow(self, action_id: int) -> str:
        glyphs = prompt_glyphs_for_action(action_id, InputDeviceMode.KEYBOARD)
        if len(glyphs) <= 0:
            return ""
        return format_prompt([glyphs[0]], self._state.prompt_glyph_detail)

    def _controls_prompt_for_crt_filter(self) -> str:
        return format_prompt(
            [PromptGlyph.KEY_F6],
            self._state.prompt_glyph_detail
        )

    @staticmethod
    def _credits_overlay_lines() -> list[str]:
        return [
            "WYRDWAY",
            "A GAME BY MARAT AZIZOV",
            "",
            "DESIGN / CODE / ART",
            "ETOMARAT",
            "",
            "THANKS FOR PLAYING"
        ]

    @staticmethod
    def _new_game_overlay_lines() -> list[str]:
        return [
            "START NEW GAME?",
            "CURRENT PROFILE PROGRESS",
            "WILL BE RESET",
            "",
            "THIS CANNOT BE UNDONE"
        ]


def make_main_menu_scene(nav: SceneNavigator) -> MainMenuScene:
    return MainMenuScene(nav)
