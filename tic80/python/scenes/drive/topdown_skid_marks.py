from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import line

    from ...core.palette import Color
    from ...data.tuning import TUNING
    from ...systems.drive.drive_fx import TopdownProjector
    from ...systems.drive.drive_logic_core import DriveLogic


class TopdownSkidMarks:
    def __init__(self) -> None:
        # Храним отрезки в world-space: так следы корректно живут при любом повороте камеры.
        self._skids: list[tuple[float, float, float, float, int]] = []
        self._start_skid_t = 0.0

    def trigger_start(self, seconds: float) -> None:
        t = float(seconds)
        if t > self._start_skid_t:
            self._start_skid_t = t

    def update_and_draw(self, logic: DriveLogic, proj: TopdownProjector) -> None:
        # slip = abs(v_side) / (abs(v_forward) + eps)
        denom = abs(logic.v_forward) + TUNING.DRIVE.slip_eps_speed
        slip = abs(logic.v_side) / denom
        if slip > 1.0:
            slip = 1.0

        # Порог чуть выше нуля, чтобы не рисовать “дрожь” на прямой.
        active = slip > TUNING.DRIVE.skid_slip_threshold
        if not active:
            # Ручник сам по себе тоже должен оставлять следы, если мы реально движемся.
            if logic.speed > TUNING.DRIVE.skid_min_speed and logic.dbg_handbrake_decel > 0.0:
                active = True

        dt = TUNING.CORE.dt
        if self._start_skid_t > 0.0:
            self._start_skid_t -= dt
            if self._start_skid_t < 0.0:
                self._start_skid_t = 0.0
            if not active and logic.speed > TUNING.DRIVE.skid_min_speed:
                active = True

        i = 0
        while i < len(self._skids):
            wx0, wy0, wx1, wy1, life = self._skids[i]
            if life > 0:
                color = Color.DARK_GREY
                if life < TUNING.DRIVE.skid_light_after_frames:
                    color = Color.GREY

                sx0, sy0 = proj.world_to_screen(wx0, wy0)
                sx1, sy1 = proj.world_to_screen(wx1, wy1)

                x0i = int(sx0)
                y0i = int(sy0)
                x1i = int(sx1)
                y1i = int(sy1)

                # Делаем след шириной 2 пикселя: две параллельные линии.
                if sx0 < sx1:
                    line(x0i, y0i, x1i, y1i, color)
                    line(x0i + 1, y0i, x1i + 1, y1i, color)
                else:
                    line(x0i - 1, y0i, x1i - 1, y1i, color)
                    line(x0i, y0i, x1i, y1i, color)

                life -= 1
                self._skids[i] = (wx0, wy0, wx1, wy1, life)
                i += 1
            else:
                self._skids.pop(i)

        if not active:
            return

        anchor_x = float(TUNING.DRIVE.car_sprite_anchor_x)
        anchor_y = float(TUNING.DRIVE.car_sprite_anchor_y)
        shift_x = 16.0 - anchor_x
        shift_back = 16.0 - anchor_y

        back = float(TUNING.DRIVE.skid_back_px) + shift_back
        wheel_dx = float(TUNING.DRIVE.skid_wheel_dx_px) + shift_x
        seg = float(TUNING.DRIVE.skid_seg_len_px)

        # Небольшое смещение в сторону заноса, чтобы след “наклонялся”.
        slant = -int(TUNING.DRIVE.skid_slant_scale * (logic.v_side / denom))
        slant_max = int(TUNING.DRIVE.skid_slant_max)
        if slant > slant_max:
            slant = slant_max
        if slant < -slant_max:
            slant = -slant_max

        fwd_x = float(logic.fwd_x)
        fwd_y = float(logic.fwd_y)
        right_x = -fwd_y
        right_y = fwd_x

        rear_x = float(logic.x) - fwd_x * back
        rear_y = float(logic.y) - fwd_y * back

        life = int(TUNING.DRIVE.skid_life_frames)

        left_wx = rear_x - right_x * wheel_dx
        left_wy = rear_y - right_y * wheel_dx
        left_ex = left_wx - fwd_x * seg + right_x * float(slant)
        left_ey = left_wy - fwd_y * seg + right_y * float(slant)
        self._skids.append((left_wx, left_wy, left_ex, left_ey, life))

        right_wx = rear_x + right_x * wheel_dx
        right_wy = rear_y + right_y * wheel_dx
        right_ex = right_wx - fwd_x * seg + right_x * float(slant)
        right_ey = right_wy - fwd_y * seg + right_y * float(slant)
        self._skids.append((right_wx, right_wy, right_ex, right_ey, life))
