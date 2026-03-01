from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import btn, btnp, key, keyp

    from .bindings import ActionBindings, InputKind, InputRef
    from .actions import ActionId
    from .key_codes import KeyCode


class Controls:
    def __init__(self, bindings: ActionBindings) -> None:
        self._bindings = bindings

    def down(self, action: "ActionId") -> bool:
        refs = self._bindings.down_buttons(action)
        if not refs:
            refs = self._bindings.pressed_buttons(action)
        for ref in refs:
            if self._down_ref(ref):
                return True
        return False

    def pressed(self, action: "ActionId", hold: int = -1, period: int = -1) -> bool:
        refs = self._bindings.pressed_buttons(action)
        if not refs:
            refs = self._bindings.down_buttons(action)
        for ref in refs:
            if self._pressed_ref(ref, hold, period):
                return True
        return False

    @staticmethod
    def _down_ref(ref: InputRef) -> bool:
        if ref.kind == InputKind.BTN:
            if Controls._btn_is_shadowed_by_keyboard(ref.code):
                return False
            return bool(btn(ref.code))
        return bool(key(ref.code))

    @staticmethod
    def _pressed_ref(ref: InputRef, hold: int, period: int) -> bool:
        if ref.kind == InputKind.BTN:
            if Controls._btn_is_shadowed_by_keyboard(ref.code):
                return False
            return bool(btnp(ref.code, hold, period))
        return bool(keyp(ref.code, hold, period))

    @staticmethod
    def _btn_is_shadowed_by_keyboard(btn_code: int) -> bool:
        """Prevents keyboard Z/X/A/S from firing gamepad face-button refs.

        TIC-80 maps keyboard Z/X/A/S to gamepad A/B/X/Y (btn ids 4..7). For our
        bindings we want to treat those as separate inputs, so `btn_ref(Button.A)`
        means "gamepad South" and `key_ref(KeyCode.Z)` means "keyboard Z".

        If a mapped keyboard key is down, we ignore the corresponding btn().
        """
        code = int(btn_code)
        if code == 4:  # Button.A
            return bool(key(KeyCode.Z))
        if code == 5:  # Button.B
            return bool(key(KeyCode.X))
        if code == 6:  # Button.X
            return bool(key(KeyCode.A))
        if code == 7:  # Button.Y
            return bool(key(KeyCode.S))
        return False

    @staticmethod
    def dir_lr(left_down: bool, right_down: bool) -> int:
        return (-1 if left_down else 0) + (1 if right_down else 0)
