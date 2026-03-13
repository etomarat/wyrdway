from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Sequence

    from tic80 import btn, btnp, key, keyp

    from .bindings import ActionBindings, InputKind, InputRef, input_ref_token
    from .actions import ActionId
    from .key_codes import KeyCode


class Controls:
    def __init__(self, bindings: ActionBindings) -> None:
        self._bindings = bindings
        self._all_refs = bindings.all_refs()
        self._blocked_refs: dict[int, bool] = {}
        self._allowed_actions: dict[int, bool] | None = None
        self._context_token = 0

    def enter_context(
        self,
        actions: "Sequence[ActionId] | None" = None,
        swallow_held: bool = True
    ) -> int:
        self._context_token += 1
        if actions is None:
            self._allowed_actions = None
        else:
            allowed: dict[int, bool] = {}
            i = 0
            while i < len(actions):
                allowed[int(actions[i])] = True
                i += 1
            self._allowed_actions = allowed
        if swallow_held:
            self.swallow_held_inputs()
        return int(self._context_token)

    def swallow_held_inputs(self) -> None:
        self._refresh_blocked_refs()
        i = 0
        while i < len(self._all_refs):
            ref = self._all_refs[i]
            if self._raw_ref_down(ref):
                self._blocked_refs[input_ref_token(ref)] = True
            i += 1

    def down(self, action: "ActionId") -> bool:
        self._refresh_blocked_refs()
        if not self._action_allowed(action):
            return False
        refs = self._bindings.down_buttons(action)
        if not refs:
            refs = self._bindings.pressed_buttons(action)
        for ref in refs:
            if self._ref_available(ref) and self._down_ref(ref):
                return True
        return False

    def pressed(self, action: "ActionId", hold: int = -1, period: int = -1) -> bool:
        self._refresh_blocked_refs()
        if not self._action_allowed(action):
            return False
        refs = self._bindings.pressed_buttons(action)
        if not refs:
            refs = self._bindings.down_buttons(action)
        for ref in refs:
            if self._ref_available(ref) and self._pressed_ref(ref, hold, period):
                return True
        return False

    def down_for(self, action: "ActionId", context_token: int) -> bool:
        if int(context_token) != int(self._context_token):
            return False
        return self.down(action)

    def pressed_for(
        self,
        action: "ActionId",
        context_token: int,
        hold: int = -1,
        period: int = -1
    ) -> bool:
        if int(context_token) != int(self._context_token):
            return False
        return self.pressed(action, hold, period)

    @staticmethod
    def _down_ref(ref: InputRef) -> bool:
        return Controls._raw_ref_down(ref)

    @staticmethod
    def _raw_ref_down(ref: InputRef) -> bool:
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

    def _refresh_blocked_refs(self) -> None:
        if len(self._blocked_refs) <= 0:
            return
        i = 0
        while i < len(self._all_refs):
            ref = self._all_refs[i]
            token = input_ref_token(ref)
            if self._blocked_refs.get(token, False) and not self._raw_ref_down(ref):
                del self._blocked_refs[token]
            i += 1

    def _action_allowed(self, action: "ActionId") -> bool:
        allowed = self._allowed_actions
        if allowed is None:
            return True
        return bool(allowed.get(int(action), False))

    def _ref_available(self, ref: InputRef) -> bool:
        return not self._blocked_refs.get(input_ref_token(ref), False)

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
