from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Literal, TypeAlias

    ActionId: TypeAlias = Literal[
        0, 1, 2, 3,
        10, 11, 12, 13, 14,
        20, 21, 22, 23
    ]
else:
    ActionId = int


class Action:
    # UI
    CONFIRM: ActionId = 0
    CANCEL: ActionId = 1
    SECONDARY: ActionId = 2
    HELP: ActionId = 3
    NAV_UP: ActionId = 10
    NAV_DOWN: ActionId = 11
    NAV_LEFT: ActionId = 12
    NAV_RIGHT: ActionId = 13
    PAUSE: ActionId = 14

    # DRIVE
    THROTTLE: ActionId = 20
    BRAKE: ActionId = 21
    HANDBRAKE: ActionId = 22
    SKILL: ActionId = 23
