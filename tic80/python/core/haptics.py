from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .rumble import rumble_try


class Haptics:
    __slots__ = (
        "_steps",
        "_step_index",
        "_step_wait_s",
        "_active"
    )

    def __init__(self) -> None:
        self._steps: list[tuple[int, int, int, int]] = []
        self._step_index = -1
        self._step_wait_s = 0.0
        self._active = False

    def clear(self) -> None:
        self._steps = []
        self._step_index = -1
        self._step_wait_s = 0.0
        self._active = False

    def update(self, dt: float) -> None:
        if not self._active:
            return
        self._step_wait_s -= float(dt)
        while self._active and self._step_wait_s <= 0.0:
            next_step = self._step_index + 1
            if next_step >= len(self._steps):
                self.clear()
                return
            if not self._play_step(next_step):
                self.clear()
                return

    def play_engine_startup(self) -> None:
        self._start_pattern([
            # Short startup: two quick roars.
            (9000, 32000, 120, 200),
            (0, 0, 40, 120),
            (13000, 43000, 160, 220),
            (4500, 12000, 90, 0)
        ])

    def pulse(self, weak: int, strong: int, duration: int = 120) -> bool:
        return bool(rumble_try(0, int(weak), int(strong), int(duration)))

    def _start_pattern(self, steps: list[tuple[int, int, int, int]]) -> None:
        self.clear()
        if len(steps) <= 0:
            return
        self._steps = list(steps)
        self._active = True
        if not self._play_step(0):
            self.clear()

    def _play_step(self, step_index: int) -> bool:
        weak, strong, duration, wait_ms = self._steps[step_index]
        ok = rumble_try(0, weak, strong, duration)
        if not ok:
            return False
        self._step_index = int(step_index)
        self._step_wait_s = float(wait_ms) / 1000.0
        return True
