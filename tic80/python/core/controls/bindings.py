from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..input_buttons import Button
    from .actions import Action


class ActionBindings:
    """Бинды Action -> список Button ids (TIC-80 btn/btnp).

    Принцип:
    - Одно действие может иметь несколько кнопок (клава + пад, альтернативы).
    - Ввод хранится отдельно от UI-подсказок: prompts могут показывать и
      триггеры/бамперы, даже если они замаплены на те же btn(id).
    """

    def __init__(self) -> None:
        self._down: dict[int, list[int]] = {}
        self._pressed: dict[int, list[int]] = {}

    def bind_down(self, action: int, buttons: list[int]) -> None:
        self._down[action] = list(buttons)

    def bind_pressed(self, action: int, buttons: list[int]) -> None:
        self._pressed[action] = list(buttons)

    def down_buttons(self, action: int) -> list[int]:
        return self._down.get(action, [])

    def pressed_buttons(self, action: int) -> list[int]:
        return self._pressed.get(action, [])


def make_default_bindings() -> ActionBindings:
    # NOTE: No runtime imports. These names must exist due to include-order.
    # - Action is defined in core.controls.actions
    # - Button is defined in core.input_buttons
    b = ActionBindings()

    # UI defaults: unify confirm/cancel across scenes.
    b.bind_pressed(Action.CONFIRM, [Button.A])
    b.bind_pressed(Action.CANCEL, [Button.B])
    b.bind_pressed(Action.NAV_UP, [Button.UP])
    b.bind_pressed(Action.NAV_DOWN, [Button.DOWN])
    b.bind_pressed(Action.NAV_LEFT, [Button.LEFT])
    b.bind_pressed(Action.NAV_RIGHT, [Button.RIGHT])

    # DRIVE defaults (current behavior):
    # keep this aligned with `systems/drive/drive_input.py` until we migrate DRIVE
    # to the Action layer.
    b.bind_down(Action.THROTTLE, [Button.UP])
    b.bind_down(Action.BRAKE, [Button.DOWN])
    b.bind_down(Action.HANDBRAKE, [Button.B])
    b.bind_pressed(Action.SKILL, [Button.A])

    return b

