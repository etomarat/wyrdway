import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import line, pix

    from ...core.palette import Color
    from ...data.tuning import TUNING
    from ...systems.drive.drive_logic_core import DriveLogic
    from ...systems.drive.pursuer_chase import PursuerChase


class PursuerScreenFx:
    def draw(self, logic: "DriveLogic", pursuer: "PursuerChase", fx_time: float) -> None:
        intensity = pursuer.near_intensity()
        if intensity <= 0.0:
            return
        strike_dist = float(TUNING.PURSUER.strike_begin_dist_s)
        gap = float(TUNING.PURSUER.follow_gap_s)
        if strike_dist < gap:
            strike_dist = gap
        caught = pursuer.distance_s <= strike_dist
        pulse = (1.0 + math.sin(fx_time * 8.0)) * 0.5

        vig = intensity * float(TUNING.PURSUER.near_vignette) * (1.0 + 0.25 * pulse)
        if vig > 0.0:
            thick = int(vig * 16.0 + 0.5)
            if thick > 8:
                thick = 8
            i = 0
            while i < thick:
                color = Color.DARK_BLUE
                if (i & 1) != 0:
                    color = Color.PURPLE
                x0 = i
                y0 = i
                x1 = 239 - i
                y1 = 135 - i
                line(x0, y0, x1, y0, color)
                line(x0, y1, x1, y1, color)
                line(x0, y0, x0, y1, color)
                line(x1, y0, x1, y1, color)
                i += 1

        noise = intensity * float(TUNING.PURSUER.near_noise) * (1.0 + 0.35 * pulse)
        if caught:
            contact_mult = float(TUNING.PURSUER.contact_noise_mult)
            if contact_mult > 0.0:
                noise *= contact_mult
        flash_n = 0.0
        if pursuer.strike_flash > 0.0:
            flash_t = float(TUNING.PURSUER.strike_flash_seconds)
            flash_n = 1.0
            if flash_t > 0.0001:
                flash_n = pursuer.strike_flash / flash_t
            if flash_n < 0.0:
                flash_n = 0.0
            if flash_n > 1.0:
                flash_n = 1.0
            noise *= 1.0 + float(TUNING.PURSUER.strike_noise_boost) * flash_n
        dots = int(noise * 110.0)
        if dots <= 0:
            if flash_n > 0.0:
                self._draw_strike_meltdown(flash_n, 0)
            return
        seed = int(
            logic.road_s * 13.0
            + pursuer.distance_s * 7.0
            + pursuer.cooldown * 100.0
            + fx_time * 1000.0
        )
        seed &= 0xFFFFFFFF
        i = 0
        while i < dots:
            seed = ((seed * 1664525) + 1013904223) & 0xFFFFFFFF
            x = int(seed % 240)
            seed = ((seed * 1664525) + 1013904223) & 0xFFFFFFFF
            y = int(seed % 136)
            c = Color.DARK_GREY
            if caught:
                c = Color.BLUE
                if (seed & 3) == 0:
                    c = Color.CYAN
                if (seed & 15) == 0:
                    c = Color.PURPLE
                if (seed & 31) == 0:
                    c = Color.WHITE
            else:
                if (seed & 3) == 0:
                    c = Color.LIGHT_GREY
            pix(x, y, c)
            i += 1
        if flash_n > 0.0:
            self._draw_strike_meltdown(flash_n, seed)

    def _draw_strike_meltdown(self, flash_n: float, seed_base: int) -> None:
        if flash_n <= 0.0:
            return
        strength = flash_n * float(TUNING.PURSUER.strike_meltdown_intensity)
        if strength <= 0.0:
            return
        if strength > 1.0:
            strength = 1.0

        seed = seed_base & 0xFFFFFFFF
        bands = int(3 + strength * 9.0)
        jitter_max = int(1 + strength * 8.0)
        i = 0
        while i < bands:
            seed = ((seed * 1664525) + 1013904223) & 0xFFFFFFFF
            y = int(seed % 136)
            seed = ((seed * 1664525) + 1013904223) & 0xFFFFFFFF
            h = 1 + int(seed % 3)
            seed = ((seed * 1664525) + 1013904223) & 0xFFFFFFFF
            spread = jitter_max * 2 + 1
            shift = int(seed % spread) - jitter_max
            c = Color.CYAN
            if (seed & 1) != 0:
                c = Color.BLUE
            if (seed & 7) == 0:
                c = Color.WHITE
            j = 0
            while j < h:
                yy = y + j
                self._shift_scanline(yy, shift)
                if yy >= 0 and yy < 136:
                    line(0, yy, 239, yy, c)
                j += 1
            i += 1

        blocks = int(2 + strength * 7.0)
        i = 0
        while i < blocks:
            seed = ((seed * 1664525) + 1013904223) & 0xFFFFFFFF
            x = int(seed % 220)
            seed = ((seed * 1664525) + 1013904223) & 0xFFFFFFFF
            y = int(seed % 124)
            seed = ((seed * 1664525) + 1013904223) & 0xFFFFFFFF
            w = 8 + int(seed % 24)
            seed = ((seed * 1664525) + 1013904223) & 0xFFFFFFFF
            h = 4 + int(seed % 10)
            seed = ((seed * 1664525) + 1013904223) & 0xFFFFFFFF
            dx = int(seed % 17) - 8
            seed = ((seed * 1664525) + 1013904223) & 0xFFFFFFFF
            dy = int(seed % 9) - 4
            self._blit_glitch_block(x, y, w, h, dx, dy)
            if (seed & 3) == 0:
                yy = y
                while yy < y + h and yy < 136:
                    line(x, yy, x + w, yy, Color.BLACK)
                    yy += 1
            i += 1

        holes = int(3 + strength * 10.0)
        i = 0
        while i < holes:
            seed = ((seed * 1664525) + 1013904223) & 0xFFFFFFFF
            x = int(seed % 224)
            seed = ((seed * 1664525) + 1013904223) & 0xFFFFFFFF
            y = int(seed % 120)
            seed = ((seed * 1664525) + 1013904223) & 0xFFFFFFFF
            w = 8 + int(seed % 24)
            seed = ((seed * 1664525) + 1013904223) & 0xFFFFFFFF
            h = 6 + int(seed % 20)
            yy = y
            while yy < y + h and yy < 136:
                xx = x
                while xx < x + w and xx < 240:
                    if (((xx - x) >> 1) + ((yy - y) >> 1)) & 1:
                        pix(xx, yy, Color.BLACK)
                    else:
                        pix(xx, yy, Color.DARK_GREY)
                    xx += 1
                yy += 1
            i += 1

    def _shift_scanline(self, y: int, shift: int) -> None:
        if y < 0 or y >= 136:
            return
        if shift == 0:
            return
        src_row: list[int] = []
        x = 0
        while x < 240:
            c = pix(x, y)
            if c is None:
                c = 0
            src_row.append(int(c))
            x += 1
        x = 0
        while x < 240:
            sx = x - shift
            if sx < 0 or sx >= 240:
                pix(x, y, Color.BLACK)
            else:
                pix(x, y, src_row[sx])
            x += 1

    def _blit_glitch_block(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        dx: int,
        dy: int
    ) -> None:
        yy = 0
        while yy < h:
            dst_y = y + yy
            src_y = y + yy + dy
            if dst_y >= 0 and dst_y < 136 and src_y >= 0 and src_y < 136:
                row: list[int] = []
                xx = 0
                while xx < w:
                    src_x = x + xx + dx
                    if src_x < 0 or src_x >= 240:
                        row.append(Color.BLACK)
                    else:
                        c = pix(src_x, src_y)
                        if c is None:
                            c = 0
                        row.append(int(c))
                    xx += 1
                xx = 0
                while xx < w:
                    dst_x = x + xx
                    if dst_x >= 0 and dst_x < 240:
                        pix(dst_x, dst_y, row[xx])
                    xx += 1
            yy += 1
