from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..controls.modes import InputDeviceModeId
    from ..drive_presets import (
        DrivePresetId,
        DrivePresetIdValues,
        drive_preset_clamp,
        drive_preset_cycle,
        drive_preset_label
    )
else:
    InputDeviceModeId = int
    DrivePresetId = int


class UiOptionsOverlayState:
    _ROW_DIFFICULTY = 0
    _ROW_MODE = 1
    _ROW_SHOULDERS = 2
    _ROW_VIBRATION = 3

    _MODE_GAMEPAD: InputDeviceModeId = 0
    _MODE_KEYBOARD: InputDeviceModeId = 1
    _MODE_BOTH: InputDeviceModeId = 2

    def __init__(self) -> None:
        self.mode_draft: InputDeviceModeId = self._MODE_BOTH
        self.drive_preset_draft: DrivePresetId = DrivePresetIdValues.NORMAL
        self.shoulders_draft = False
        self.vibration_draft = True
        self.focus_row = 0
        self._rumble_supported = False
        self._gamepad_shoulders_draft = False
        self._gamepad_vibration_draft = True
        self._both_vibration_draft = True
        self._shoulders_touched = False
        self._vibration_touched = False

    def reset_draft(
        self,
        mode: InputDeviceModeId,
        drive_preset: DrivePresetId,
        shoulders_enabled: bool,
        vibration_enabled: bool,
        rumble_supported: bool
    ) -> None:
        self.mode_draft = mode
        self.drive_preset_draft = drive_preset_clamp(drive_preset)
        self.focus_row = 0
        self._shoulders_touched = False
        self._vibration_touched = False
        self._rumble_supported = rumble_supported

        self._gamepad_shoulders_draft = self._rumble_supported
        self._gamepad_vibration_draft = vibration_enabled
        self._both_vibration_draft = vibration_enabled

        mode_i = self.mode_draft
        if mode_i == self._MODE_GAMEPAD:
            self._gamepad_shoulders_draft = shoulders_enabled
        elif mode_i == self._MODE_BOTH:
            self._both_vibration_draft = vibration_enabled

        self._sync_drafts_from_mode()
        self._normalize_state()

    def set_rumble_supported(self, rumble_supported: bool) -> None:
        self._rumble_supported = rumble_supported
        self._sync_drafts_from_mode()

    def row_count(self) -> int:
        return 4

    def shoulders_enabled(self) -> bool:
        return self.mode_draft == self._MODE_GAMEPAD

    def shoulders_unsupported(self) -> bool:
        return self.mode_draft == self._MODE_KEYBOARD

    def vibration_supported(self) -> bool:
        if self.mode_draft == self._MODE_KEYBOARD:
            return False
        return self._rumble_supported

    def vibration_enabled(self) -> bool:
        return self.vibration_draft

    def vibration_unsupported(self) -> bool:
        return not self.vibration_supported()

    def shoulders_touched(self) -> bool:
        return self._shoulders_touched

    def vibration_touched(self) -> bool:
        return self._vibration_touched

    def input_mode_label(self) -> str:
        if self.mode_draft == self._MODE_KEYBOARD:
            return "KEYBOARD"
        if self.mode_draft == self._MODE_GAMEPAD:
            return "GAMEPAD"
        return "DUAL INPUT"

    def setting_label(self, row: int) -> str:
        if row == self._ROW_MODE:
            return "CONTROL MODE:"
        if row == self._ROW_DIFFICULTY:
            return "DIFFICULTY:"
        if row == self._ROW_SHOULDERS:
            return "SHOULDERS:"
        return "VIBRATION:"

    def setting_value(self, row: int) -> str:
        if row == self._ROW_MODE:
            return self.input_mode_label()
        if row == self._ROW_DIFFICULTY:
            return drive_preset_label(self.drive_preset_draft)
        if row == self._ROW_SHOULDERS:
            if self.shoulders_unsupported():
                return "UNSUPPORTED"
            if self.shoulders_draft:
                return "ON"
            return "OFF"
        if self.vibration_unsupported():
            return "UNAVAILABLE"
        if self.vibration_draft:
            return "ON"
        return "OFF"

    def setting_enabled(self, row: int) -> bool:
        if row == self._ROW_MODE:
            return True
        if row == self._ROW_DIFFICULTY:
            return True
        if row == self._ROW_SHOULDERS:
            return self.shoulders_enabled()
        if row == self._ROW_VIBRATION:
            return not self.vibration_unsupported()
        return False

    def update_from_nav(
        self,
        nav_up_released: bool,
        nav_down_released: bool,
        nav_left_released: bool,
        nav_right_released: bool
    ) -> None:
        self._clamp_focus()
        row_count = self.row_count()
        if nav_up_released or nav_down_released:
            if nav_down_released:
                self.focus_row += 1
                if self.focus_row >= row_count:
                    self.focus_row = 0
            else:
                self.focus_row -= 1
                if self.focus_row < 0:
                    self.focus_row = row_count - 1
        if nav_left_released:
            self.apply_setting_change(self.focus_row, True)
        if nav_right_released:
            self.apply_setting_change(self.focus_row, False)

    def apply_setting_change(self, row: int, forward: bool) -> None:
        if row == self._ROW_MODE:
            self._cycle_mode(forward)
            return
        if row == self._ROW_DIFFICULTY:
            self._cycle_difficulty(forward)
            return
        if row == self._ROW_SHOULDERS and self.shoulders_enabled():
            self.shoulders_draft = not self.shoulders_draft
            self._gamepad_shoulders_draft = self.shoulders_draft
            self._shoulders_touched = True
            return
        if row == self._ROW_VIBRATION and not self.vibration_unsupported():
            self.vibration_draft = not self.vibration_draft
            if self.mode_draft == self._MODE_GAMEPAD:
                self._gamepad_vibration_draft = self.vibration_draft
            elif self.mode_draft == self._MODE_BOTH:
                self._both_vibration_draft = self.vibration_draft
            self._vibration_touched = True

    def _cycle_mode(self, forward: bool) -> None:
        modes: list[InputDeviceModeId] = [
            self._MODE_KEYBOARD,
            self._MODE_GAMEPAD,
            self._MODE_BOTH
        ]
        idx = 0
        i = 0
        while i < len(modes):
            if modes[i] == self.mode_draft:
                idx = i
                break
            i += 1

        self._store_mode_draft_values()
        if forward:
            idx += 1
            if idx >= len(modes):
                idx = 0
        else:
            idx -= 1
            if idx < 0:
                idx = len(modes) - 1
        self.mode_draft = modes[idx]
        self._sync_drafts_from_mode()
        self._clamp_focus()

    def _cycle_difficulty(self, forward: bool) -> None:
        self.drive_preset_draft = drive_preset_cycle(
            self.drive_preset_draft,
            forward
        )

    def _clamp_focus(self) -> None:
        if self.focus_row < 0 or self.focus_row >= self.row_count():
            self.focus_row = 0

    def _normalize_state(self) -> None:
        self.drive_preset_draft = drive_preset_clamp(self.drive_preset_draft)
        self._sync_drafts_from_mode()
        self._clamp_focus()

    def _store_mode_draft_values(self) -> None:
        mode_i = self.mode_draft
        if mode_i == self._MODE_GAMEPAD:
            self._gamepad_shoulders_draft = self.shoulders_draft
            self._gamepad_vibration_draft = self.vibration_draft
        elif mode_i == self._MODE_BOTH:
            self._both_vibration_draft = self.vibration_draft

    def _sync_drafts_from_mode(self) -> None:
        mode_i = self.mode_draft
        if mode_i == self._MODE_GAMEPAD:
            self.shoulders_draft = self._gamepad_shoulders_draft
            self.vibration_draft = self._gamepad_vibration_draft
            return
        if mode_i == self._MODE_BOTH:
            self.shoulders_draft = False
            self.vibration_draft = self._both_vibration_draft
            return
        self.shoulders_draft = False
        self.vibration_draft = False
