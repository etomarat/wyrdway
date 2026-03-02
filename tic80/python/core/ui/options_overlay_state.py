from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..controls.modes import InputDeviceModeId
else:
    InputDeviceModeId = int


class UiOptionsOverlayState:
    _MODE_GAMEPAD: InputDeviceModeId = 0
    _MODE_KEYBOARD: InputDeviceModeId = 1
    _MODE_BOTH: InputDeviceModeId = 2

    def __init__(self) -> None:
        self.mode_draft: InputDeviceModeId = self._MODE_BOTH
        self.shoulders_draft = False
        self.vibration_draft = True
        self.focus_row = 0

    def reset_draft(
        self,
        mode: InputDeviceModeId,
        shoulders_enabled: bool,
        vibration_enabled: bool
    ) -> None:
        self.mode_draft = mode
        self.shoulders_draft = bool(shoulders_enabled)
        self.vibration_draft = bool(vibration_enabled)
        self.focus_row = 0
        self._normalize_state()

    def shoulders_enabled(self) -> bool:
        return self.mode_draft == self._MODE_GAMEPAD

    def vibration_enabled(self) -> bool:
        return self.mode_draft != self._MODE_KEYBOARD

    def input_mode_label(self) -> str:
        if self.mode_draft == self._MODE_KEYBOARD:
            return "KEYBOARD+mouse"
        if self.mode_draft == self._MODE_GAMEPAD:
            return "GAMEPAD"
        return "KEYBOARD|GAMEPAD"

    def setting_label(self, row: int) -> str:
        if row == 0:
            return "CONTROL MODE:"
        if row == 1:
            return "SHOULDERS:"
        return "VIBRATION:"

    def setting_value(self, row: int) -> str:
        if row == 0:
            return self.input_mode_label()
        if row == 1:
            if self.shoulders_draft:
                return "ON"
            return "OFF"
        if self.vibration_draft:
            return "ON"
        return "OFF"

    def setting_enabled(self, row: int) -> bool:
        if row == 0:
            return True
        if row == 1:
            return self.shoulders_enabled()
        if row == 2:
            return self.vibration_enabled()
        return False

    def update_from_nav(
        self,
        nav_up_released: bool,
        nav_down_released: bool,
        nav_left_released: bool,
        nav_right_released: bool
    ) -> None:
        self._clamp_focus()
        if nav_up_released or nav_down_released:
            if nav_down_released:
                self.focus_row += 1
                if self.focus_row > 2:
                    self.focus_row = 0
            else:
                self.focus_row -= 1
                if self.focus_row < 0:
                    self.focus_row = 2
        if nav_left_released:
            self.apply_setting_change(self.focus_row, True)
        if nav_right_released:
            self.apply_setting_change(self.focus_row, False)

    def apply_setting_change(self, row: int, forward: bool) -> None:
        if row == 0:
            self._cycle_mode(forward)
            return
        if row == 1 and self.shoulders_enabled():
            self.shoulders_draft = not self.shoulders_draft
            return
        if row == 2 and self.vibration_enabled():
            self.vibration_draft = not self.vibration_draft

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
        if forward:
            idx += 1
            if idx >= len(modes):
                idx = 0
        else:
            idx -= 1
            if idx < 0:
                idx = len(modes) - 1
        self.mode_draft = modes[idx]
        self._normalize_state()

    def _clamp_focus(self) -> None:
        if self.focus_row < 0 or self.focus_row > 2:
            self.focus_row = 0

    def _normalize_state(self) -> None:
        if not self.shoulders_enabled():
            self.shoulders_draft = False
        if not self.vibration_enabled():
            self.vibration_draft = False
        self._clamp_focus()
