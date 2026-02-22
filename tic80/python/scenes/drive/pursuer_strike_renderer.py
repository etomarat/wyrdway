from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import line

    from ...core.palette import Color
    from ...systems.drive.rng import lcg_next_u32


class PursuerStrikeRenderer:
    __slots__ = ()

    @staticmethod
    def _lcg(seed: int) -> int:
        return lcg_next_u32(seed)

    def draw_entity_strike(
        self,
        px: int,
        py: int,
        tx: int,
        ty: int,
        flash_n: float,
        seed_base: int
    ) -> None:
        dx = float(tx - px)
        dy = float(ty - py)
        d2 = dx * dx + dy * dy
        if d2 <= 0.0001:
            return
        inv = 1.0 / (d2 ** 0.5)
        nx = -dy * inv
        ny = dx * inv
        segs = 4
        seed = seed_base
        prev_x = float(px)
        prev_y = float(py)
        i = 1
        while i <= segs:
            t = float(i) / float(segs)
            x = float(px) + dx * t
            y = float(py) + dy * t
            if i < segs:
                seed = self._lcg(seed)
                jitter = (float(seed & 255) / 255.0) * 2.0 - 1.0
                amp = 1.0 + 4.0 * flash_n
                x += nx * jitter * amp
                y += ny * jitter * amp
            line(int(prev_x), int(prev_y), int(x), int(y), Color.LIGHT_BLUE)
            if flash_n > 0.45:
                line(int(prev_x), int(prev_y) + 1, int(x), int(y) + 1, Color.WHITE)
            prev_x = x
            prev_y = y
            i += 1

    def draw_glitch_strike(
        self,
        px: int,
        py: int,
        tx: int,
        ty: int,
        flash_n: float,
        seed_base: int
    ) -> None:
        self._draw_lightning(px, py, tx, ty, flash_n, seed_base)

    def _draw_lightning(
        self,
        px: int,
        py: int,
        tx: int,
        ty: int,
        flash_n: float,
        seed_base: int
    ) -> None:
        dx = float(tx - px)
        dy = float(ty - py)
        d2 = dx * dx + dy * dy
        if d2 <= 0.0001:
            return
        inv = 1.0 / (d2 ** 0.5)
        nx = -dy * inv
        ny = dx * inv
        seed = seed_base
        segs = 7
        prev_x = float(px)
        prev_y = float(py)
        i = 1
        while i <= segs:
            t = float(i) / float(segs)
            x = float(px) + dx * t
            y = float(py) + dy * t
            if i < segs:
                seed = self._lcg(seed)
                jitter = (float(seed & 255) / 255.0) * 2.0 - 1.0
                amp = 2.0 + 7.0 * flash_n
                x += nx * jitter * amp
                y += ny * jitter * amp
            line(int(prev_x), int(prev_y), int(x), int(y), Color.CYAN)
            line(int(prev_x) + 1, int(prev_y), int(x) + 1, int(y), Color.BLUE)
            if flash_n > 0.55:
                line(int(prev_x), int(prev_y) + 1, int(x), int(y) + 1, Color.WHITE)
            prev_x = x
            prev_y = y
            i += 1
