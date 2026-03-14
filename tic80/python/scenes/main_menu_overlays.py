from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import line, print, rect

    from ..core.campaign_seed import (
        generate_seed_text_default,
        normalize_seed_text,
        seed_cycle_char,
        seed_text_max_len
    )
    from ..core.controls.actions import Action, ActionId
    from ..core.controls.modes import InputDeviceMode, InputDeviceModeId
    from ..core.controls.prompts import (
        PromptGlyph,
        filter_prompt_glyphs,
        format_prompt,
        prompt_glyphs_for_action,
        prompt_glyphs_for_nav_hint
    )
    from ..core.drive_presets import (
        DrivePresetId,
        drive_preset_cycle,
        drive_preset_label
    )
    from ..core.game_state import GameState
    from ..core.palette import Color
    from ..core.ui.modal_spec import (
        UiModalFooterSpec,
        UiModalNavMode,
        UiModalSpec
    )
    from ..core.ui.options_bindings_table import ui_options_bindings_table_draw
    from ..core.ui.options_overlay_state import UiOptionsOverlayState
    from ..core.ui.options_settings import (
        ui_options_settings_draw,
        ui_options_settings_row_at
    )
    from ..core.ui.overlay_layout import (
        FOOTER_PAD_PROFILE_DEFAULT,
        FOOTER_PAD_PROFILE_INVERTED,
        OverlayLayout,
        ui_overlay_layout_int
    )
    from ..core.ui.overlay_screen import ui_overlay_screen_draw
    from ..core.ui.overlay_theme import ui_overlay_theme_inverted
    from ..core.ui.prompts import (
        ui_prompt_for_action,
        ui_prompt_gap_join,
        ui_prompt_with_text
    )
    from ..core.ui.rich_text import ui_rich_print, ui_rich_text_width
    from .main_menu_scene import MainMenuScene


MAIN_MENU_OVERLAY_NONE = 0
MAIN_MENU_OVERLAY_CONTROLS = 1
MAIN_MENU_OVERLAY_CREDITS = 2
MAIN_MENU_OVERLAY_NEW_GAME_CONFIRM = 3
MAIN_MENU_OVERLAY_NEW_GAME_SETUP = 4
MAIN_MENU_OVERLAY_NEW_GAME_SEED = 5


def _menu_overlay_layout(
    box_x: int,
    box_y: int,
    box_w: int,
    box_h: int,
    header_text_y: int,
    body_top: int,
    slot_count: int,
    slot_weights: tuple[int, ...],
    slot_nav: int,
    slot_confirm: int,
    slot_cancel: int,
    footer_pad_profile: int,
    footer_line_gap: int = 4,
    footer_bg_color: int = 0,
    footer_button_top_pad: int = -1
) -> OverlayLayout:
    layout: OverlayLayout = {
        "box_x": int(box_x),
        "box_y": int(box_y),
        "box_w": int(box_w),
        "box_h": int(box_h),
        "header_text_y": int(header_text_y),
        "body_top": int(body_top),
        "footer_pad_profile": int(footer_pad_profile),
        "footer_line_gap": int(footer_line_gap),
        "footer_bg_color": int(footer_bg_color),
        "slot_count": int(slot_count),
        "slot_weights": slot_weights,
        "slot_nav": int(slot_nav),
        "slot_confirm": int(slot_confirm),
        "slot_cancel": int(slot_cancel)
    }
    if footer_button_top_pad >= 0:
        layout["footer_button_top_pad"] = int(footer_button_top_pad)
    return layout


def main_menu_overlay_default_layout() -> OverlayLayout:
    return _menu_overlay_layout(
        20,
        28,
        200,
        90,
        37,
        54,
        4,
        (1, 1, 1, 1),
        0,
        2,
        3,
        FOOTER_PAD_PROFILE_DEFAULT
    )


class MainMenuOverlayFlow:
    def on_open(self, scene: MainMenuScene, prev_overlay_id: int) -> None:
        return

    def on_close(self, scene: MainMenuScene) -> None:
        return

    def body_lines(self) -> list[str]:
        return []

    def update(
        self,
        scene: MainMenuScene,
        nav_up_released: bool,
        nav_down_released: bool,
        nav_left_released: bool,
        nav_right_released: bool,
        confirm_released: bool,
        cancel_released: bool,
        secondary_released: bool,
        mouse_nav_released: bool
    ) -> None:
        return

    def draw(self, scene: MainMenuScene, body_x_pad: int, body_line_step: int) -> None:
        return


class MainMenuOverlayDef:
    def __init__(
        self,
        spec: UiModalSpec,
        flow: MainMenuOverlayFlow
    ) -> None:
        self.spec = spec
        self.flow = flow


