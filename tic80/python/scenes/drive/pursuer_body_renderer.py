import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import circ, circb, line, print

    from ...contracts import PursuerVariantTuning
    from ...core.palette import Color
    from ...core.text_layout import text_width
    from ...systems.drive.rng import lcg_next_u32
    from .pursuer_text_bank import PursuerTextBank


class PursuerBodyRenderer:
    __slots__ = ("_text_bank")

    def __init__(self, text_bank: PursuerTextBank) -> None:
        self._text_bank = text_bank

    @staticmethod
    def _lcg(seed: int) -> int:
        return lcg_next_u32(seed)

    def draw_glitch_body(
        self,
        px: int,
        py: int,
        pursuer_state: str,
        seed_base: int,
        road_half_px: float,
        profile: PursuerVariantTuning,
        anim_t: float,
        cam_angle: float
    ) -> None:
        self._draw_glitch_body(
            px,
            py,
            pursuer_state,
            seed_base,
            road_half_px,
            profile,
            anim_t,
            cam_angle,
            False
        )

    def draw_prime_body(
        self,
        px: int,
        py: int,
        pursuer_state: str,
        seed_base: int,
        road_half_px: float,
        profile: PursuerVariantTuning,
        anim_t: float,
        cam_angle: float
    ) -> None:
        self._draw_glitch_body(
            px,
            py,
            pursuer_state,
            seed_base,
            road_half_px,
            profile,
            anim_t,
            cam_angle,
            True
        )

    def _draw_glitch_body(
        self,
        px: int,
        py: int,
        pursuer_state: str,
        seed_base: int,
        road_half_px: float,
        profile: PursuerVariantTuning,
        anim_t: float,
        cam_angle: float,
        clamp_to_road: bool
    ) -> None:
        r = int(profile.body_radius_chase)
        if pursuer_state == "NEAR":
            r = int(profile.body_radius_near)
        if clamp_to_road:
            min_by_road = int(road_half_px * 1.08)
            if min_by_road > r:
                r = min_by_road
        if r < 3:
            r = 3

        core_color = Color.DARK_BLUE
        if pursuer_state == "NEAR":
            core_color = Color.BLUE
        circ(px, py, r, core_color)
        core_r = r - 4
        if core_r < 2:
            core_r = 2
        circ(px, py, core_r, Color.CYAN)
        circb(px, py, r + 1, Color.LIGHT_BLUE)
        circb(px - 1, py, r, Color.CYAN)
        circb(px + 1, py, r, Color.BLUE)

        seed = seed_base
        lines_n = 7 + int(r * 0.55)
        if pursuer_state == "NEAR":
            lines_n += int(r * 0.35)
        i = 0
        while i < lines_n:
            seed = self._lcg(seed)
            if pursuer_state != "NEAR" and (seed & 3) == 0:
                i += 1
                continue
            y_off = int(seed % (r * 2 + 3)) - (r + 1)
            seed = self._lcg(seed)
            half = r - int(abs(y_off) * 0.4) + int(seed & 1)
            if half < 1:
                half = 1
            seed = self._lcg(seed)
            x_jit = int(r * 0.22)
            if x_jit < 2:
                x_jit = 2
            x_off = int(seed % (x_jit * 2 + 1)) - x_jit
            color = Color.CYAN
            if (seed & 1) == 0:
                color = Color.LIGHT_BLUE
            if (seed & 7) == 0:
                color = Color.WHITE
            line(
                px - half + x_off,
                py + y_off,
                px + half + x_off,
                py + y_off,
                color
            )
            i += 1

        if pursuer_state == "FAR":
            return
        is_near = pursuer_state == "NEAR"
        seed = self._lcg(seed)

        shards = int(profile.code_shard_count_chase)
        if is_near:
            shards = int(profile.code_shard_count_near)
        if shards < 1:
            shards = 1

        inner_r = float(profile.code_shard_radius_inner)
        outer_r = float(profile.code_shard_radius_outer)
        if inner_r < 0.0:
            inner_r = 0.0
        if outer_r < 1.0:
            outer_r = 1.0
        if outer_r < inner_r:
            t = inner_r
            inner_r = outer_r
            outer_r = t
        min_outer_shell = float(r) + 8.0
        if inner_r < min_outer_shell:
            inner_r = min_outer_shell
        if outer_r < inner_r + 8.0:
            outer_r = inner_r + 8.0
        up_bias = float(profile.code_shard_up_bias)
        inner2 = inner_r * inner_r
        outer2 = outer_r * outer_r

        j = 0
        while j < shards:
            seed = self._lcg(seed)
            angle = (float(seed & 4095) / 4095.0) * math.pi * 2.0
            seed = self._lcg(seed)
            dist_n = float(seed & 1023) / 1023.0
            dist = (inner2 + (outer2 - inner2) * dist_n) ** 0.5
            anchor_x = px + int(math.cos(angle) * dist)
            anchor_y = py + int(math.sin(angle) * dist - up_bias)
            seed = self._lcg(seed)
            txt = self._text_bank.code_shard_text(seed)
            color = Color.LIGHT_BLUE
            if is_near and (seed & 1) != 0:
                color = Color.CYAN
            elif (seed & 15) == 0:
                color = Color.WHITE
            text_w = text_width(txt, 6)
            sx = anchor_x - (text_w // 2)
            sy = anchor_y
            if sy >= -6 and sy <= 130:
                if sx >= -text_w and sx <= 239:
                    print(txt, sx, sy, color)
            j += 1

    def draw_entity_body(
        self,
        px: int,
        py: int,
        pursuer_state: str,
        seed_base: int,
        profile: PursuerVariantTuning,
        anim_t: float
    ) -> None:
        r = int(profile.body_radius_chase)
        if pursuer_state == "NEAR":
            r = int(profile.body_radius_near)
        if r < 3:
            r = 3

        core_color = Color.DARK_BLUE
        if pursuer_state == "NEAR":
            core_color = Color.BLUE
        circ(px, py, r, core_color)
        inner = r - 2
        if inner < 2:
            inner = 2
        circ(px, py, inner, Color.CYAN)
        ring_color = Color.CYAN
        if pursuer_state == "NEAR":
            ring_color = Color.WHITE
        circb(px, py, r + 1, ring_color)
        eye_half = 1
        if r >= 6:
            eye_half = 2
        line(px - eye_half, py, px + eye_half, py, Color.WHITE)

        seed = seed_base
        trail_n = 3
        if pursuer_state == "NEAR":
            trail_n = 5
        i = 0
        while i < trail_n:
            seed = self._lcg(seed)
            x_off = int(seed % 3) - 1
            y0 = py + r + 1 + i * 2
            y1 = y0 + 1
            c = Color.DARK_BLUE
            if (seed & 1) != 0:
                c = Color.BLUE
            line(px + x_off, y0, px + x_off, y1, c)
            i += 1

        labels_n = 2
        if pursuer_state == "NEAR":
            labels_n = 3
        orbit_r = float(r) + 13.0
        if pursuer_state == "NEAR":
            orbit_r += 3.0
        j = 0
        while j < labels_n:
            seed = self._lcg(seed)
            txt = self._text_bank.entity_whisper_text(seed)
            seed = self._lcg(seed)
            a = (float(seed & 4095) / 4095.0) * math.pi * 2.0
            a += anim_t * 0.65 + float(j) * 1.2
            wobble = 1.2 * math.sin(anim_t * 2.4 + float(seed & 255) * 0.03)
            dist = orbit_r + wobble
            ax = px + int(math.cos(a) * dist)
            ay = py + int(math.sin(a) * dist * 0.72 - 4.0)
            color = Color.LIGHT_BLUE
            if pursuer_state == "NEAR" and (seed & 1) != 0:
                color = Color.CYAN
            elif (seed & 31) == 0:
                color = Color.WHITE
            text_w = text_width(txt, 5)
            sx = ax - (text_w // 2)
            sy = ay
            if sy >= -6 and sy <= 130:
                if sx >= -text_w and sx <= 239:
                    print(txt, sx, sy, color, True, 1, True)
            j += 1
