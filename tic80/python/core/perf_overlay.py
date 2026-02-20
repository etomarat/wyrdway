from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import btnp, print, time

    from .input_buttons import Button


class PerfOverlay:
    def __init__(self) -> None:
        self._enabled = False
        self._frame = 0

        self._begin_ms = 0
        self._prev_end_ms = 0
        self._cpu_ms = 0
        self._frame_ms = 0

        self._fps_int = 0
        self._lines: list[str] = []

    @property
    def enabled(self) -> bool:
        return self._enabled

    def set_enabled(self, value: bool) -> None:
        self._enabled = bool(value)

    def toggle(self) -> None:
        self._enabled = not self._enabled

    def handle_input(self) -> None:
        if btnp(Button.X):
            self.toggle()

    def begin_frame(self) -> None:
        if not self._enabled:
            return
        self._begin_ms = int(time())

    def end_frame(self) -> None:
        if not self._enabled:
            return

        end_ms = int(time())
        self._cpu_ms = end_ms - self._begin_ms

        if self._prev_end_ms > 0:
            self._frame_ms = end_ms - self._prev_end_ms
        self._prev_end_ms = end_ms

        if self._frame_ms > 0:
            self._fps_int = int((1000 + self._frame_ms // 2) // self._frame_ms)
        else:
            self._fps_int = 0

        self._frame += 1
        if (self._frame & 7) == 0:
            self._lines = [
                "fps=" + str(self._fps_int),
                "frame=" + str(self._frame_ms) + "ms",
                "cpu=" + str(self._cpu_ms) + "ms"
            ]

    def draw(self, x: int = 1, y: int = 1, color: int = 12) -> None:
        if not self._enabled:
            return
        if len(self._lines) <= 0:
            return
        i = 0
        while i < len(self._lines):
            text = self._lines[i]
            text_w = len(text) * 4
            px = 240 - x - text_w
            if px < 0:
                px = 0
            py = y + i * 6
            print(text, px, py, color, fixed=True, alt=True)
            i += 1