class MainMenuNewGameFlow:
    ACTION_NONE = 0
    ACTION_CLOSE = 1
    ACTION_OPEN_SEED = 2
    ACTION_START = 3
    ACTION_RETURN_SETUP = 4

    ROW_DIFFICULTY = 0
    ROW_MODE = 1
    ROW_SEED = 2
    ROW_START = 3
    ROW_COUNT = 4

    def __init__(
        self,
        mode: InputDeviceModeId,
        preset: DrivePresetId
    ) -> None:
        self.focus_row = self.ROW_DIFFICULTY
        self.mode_draft: InputDeviceModeId = mode
        self.preset_draft: DrivePresetId = preset
        seed = normalize_seed_text(generate_seed_text_default())
        max_len = seed_text_max_len()
        if len(seed) > max_len:
            seed = seed[:max_len]
        self.seed_text = seed
        self.seed_cursor = 0
        self.seed_snapshot = seed

    def reset_draft(
        self,
        mode: InputDeviceModeId,
        preset: DrivePresetId
    ) -> None:
        self.focus_row = self.ROW_DIFFICULTY
        self.mode_draft = mode
        self.preset_draft = preset
        seed = normalize_seed_text(generate_seed_text_default())
        max_len = seed_text_max_len()
        if len(seed) > max_len:
            seed = seed[:max_len]
        self.seed_text = seed
        self.seed_cursor = 0
        self.seed_snapshot = seed

    def mode_label(self) -> str:
        mode = self.mode_draft
        if mode == InputDeviceMode.KEYBOARD:
            return "KEYBOARD"
        if mode == InputDeviceMode.GAMEPAD:
            return "GAMEPAD"
        return "DUAL INPUT"

    def setup_rows(self) -> list[tuple[str, str, int]]:
        return [
            ("DIFFICULTY:", drive_preset_label(
                self.preset_draft), self.ROW_DIFFICULTY),
            ("CONTROL MODE:", self.mode_label(), self.ROW_MODE),
            ("SEED:", self.seed_text, self.ROW_SEED),
            ("START:", "START GAME", self.ROW_START)
        ]

    def apply_setup_row_click(self, row_id: int, reverse: bool) -> int:
        row = int(row_id)
        if row < self.ROW_DIFFICULTY or row > self.ROW_START:
            return self.ACTION_NONE
        self.focus_row = row
        if row == self.ROW_DIFFICULTY:
            self.preset_draft = drive_preset_cycle(self.preset_draft, not reverse)
            return self.ACTION_NONE
        if row == self.ROW_MODE:
            self._cycle_mode(not reverse)
            return self.ACTION_NONE
        if reverse:
            return self.ACTION_NONE
        if row == self.ROW_SEED:
            return self.ACTION_OPEN_SEED
        if row == self.ROW_START:
            return self.ACTION_START
        return self.ACTION_NONE

    def update_setup_input(
        self,
        nav_up_released: bool,
        nav_down_released: bool,
        nav_left_released: bool,
        nav_right_released: bool,
        confirm_released: bool,
        cancel_released: bool,
        mouse_nav_released: bool
    ) -> int:
        if mouse_nav_released:
            nav_down_released = True
        if nav_up_released:
            self.focus_row -= 1
        elif nav_down_released:
            self.focus_row += 1
        if self.focus_row < 0:
            self.focus_row = self.ROW_COUNT - 1
        elif self.focus_row >= self.ROW_COUNT:
            self.focus_row = 0

        if self.focus_row == self.ROW_DIFFICULTY:
            if nav_left_released:
                self.preset_draft = drive_preset_cycle(self.preset_draft, True)
            elif nav_right_released:
                self.preset_draft = drive_preset_cycle(
                    self.preset_draft, False)
        elif self.focus_row == self.ROW_MODE:
            if nav_left_released:
                self._cycle_mode(True)
            elif nav_right_released:
                self._cycle_mode(False)

        if cancel_released:
            return self.ACTION_CLOSE
        if not confirm_released:
            return self.ACTION_NONE

        if self.focus_row == self.ROW_SEED:
            return self.ACTION_OPEN_SEED
        if self.focus_row == self.ROW_START:
            return self.ACTION_START
        if self.focus_row == self.ROW_DIFFICULTY:
            self.preset_draft = drive_preset_cycle(self.preset_draft, True)
            return self.ACTION_NONE
        if self.focus_row == self.ROW_MODE:
            self._cycle_mode(True)
        return self.ACTION_NONE

    def update_seed_input(
        self,
        nav_up_released: bool,
        nav_down_released: bool,
        nav_left_released: bool,
        nav_right_released: bool,
        confirm_released: bool,
        cancel_released: bool,
        secondary_released: bool
    ) -> int:
        if nav_left_released:
            self.seed_cursor -= 1
            self._clamp_seed_cursor()
        elif nav_right_released:
            self.seed_cursor += 1
            self._clamp_seed_cursor()
        if nav_up_released:
            self._cycle_seed_char(True)
        elif nav_down_released:
            self._cycle_seed_char(False)
        if secondary_released:
            self.seed_text = normalize_seed_text(
                generate_seed_text_default()
            )
            self._clamp_seed_cursor()
        if cancel_released:
            self.seed_text = self.seed_snapshot
            return self.ACTION_RETURN_SETUP
        if confirm_released:
            self.seed_text = normalize_seed_text(self.seed_text)
            return self.ACTION_RETURN_SETUP
        return self.ACTION_NONE

    def prepare_seed_overlay(self) -> None:
        self.seed_snapshot = self.seed_text
        self._clamp_seed_cursor()

    def seed_cursor_index(self) -> int:
        seed = self.seed_text
        if seed == "":
            return 0
        idx = self.seed_cursor
        if idx < 0:
            return 0
        if idx >= len(seed):
            return len(seed) - 1
        return idx

    @staticmethod
    def info_lines() -> list[str]:
        return [
            "CONTROL MODE and DIFFICULTY", "can be changed later in OPTIONS",
        ]

    def update_setup_overlay_input(
        self,
        scene: MainMenuScene,
        nav_up_released: bool,
        nav_down_released: bool,
        nav_left_released: bool,
        nav_right_released: bool,
        confirm_released: bool,
        cancel_released: bool,
        mouse_nav_released: bool
    ) -> None:
        action = self.update_setup_input(
            nav_up_released,
            nav_down_released,
            nav_left_released,
            nav_right_released,
            confirm_released,
            cancel_released,
            mouse_nav_released
        )
        if action == self.ACTION_CLOSE:
            scene._close_overlay()
            return
        if action == self.ACTION_OPEN_SEED:
            scene._open_new_game_seed_overlay()
            return
        if action == self.ACTION_START:
            scene._start_new_campaign_from_setup()

    def update_seed_overlay_input(
        self,
        scene: MainMenuScene,
        nav_up_released: bool,
        nav_down_released: bool,
        nav_left_released: bool,
        nav_right_released: bool,
        confirm_released: bool,
        cancel_released: bool,
        secondary_released: bool
    ) -> None:
        action = self.update_seed_input(
            nav_up_released,
            nav_down_released,
            nav_left_released,
            nav_right_released,
            confirm_released,
            cancel_released,
            secondary_released
        )
        if action == self.ACTION_RETURN_SETUP:
            scene._open_overlay(scene._OVERLAY_NEW_GAME_SETUP)

    def draw_setup_overlay(
        self,
        scene: MainMenuScene,
        body_x_pad: int,
        body_line_step: int
    ) -> None:
        layout = scene._overlay_layout()
        slots, keyboard_active, button_bg_color = scene._overlay_footer_state(
            layout)
        x, _y, w, _h, body_top, _footer_line_y, _footer_text_y = ui_overlay_screen_draw(
            scene._overlay_ui.runtime,
            layout,
            scene._overlay_title("NEW GAME SETUP"),
            [],
            slots,
            keyboard_active,
            body_line_step=body_line_step,
            button_bg_color=button_bg_color
        )
        body_x = x + body_x_pad
        row_step = 8
        left_arrow = self._setup_nav_arrow(scene, Action.NAV_LEFT)
        right_arrow = self._setup_nav_arrow(scene, Action.NAV_RIGHT)
        rows = self.setup_rows()
        i = 0
        while i < len(rows):
            label, value, row_id = rows[i]
            self._draw_setup_row(
                body_x,
                body_top + row_step * i,
                label,
                value,
                row_id,
                left_arrow,
                right_arrow
            )
            i += 1
        info = scene._overlay_wrap_lines(self.info_lines(), layout)
        info_y = body_top + row_step * 5
        i = 0
        while i < len(info):
            print(info[i], body_x, info_y, Color.GREY)
            info_y += row_step
            i += 1
            if i >= 2:
                break

    def draw_seed_overlay(
        self,
        scene: MainMenuScene,
        body_x_pad: int,
        body_line_step: int
    ) -> None:
        layout = scene._overlay_layout()
        slots, keyboard_active, button_bg_color = scene._overlay_footer_state(
            layout)
        x, _y, _w, _h, body_top, _footer_line_y, _footer_text_y = ui_overlay_screen_draw(
            scene._overlay_ui.runtime,
            layout,
            scene._overlay_title("SEED EDITOR"),
            [],
            slots,
            keyboard_active,
            body_line_step=body_line_step,
            button_bg_color=button_bg_color
        )
        body_x = x + body_x_pad
        seed_x = body_x + 36
        print("SEED:", body_x, body_top, Color.LIGHT_GREY)
        self._draw_seed_value(seed_x, body_top)
        random_hint = ui_prompt_with_text(
            ui_prompt_for_action(scene._state, Action.SECONDARY),
            "RANDOM"
        )
        ui_rich_print(random_hint, seed_x, body_top + 10,
                      Color.LIGHT_GREY, fixed=True)

    def start_campaign(self, state: GameState) -> None:
        seed = normalize_seed_text(self.seed_text)
        max_len = seed_text_max_len()
        if len(seed) > max_len:
            seed = seed[:max_len]
        state.set_input_device_mode(self.mode_draft)
        state.set_drive_preset_id(self.preset_draft)
        rumble_supported = state.refresh_rumble_support()
        mode = self.mode_draft
        if mode == InputDeviceMode.KEYBOARD:
            state.set_prompt_show_shoulders(False)
            state.set_vibration_enabled(False)
        elif mode == InputDeviceMode.BOTH:
            state.set_prompt_show_shoulders(False)
            if not state.options_vibration_configured:
                state.set_vibration_enabled(rumble_supported)
            if not rumble_supported:
                state.set_vibration_enabled(False)
        else:
            if not state.options_shoulders_configured:
                state.set_prompt_show_shoulders(rumble_supported)
            if not state.options_vibration_configured:
                state.set_vibration_enabled(rumble_supported)
            if not rumble_supported:
                state.set_vibration_enabled(False)
        state.save_options()
        state.start_new_campaign(seed)

    def _cycle_mode(self, forward: bool) -> None:
        modes: list[InputDeviceModeId] = [
            InputDeviceMode.KEYBOARD,
            InputDeviceMode.GAMEPAD,
            InputDeviceMode.BOTH
        ]
        idx = 0
        i = 0
        current = int(self.mode_draft)
        while i < len(modes):
            if int(modes[i]) == current:
                idx = i
                break
            i += 1
        if forward:
            idx += 1
            if idx >= len(modes):
                idx = 0
        else:
            idx -= 1
            if idx < 0:
                idx = len(modes) - 1
        self.mode_draft = modes[idx]

    def _cycle_seed_char(self, forward: bool) -> None:
        text = self.seed_text
        if text == "":
            text = normalize_seed_text(generate_seed_text_default())
        if self.seed_cursor < 0:
            self.seed_cursor = 0
        if self.seed_cursor >= len(text):
            self.seed_cursor = len(text) - 1
        if self.seed_cursor < 0:
            self.seed_cursor = 0
        i = self.seed_cursor
        head = text[:i]
        ch = text[i]
        tail = text[i + 1:]
        self.seed_text = head + seed_cycle_char(ch, forward) + tail

    def _clamp_seed_cursor(self) -> None:
        n = len(self.seed_text)
        if n <= 0:
            self.seed_cursor = 0
            return
        if self.seed_cursor < 0:
            self.seed_cursor = 0
            return
        if self.seed_cursor >= n:
            self.seed_cursor = n - 1

    def _draw_setup_row(
        self,
        x: int,
        y: int,
        label: str,
        value: str,
        row_id: int,
        left_arrow: str,
        right_arrow: str
    ) -> None:
        selected = self.focus_row == row_id
        if selected:
            rect(x - 1, y - 2, 184, 9, Color.BLACK)
        label_color = Color.LIGHT_GREY
        value_color = Color.WHITE
        if selected:
            label_color = Color.YELLOW
            value_color = Color.YELLOW
        print(label, x, y, label_color)
        show_adjust_hints = (
            selected
            and row_id != self.ROW_SEED
            and row_id != self.ROW_START
            and left_arrow != ""
            and right_arrow != ""
        )
        left_w = ui_rich_text_width(left_arrow)
        right_w = ui_rich_text_width(right_arrow)
        left_gap = ui_rich_text_width("{gap}")
        right_gap = ui_rich_text_width("{gap}")
        right_gap_comp = -1
        left_reserve = left_w + left_gap
        right_reserve = right_w + right_gap
        value_w = self._mono_text_width(value)
        value_x = x + 180 - right_reserve + right_gap_comp - value_w
        min_value_x = x + 72 + left_reserve
        if value_x < min_value_x:
            value_x = min_value_x
        print(value, value_x, y, value_color, fixed=True)
        if show_adjust_hints:
            left_x = value_x - left_reserve
            right_x = value_x + value_w + right_gap + right_gap_comp
            ui_rich_print(left_arrow, left_x, y, value_color, fixed=True)
            ui_rich_print(right_arrow, right_x, y, value_color, fixed=True)

    def _draw_seed_value(self, x: int, y: int) -> None:
        seed = self.seed_text
        if seed == "":
            return
        idx = self.seed_cursor_index()
        cell_x = x + idx * 6
        rect(cell_x - 1, y - 1, 7, 8, Color.BLACK)
        print(seed, x, y, Color.WHITE, fixed=True)
        print(seed[idx], cell_x, y, Color.YELLOW, fixed=True)
        line(cell_x, y + 6, cell_x + 5, y + 6, Color.YELLOW)

    def _setup_nav_arrow(self, scene: MainMenuScene, action_id: ActionId) -> str:
        glyphs = prompt_glyphs_for_action(action_id, self.mode_draft)
        if not glyphs:
            return ""
        return format_prompt([glyphs[0]], scene._state.prompt_glyph_detail)

    @staticmethod
    def _mono_text_width(text: str) -> int:
        return len(str(text)) * 6


