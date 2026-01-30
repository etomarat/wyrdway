from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import btnp, print
    from .input_buttons import Button

DEBUG_ENABLED: bool = True


def debug_toggle() -> None:
    global DEBUG_ENABLED
    DEBUG_ENABLED = not DEBUG_ENABLED


def debug_set_enabled(value: bool) -> None:
    global DEBUG_ENABLED
    DEBUG_ENABLED = value


def debug_handle_input() -> None:
    if btnp(Button.Y):
        debug_toggle()


def debug_draw(lines: list[str], x: int = 1, y: int = 1, color: int = 12) -> None:
    if not DEBUG_ENABLED:
        return
    for i, line in enumerate(lines):
        print(line, x, y + i * 6, color, fixed=True, alt=True)
