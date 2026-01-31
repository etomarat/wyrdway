from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import btnp, print

    from .input_buttons import Button


class DebugOverlay:
    """Дебаг-оверлей для TIC-80.
    """

    def __init__(self) -> None:
        self.enabled = True

    def toggle(self) -> None:
        self.enabled = not self.enabled

    def set_enabled(self, value: bool) -> None:
        self.enabled = value

    def handle_input(self) -> None:
        if btnp(Button.Y):
            self.toggle()

    def draw(
        self,
        lines: list[str],
        x: int = 1,
        y: int = 1,
        color: int = 12,
    ) -> None:
        if not self.enabled:
            return
        for i, line in enumerate(lines):
            print(line, x, y + i * 6, color, fixed=True, alt=True)
