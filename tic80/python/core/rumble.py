from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import rumble


def rumble_try(
    gamepad: int = 0,
    weak: int = 0,
    strong: int = 0,
    duration: int = 120
) -> bool:
    try:
        return bool(rumble(int(gamepad), int(weak), int(strong), int(duration)))
    except Exception:
        return False


def rumble_supported() -> bool:
    if rumble_try(0, 0, 0, 0):
        return True
    return rumble_try(-1, 0, 0, 0)
