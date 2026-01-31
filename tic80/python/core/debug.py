from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import btnp, print

    from .input_buttons import Button


class DebugOverlay:
    """Дебаг-оверлей для TIC-80.
    """

    def __init__(self) -> None:
        self._enabled = True

    @property
    def enabled(self) -> bool:
        return self._enabled

    def toggle(self) -> None:
        self._enabled = not self._enabled

    def set_enabled(self, value: bool) -> None:
        self._enabled = value

    def handle_input(self) -> None:
        if btnp(Button.Y):
            self.toggle()

    def draw(
        self,
        lines: list[str],
        x: int = 1,
        y: int = 1,
        color: int = 12
    ) -> None:
        if not self._enabled:
            return
        for i, line in enumerate(lines):
            print(line, x, y + i * 6, color, fixed=True, alt=True)
