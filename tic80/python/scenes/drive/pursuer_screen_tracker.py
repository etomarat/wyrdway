from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...contracts import PursuerVariantTuning


class PursuerScreenTracker:
    __slots__ = (
        "_draw_s",
        "_draw_inited",
        "_draw_d",
        "_draw_d_inited",
        "_screen_x",
        "_screen_y",
        "_screen_inited",
        "_intro_active",
        "_intro_t",
        "_intro_start_x",
        "_intro_start_y"
    )

    def __init__(self) -> None:
        self._draw_s = 0.0
        self._draw_inited = False
        self._draw_d = 0.0
        self._draw_d_inited = False
        self._screen_x = 0.0
        self._screen_y = 0.0
        self._screen_inited = False
        self._intro_active = False
        self._intro_t = 0.0
        self._intro_start_x = 0.0
        self._intro_start_y = 0.0

    def reset(self) -> None:
        self._draw_inited = False
        self._draw_d = 0.0
        self._draw_d_inited = False
        self._screen_inited = False
        self._intro_active = False
        self._intro_t = 0.0

    def smooth_draw_s(self, target_s: float) -> float:
        if (not self._draw_inited) or abs(target_s - self._draw_s) > 48.0:
            self._draw_s = target_s
            self._draw_inited = True
            return self._draw_s
        lerp = 0.14
        self._draw_s += (target_s - self._draw_s) * lerp
        return self._draw_s

    def smooth_draw_d(self, target_d: float, half_w: float, pursuer_state: str) -> float:
        if (not self._draw_d_inited) or abs(target_d - self._draw_d) > half_w * 0.9:
            self._draw_d = target_d
            self._draw_d_inited = True
            return self._draw_d
        d_lerp = 0.16
        if pursuer_state == "NEAR":
            d_lerp = 0.10
        self._draw_d += (target_d - self._draw_d) * d_lerp
        return self._draw_d

    def draw_d(self) -> float:
        return self._draw_d

    def screen_position(
        self,
        sx: float,
        sy: float,
        profile: PursuerVariantTuning,
        pursuer_state: str,
        dt: float
    ) -> tuple[int, int]:
        if not self._screen_inited:
            entry_y = float(profile.intro_entry_screen_y)
            if entry_y <= 0.0:
                entry_y = 164.0
            self._screen_x = sx
            self._screen_y = entry_y
            self._screen_inited = True
            self._intro_active = True
            self._intro_t = 0.0
            self._intro_start_x = sx
            self._intro_start_y = entry_y
        elif (
            abs(sx - self._screen_x) + abs(sy - self._screen_y) > 80.0
        ) and (not self._intro_active):
            self._screen_x = sx
            self._screen_y = sy

        if self._intro_active:
            self._intro_t += dt
            n = 1.0
            entry_seconds = float(profile.intro_entry_seconds)
            if entry_seconds <= 0.0:
                entry_seconds = 0.75
            if entry_seconds > 0.0001:
                n = self._intro_t / entry_seconds
            if n < 0.0:
                n = 0.0
            if n > 1.0:
                n = 1.0
            ease = n * n * (3.0 - 2.0 * n)
            self._screen_x = self._intro_start_x + (sx - self._intro_start_x) * ease
            self._screen_y = self._intro_start_y + (sy - self._intro_start_y) * ease
            if n >= 1.0:
                self._intro_active = False
        else:
            screen_lerp = 0.14
            if pursuer_state == "NEAR":
                screen_lerp = 0.09
            self._screen_x += (sx - self._screen_x) * screen_lerp
            self._screen_y += (sy - self._screen_y) * screen_lerp

        return int(self._screen_x), int(self._screen_y)