class MainMenuNewGameSetupOverlayFlow(MainMenuOverlayFlow):
    _BODY_X_PAD = 8
    _ROW_STEP = 8
    _ROW_W = 184

    def __init__(self, flow: MainMenuNewGameFlow, seed_overlay_id: int) -> None:
        self._flow = flow
        self._seed_overlay_id = int(seed_overlay_id)
        self._mouse_hover_row = -1
        self._mouse_down_row = -1
        self._mouse_right_down_row = -1

    def on_open(self, scene: MainMenuScene, prev_overlay_id: int) -> None:
        self.reset_mouse_state()
        if prev_overlay_id == self._seed_overlay_id:
            return
        self._flow.reset_draft(
            scene._state.input_device_mode,
            scene._state.drive_preset_id
        )

    def on_close(self, scene: MainMenuScene) -> None:
        self.reset_mouse_state()

    def reset_mouse_state(self) -> None:
        self._mouse_hover_row = -1
        self._mouse_down_row = -1
        self._mouse_right_down_row = -1

    def body_lines(self) -> list[str]:
        return self._flow.info_lines()

    def update(
        self,
        scene: MainMenuScene,
        nav_up_released: bool,
        nav_down_released: bool,
        nav_left_released: bool,
        nav_right_released: bool,
        confirm_released: bool,
        cancel_released: bool,
        secondary_released: bool,
        mouse_nav_released: bool
    ) -> None:
        self._update_mouse_state(scene)
        mouse_action = self._poll_mouse_setup_release(scene)
        if mouse_action == self._flow.ACTION_OPEN_SEED:
            scene._open_new_game_seed_overlay()
            return
        if mouse_action == self._flow.ACTION_START:
            scene._start_new_campaign_from_setup()
            return
        self._flow.update_setup_overlay_input(
            scene,
            nav_up_released,
            nav_down_released,
            nav_left_released,
            nav_right_released,
            confirm_released,
            cancel_released,
            mouse_nav_released
        )

    def draw(self, scene: MainMenuScene, body_x_pad: int, body_line_step: int) -> None:
        self._flow.draw_setup_overlay(scene, body_x_pad, body_line_step)

    def _update_mouse_state(self, scene: MainMenuScene) -> None:
        hover_row = self._setup_row_at(scene, scene._mouse_x, scene._mouse_y)
        self._mouse_hover_row = hover_row
        if hover_row >= 0:
            self._flow.focus_row = hover_row
        if scene._mouse_left_pressed:
            self._mouse_down_row = hover_row
        if scene._mouse_right_pressed:
            self._mouse_right_down_row = hover_row
        if not scene._mouse_left_down and not scene._mouse_left_released:
            self._mouse_down_row = -1
        if not scene._mouse_right_down and not scene._mouse_right_released:
            self._mouse_right_down_row = -1

    def _poll_mouse_setup_release(self, scene: MainMenuScene) -> int:
        hover_row = self._mouse_hover_row
        if scene._mouse_left_released:
            down_row = self._mouse_down_row
            self._mouse_down_row = -1
            if down_row >= 0 and down_row == hover_row:
                return self._flow.apply_setup_row_click(down_row, True)
            return self._flow.ACTION_NONE
        if scene._mouse_right_released:
            down_row = self._mouse_right_down_row
            self._mouse_right_down_row = -1
            if down_row >= 0 and down_row == hover_row:
                return self._flow.apply_setup_row_click(down_row, False)
        return self._flow.ACTION_NONE

    def _setup_row_at(self, scene: MainMenuScene, mx: int, my: int) -> int:
        layout = scene._overlay_layout()
        body_x = ui_overlay_layout_int(layout, "box_x", 20) + self._BODY_X_PAD
        body_top = ui_overlay_layout_int(layout, "body_top", 44)
        row_x = body_x - 1
        if mx < row_x or mx >= row_x + self._ROW_W:
            return -1
        rows = self._flow.setup_rows()
        i = 0
        while i < len(rows):
            _label, _value, row_id = rows[i]
            row_y = body_top + i * self._ROW_STEP
            if my >= row_y - 2 and my < row_y + 7:
                return row_id
            i += 1
        return -1


