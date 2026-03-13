from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..input_buttons import Button
    from .actions import Action, ActionId
    from .key_codes import KeyCode


class InputKind:
    BTN = 0
    KEY = 1


class InputRef:
    def __init__(self, kind: int, code: int) -> None:
        self.kind = int(kind)
        self.code = int(code)


INPUT_REF_TOKEN_STRIDE = 65536


def input_ref_token(ref: InputRef) -> int:
    return int(ref.kind) * INPUT_REF_TOKEN_STRIDE + int(ref.code)


def btn_ref(button_id: int) -> InputRef:
    return InputRef(InputKind.BTN, button_id)


def key_ref(key_code: int) -> InputRef:
    return InputRef(InputKind.KEY, key_code)


class ActionBindings:
    """Бинды Action -> список Button ids (TIC-80 btn/btnp).

    Принцип:
    - Одно действие может иметь несколько кнопок (клава + пад, альтернативы).
    - Ввод хранится отдельно от UI-подсказок: prompts могут показывать и
      триггеры/бамперы, даже если они замаплены на те же btn(id).
    """

    def __init__(self) -> None:
        self._down: dict[int, list[InputRef]] = {}
        self._pressed: dict[int, list[InputRef]] = {}

    def bind_down(self, action: ActionId, inputs: list[InputRef]) -> None:
        self._down[action] = list(inputs)

    def bind_pressed(self, action: ActionId, inputs: list[InputRef]) -> None:
        self._pressed[action] = list(inputs)

    def down_buttons(self, action: ActionId) -> list[InputRef]:
        return self._down.get(action, [])

    def pressed_buttons(self, action: ActionId) -> list[InputRef]:
        return self._pressed.get(action, [])

    def all_refs(self) -> list[InputRef]:
        out: list[InputRef] = []
        seen: dict[int, bool] = {}
        groups = [self._down, self._pressed]
        group_index = 0
        while group_index < len(groups):
            group = groups[group_index]
            for action_id in group:
                refs = group[action_id]
                i = 0
                while i < len(refs):
                    ref = refs[i]
                    token = input_ref_token(ref)
                    if not seen.get(token, False):
                        seen[token] = True
                        out.append(ref)
                    i += 1
            group_index += 1
        return out


def make_default_bindings() -> ActionBindings:
    # NOTE: No runtime imports. These names must exist due to include-order.
    # - Action is defined in core.controls.actions
    # - Button is defined in core.input_buttons
    b = ActionBindings()

    # UI defaults: unify confirm/cancel across scenes.
    b.bind_pressed(
        Action.CONFIRM,
        [btn_ref(Button.A), key_ref(KeyCode.ENTER), key_ref(KeyCode.Z)]
    )
    b.bind_pressed(
        Action.CANCEL,
        [btn_ref(Button.B), key_ref(KeyCode.BACKSPACE), key_ref(KeyCode.X)]
    )
    b.bind_pressed(Action.SECONDARY, [btn_ref(Button.X), key_ref(KeyCode.A)])
    b.bind_pressed(Action.HELP, [btn_ref(Button.Y), key_ref(KeyCode.S)])
    b.bind_pressed(Action.NAV_UP, [btn_ref(Button.UP), key_ref(KeyCode.UP)])
    b.bind_pressed(Action.NAV_DOWN, [btn_ref(Button.DOWN), key_ref(KeyCode.DOWN)])
    b.bind_pressed(Action.NAV_LEFT, [btn_ref(Button.LEFT), key_ref(KeyCode.LEFT)])
    b.bind_pressed(Action.NAV_RIGHT, [btn_ref(Button.RIGHT), key_ref(KeyCode.RIGHT)])
    b.bind_down(Action.NAV_UP, [btn_ref(Button.UP), key_ref(KeyCode.UP)])
    b.bind_down(Action.NAV_DOWN, [btn_ref(Button.DOWN), key_ref(KeyCode.DOWN)])
    b.bind_down(Action.NAV_LEFT, [btn_ref(Button.LEFT), key_ref(KeyCode.LEFT)])
    b.bind_down(Action.NAV_RIGHT, [btn_ref(Button.RIGHT), key_ref(KeyCode.RIGHT)])

    # DRIVE defaults (current behavior):
    # keep this aligned with `systems/drive/drive_input.py` until we migrate DRIVE
    # to the Action layer.
    b.bind_down(Action.THROTTLE, [btn_ref(Button.UP), btn_ref(Button.A)])
    b.bind_down(Action.BRAKE, [btn_ref(Button.DOWN), btn_ref(Button.B)])
    # Keyboard X must stay, but gamepad should prefer West. Keyboard X is key-code,
    # so it doesn't conflict with gamepad East (Button.B).
    b.bind_down(
        Action.HANDBRAKE,
        [btn_ref(Button.X), key_ref(KeyCode.SPACE), key_ref(KeyCode.X)]
    )
    b.bind_pressed(Action.SKILL, [btn_ref(Button.Y), key_ref(KeyCode.Z)])

    return b