class MainMenuNewGameSeedOverlayFlow(MainMenuOverlayFlow):
    def __init__(self, flow: MainMenuNewGameFlow) -> None:
        self._flow = flow

    def on_open(self, scene: MainMenuScene, prev_overlay_id: int) -> None:
        self._flow.prepare_seed_overlay()

    def update(
        self,
        scene: MainMenuScene,
        nav_up_released: bool,
        nav_down_released: bool,
        nav_left_released: bool,
        nav_right_released: bool,
        confirm_released: bool,
        cancel_released: bool,
        secondary_released: bool,
        mouse_nav_released: bool
    ) -> None:
        self._flow.update_seed_overlay_input(
            scene,
            nav_up_released,
            nav_down_released,
            nav_left_released,
            nav_right_released,
            confirm_released,
            cancel_released,
            secondary_released
        )

    def draw(self, scene: MainMenuScene, body_x_pad: int, body_line_step: int) -> None:
        self._flow.draw_seed_overlay(scene, body_x_pad, body_line_step)


class MainMenuControlsOverlayFlow(MainMenuOverlayFlow):
    def __init__(self, state: GameState) -> None:
        self._state = state
        self._options = UiOptionsOverlayState()
        self._mouse_hover_row = -1
        self._mouse_down_row = -1
        self._mouse_right_down_row = -1

    def reset_draft(self) -> None:
        rumble_supported = self._state.refresh_rumble_support()
        self._options.reset_draft(
            self._state.input_device_mode,
            self._state.drive_preset_id,
            self._state.prompt_show_shoulders,
            self._state.vibration_enabled,
            rumble_supported
        )
        self.reset_mouse_state()

    def on_open(self, scene: MainMenuScene, prev_overlay_id: int) -> None:
        self.reset_draft()

    def on_close(self, scene: MainMenuScene) -> None:
        self.reset_mouse_state()

    def reset_mouse_state(self) -> None:
        self._mouse_hover_row = -1
        self._mouse_down_row = -1
        self._mouse_right_down_row = -1

    def body_lines(self) -> list[str]:
        lines, _colors = self._bindings_lines()
        return lines

    def update(
        self,
        scene: MainMenuScene,
        nav_up_released: bool,
        nav_down_released: bool,
        nav_left_released: bool,
        nav_right_released: bool,
        confirm_released: bool,
        cancel_released: bool,
        secondary_released: bool,
        mouse_nav_released: bool
    ) -> None:
        prev_mode = int(self._options.mode_draft)
        self._update_mouse_state(scene)
        self._options.update_from_nav(
            nav_up_released,
            nav_down_released,
            nav_left_released,
            nav_right_released
        )
        if mouse_nav_released:
            self._options.update_from_nav(False, True, False, False)
        self._poll_mouse_setting_release(scene)
        if int(self._options.mode_draft) != prev_mode:
            self._options.set_rumble_supported(self._state.refresh_rumble_support())
        if cancel_released:
            scene._close_overlay()
            return
        if confirm_released:
            self._apply_settings_to_state()
            scene._close_overlay()

    def draw(self, scene: MainMenuScene, body_x_pad: int, body_line_step: int) -> None:
        layout = scene._overlay_layout()
        slots, keyboard_active, button_bg_color = scene._overlay_footer_state(
            layout)
        x, _y, w, _h, body_top, footer_line_y, _footer_text_y = ui_overlay_screen_draw(
            scene._overlay_ui.runtime,
            layout,
            scene._overlay_title("OPTIONS"),
            [],
            slots,
            keyboard_active,
            theme=ui_overlay_theme_inverted(),
            body_line_step=body_line_step,
            button_bg_color=button_bg_color
        )
        line_step = 7
        body_x = x + body_x_pad
        self._draw_settings(
            scene,
            layout,
            body_x,
            body_top,
            line_step,
            body_x_pad
        )
        info_top = body_top + line_step * self._options.row_count() + 5
        line(body_x, info_top - 2, x + w - 9, info_top - 2, Color.DARK_GREY)
        self._draw_bindings_table(
            layout,
            body_x,
            info_top,
            footer_line_y
        )

    def _update_mouse_state(self, scene: MainMenuScene) -> None:
        layout = scene._overlay_layout()
        hover_row = self._setting_row_at(
            layout,
            scene._mouse_x,
            scene._mouse_y
        )
        if hover_row >= 0:
            self._options.focus_row = hover_row
        self._mouse_hover_row = hover_row
        if scene._mouse_left_pressed:
            self._mouse_down_row = hover_row
        if scene._mouse_right_pressed:
            self._mouse_right_down_row = hover_row
        if not scene._mouse_left_down and not scene._mouse_left_released:
            self._mouse_down_row = -1
        if not scene._mouse_right_down and not scene._mouse_right_released:
            self._mouse_right_down_row = -1

    def _poll_mouse_setting_release(self, scene: MainMenuScene) -> None:
        hover_row = self._mouse_hover_row
        if scene._mouse_left_released:
            down_row = self._mouse_down_row
            self._mouse_down_row = -1
            if down_row >= 0 and down_row == hover_row:
                self._options.focus_row = down_row
                if self._options.setting_enabled(down_row):
                    self._options.apply_setting_change(down_row, False)
            return
        if scene._mouse_right_released:
            down_row = self._mouse_right_down_row
            self._mouse_right_down_row = -1
            if down_row < 0 or down_row != hover_row:
                return
            self._options.focus_row = down_row
            if not self._options.setting_enabled(down_row):
                return
            self._options.apply_setting_change(down_row, True)

    def _apply_settings_to_state(self) -> None:
        self._state.set_input_device_mode(self._options.mode_draft)
        self._state.set_drive_preset_id(self._options.drive_preset_draft)
        show_shoulders = (
            self._options.shoulders_draft
            and self._options.shoulders_enabled()
        )
        self._state.set_prompt_show_shoulders(show_shoulders)
        vibration_enabled = (
            self._options.vibration_draft
            and self._options.vibration_enabled()
        )
        self._state.set_vibration_enabled(vibration_enabled)
        self._state.mark_options_configured(
            self._options.shoulders_touched(),
            self._options.vibration_touched()
        )
        self._state.save_options()

    def _draw_settings(
        self,
        scene: MainMenuScene,
        layout: OverlayLayout,
        body_x: int,
        body_top: int,
        line_step: int,
        body_x_pad: int
    ) -> None:
        selected_row = self._options.focus_row
        row_count = self._options.row_count()
        if selected_row < 0 or selected_row >= row_count:
            selected_row = 0
        left_arrow = self._keyboard_nav_arrow(Action.NAV_LEFT)
        right_arrow = self._keyboard_nav_arrow(Action.NAV_RIGHT)
        labels: list[str] = []
        values: list[str] = []
        enabled_rows: list[bool] = []
        active_rows: list[bool] = []
        row = 0
        while row < row_count:
            enabled = self._options.setting_enabled(row)
            selected = row == selected_row
            labels.append(self._options.setting_label(row))
            values.append(self._options.setting_value(row))
            enabled_rows.append(enabled)
            active_rows.append(
                self._setting_row_active(scene, row, selected, enabled)
            )
            row += 1
        ui_options_settings_draw(
            layout,
            body_x,
            body_top,
            line_step,
            body_x_pad,
            selected_row,
            labels,
            values,
            enabled_rows,
            active_rows,
            left_arrow,
            right_arrow,
            -1,
            "CONTROL MODE:",
            Color.DARK_GREY,
            Color.LIGHT_GREY,
            Color.YELLOW,
            Color.WHITE
        )

    def _setting_row_active(
        self,
        scene: MainMenuScene,
        row: int,
        selected: bool,
        enabled: bool
    ) -> bool:
        mouse_active = (
            self._mouse_down_row == row
            and self._mouse_hover_row == row
        )
        mouse_right_active = (
            self._mouse_right_down_row == row
            and self._mouse_hover_row == row
        )
        if mouse_active:
            return True
        if mouse_right_active:
            return True
        if not selected:
            return False
        if not enabled:
            return False
        return (
            scene._overlay_down(Action.NAV_LEFT)
            or scene._overlay_down(Action.NAV_RIGHT)
        )

    def _setting_row_at(self, layout: OverlayLayout, mx: int, my: int) -> int:
        return ui_options_settings_row_at(
            layout,
            8,
            7,
            self._options.row_count(),
            mx,
            my
        )

    def _draw_bindings_table(
        self,
        layout: OverlayLayout,
        body_x: int,
        area_top: int,
        footer_line_y: int
    ) -> None:
        left_rows: list[tuple[str, str]] = [
            ("NAVIGATION", self._prompt_nav()),
            ("CONFIRM", self._prompt_for_action(Action.CONFIRM)),
            ("CANCEL", self._prompt_for_action(Action.CANCEL))
        ]
        system_rows: list[tuple[str, str]] = [
            ("CRT TOGGLE", self._prompt_for_crt_filter())
        ]
        right_rows: list[tuple[str, str]] = [
            ("STEER", self._prompt_for_steer()),
            ("THROTTLE", self._prompt_for_action(Action.THROTTLE)),
            ("BRAKE", self._prompt_for_action(Action.BRAKE)),
            ("HANDBRAKE", self._prompt_for_action(Action.HANDBRAKE)),
            ("MODULE", self._prompt_for_action(Action.MODULE))
        ]
        left_sections: list[tuple[str, list[tuple[str, str]]]] = []
        if system_rows:
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

    def _bindings_lines(self) -> tuple[list[str], list[int]]:
        menu_nav = ui_prompt_with_text(self._prompt_nav(), "NAVIGATION")
        menu_ok = ui_prompt_with_text(
            self._prompt_for_action(Action.CONFIRM),
            "CONFIRM"
        )
        menu_back = ui_prompt_with_text(
            self._prompt_for_action(Action.CANCEL),
            "CANCEL"
        )
        drive_steer = ui_prompt_with_text(self._prompt_for_steer(), "STEER")
        drive_gas = ui_prompt_with_text(
            self._prompt_for_action(Action.THROTTLE),
            "THROTTLE"
        )
        drive_brk = ui_prompt_with_text(
            self._prompt_for_action(Action.BRAKE),
            "BRAKE"
        )
        drive_aux = ui_prompt_gap_join([
            ui_prompt_with_text(
                self._prompt_for_action(Action.HANDBRAKE),
                "HANDBRAKE"
            ),
            ui_prompt_with_text(
                self._prompt_for_action(Action.MODULE),
                "MODULE"
            )
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

    def _prompt_for_action(self, action_id: int) -> str:
        glyphs = prompt_glyphs_for_action(action_id, self._options.mode_draft)
        if not self._options.shoulders_draft:
            glyphs = filter_prompt_glyphs(glyphs, False)
        return format_prompt(glyphs, self._state.prompt_glyph_detail)

    def _prompt_nav(self) -> str:
        glyphs = prompt_glyphs_for_nav_hint(self._options.mode_draft)
        return format_prompt(glyphs, self._state.prompt_glyph_detail)

    def _prompt_for_steer(self) -> str:
        left = self._prompt_for_action(Action.NAV_LEFT)
        right = self._prompt_for_action(Action.NAV_RIGHT)
        return ui_prompt_gap_join([left, right])

    def _keyboard_nav_arrow(self, action_id: int) -> str:
        glyphs = prompt_glyphs_for_action(action_id, self._options.mode_draft)
        if not glyphs:
            return ""
        return format_prompt([glyphs[0]], self._state.prompt_glyph_detail)

    def _prompt_for_crt_filter(self) -> str:
        return format_prompt([PromptGlyph.KEY_F6], self._state.prompt_glyph_detail)


class MainMenuSimpleOverlayFlow(MainMenuOverlayFlow):
    def __init__(
        self,
        lines: list[str],
        confirm_open_overlay: int = -1,
        line_colors: list[int] | None = None
    ) -> None:
        self._lines = list(lines)
        self._confirm_open_overlay = int(confirm_open_overlay)
        self._line_colors: list[int] | None = None
        if line_colors is not None:
            self._line_colors = list(line_colors)

    def body_lines(self) -> list[str]:
        return list(self._lines)

    def update(
        self,
        scene: MainMenuScene,
        nav_up_released: bool,
        nav_down_released: bool,
        nav_left_released: bool,
        nav_right_released: bool,
        confirm_released: bool,
        cancel_released: bool,
        secondary_released: bool,
        mouse_nav_released: bool
    ) -> None:
        if mouse_nav_released:
            nav_down_released = True
        body_lines = self.body_lines()
        scene._clamp_overlay_scroll(body_lines)
        if nav_up_released:
            scene._overlay_scroll -= 1
            scene._clamp_overlay_scroll(body_lines)
        elif nav_down_released:
            scene._overlay_scroll += 1
            scene._clamp_overlay_scroll(body_lines)
        if cancel_released:
            scene._close_overlay()
            return
        if not confirm_released:
            return
        if self._confirm_open_overlay >= 0:
            scene._open_overlay(self._confirm_open_overlay)
            return
        scene._close_overlay()

    def draw(self, scene: MainMenuScene, body_x_pad: int, body_line_step: int) -> None:
        scene._draw_overlay_box(
            scene._overlay_title(""),
            self._lines,
            self._line_colors
        )


def build_main_menu_overlay_defs(
    state: GameState,
    new_game_flow: MainMenuNewGameFlow
) -> dict[int, MainMenuOverlayDef]:
    controls_flow = MainMenuControlsOverlayFlow(state)
    credits_flow = MainMenuSimpleOverlayFlow(
        [
            "Wyrdway",
            "A game by @etomarat",
            "",
            "Want to appear here?",
            "Leave feedback at itch.io page:",
            "https://etomarat.itch.io/wyrdway",
            "",
            "Playtesters:",
            "Skellybob56",
            "14zy",
            "plasticlife-art",
            "",
            "Thanks for playing!"
        ],
        line_colors=[
            Color.WHITE,
            Color.LIGHT_GREY,
            Color.LIGHT_GREY,
            Color.WHITE,
            Color.WHITE,
            Color.YELLOW,
            Color.LIGHT_GREY,
            Color.WHITE,
            Color.LIGHT_GREY,
            Color.LIGHT_GREY,
            Color.LIGHT_GREY,
            Color.LIGHT_GREY,
            Color.WHITE
        ]
    )
    new_game_confirm_flow = MainMenuSimpleOverlayFlow(
        [
            "START NEW GAME?",
            "CURRENT PROFILE PROGRESS",
            "WILL BE RESET",
            "",
            "THIS CANNOT BE UNDONE"
        ],
        MAIN_MENU_OVERLAY_NEW_GAME_SETUP
    )
    new_game_setup_flow = MainMenuNewGameSetupOverlayFlow(
        new_game_flow,
        MAIN_MENU_OVERLAY_NEW_GAME_SEED
    )
    new_game_seed_flow = MainMenuNewGameSeedOverlayFlow(new_game_flow)
    return {
        MAIN_MENU_OVERLAY_CONTROLS: MainMenuOverlayDef(
            UiModalSpec(
                "OPTIONS",
                _menu_overlay_layout(
                    4,
                    4,
                    232,
                    130,
                    13,
                    25,
                    3,
                    (1, 1, 1),
                    0,
                    1,
                    2,
                    FOOTER_PAD_PROFILE_INVERTED,
                    footer_button_top_pad=2
                ),
                UiModalFooterSpec(
                    Action.CONFIRM,
                    Action.CANCEL,
                    UiModalNavMode.ALWAYS,
                    "NAV",
                    "SAVE",
                    "CANCEL"
                )
            ),
            controls_flow
        ),
        MAIN_MENU_OVERLAY_CREDITS: MainMenuOverlayDef(
            UiModalSpec(
                "CREDITS",
                _menu_overlay_layout(
                    16,
                    20,
                    208,
                    106,
                    30,
                    44,
                    2,
                    (1, 1),
                    0,
                    1,
                    1,
                    FOOTER_PAD_PROFILE_DEFAULT
                ),
                UiModalFooterSpec(
                    Action.CONFIRM,
                    Action.CANCEL,
                    UiModalNavMode.ALWAYS,
                    "NAV",
                    "",
                    "CLOSE"
                )
            ),
            credits_flow
        ),
        MAIN_MENU_OVERLAY_NEW_GAME_CONFIRM: MainMenuOverlayDef(
            UiModalSpec(
                "CONFIRM RESET",
                _menu_overlay_layout(
                    20,
                    28,
                    200,
                    90,
                    37,
                    54,
                    2,
                    (1, 1),
                    0,
                    0,
                    1,
                    FOOTER_PAD_PROFILE_DEFAULT
                ),
                UiModalFooterSpec(
                    Action.CONFIRM,
                    Action.CANCEL,
                    UiModalNavMode.NEVER,
                    "",
                    "CONFIRM",
                    "CANCEL"
                )
            ),
            new_game_confirm_flow
        ),
        MAIN_MENU_OVERLAY_NEW_GAME_SETUP: MainMenuOverlayDef(
            UiModalSpec(
                "NEW GAME SETUP",
                _menu_overlay_layout(
                    20,
                    20,
                    200,
                    98,
                    30,
                    44,
                    3,
                    (1, 1, 1),
                    0,
                    1,
                    2,
                    FOOTER_PAD_PROFILE_DEFAULT
                ),
                UiModalFooterSpec(
                    Action.CONFIRM,
                    Action.CANCEL,
                    UiModalNavMode.ALWAYS,
                    "NAV",
                    "SELECT",
                    "CANCEL"
                )
            ),
            new_game_setup_flow
        ),
        MAIN_MENU_OVERLAY_NEW_GAME_SEED: MainMenuOverlayDef(
            UiModalSpec(
                "SEED EDITOR",
                _menu_overlay_layout(
                    20,
                    24,
                    200,
                    90,
                    34,
                    50,
                    3,
                    (1, 1, 1),
                    0,
                    1,
                    2,
                    FOOTER_PAD_PROFILE_DEFAULT
                ),
                UiModalFooterSpec(
                    Action.CONFIRM,
                    Action.CANCEL,
                    UiModalNavMode.ALWAYS,
                    "EDIT",
                    "SAVE",
                    "CANCEL"
                )
            ),
            new_game_seed_flow
        )
    }
