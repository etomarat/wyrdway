from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import line

    from ...core.palette import Color
    from ...data.tuning import TUNING
    from ...systems.drive.drive_fx import TopdownProjector
    from ...systems.drive.drive_logic_core import DriveLogic


class TopdownSkidMarks:
    def __init__(self) -> None:
        self._skids: list[tuple[float, float, float, float, int]] = []
        self._start_skid_t = 0.0

    def trigger_start(self, seconds: float) -> None:
        t = float(seconds)
        if t > self._start_skid_t:
            self._start_skid_t = t

    def update_and_draw(
        self,
        logic: DriveLogic,
        cx: int,
        cy: int,
        proj: TopdownProjector
    ) -> None:
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

        # Важно: следы “живут” в мире, поэтому мировой сдвиг берём в camera-space.
        dx, dy = proj.world_vec_to_screen(-logic.vx * dt, -logic.vy * dt)

        i = 0
        while i < len(self._skids):
            x0, y0, x1, y1, life = self._skids[i]
            if life > 0:
                color = Color.DARK_GREY
                if life < TUNING.DRIVE.skid_light_after_frames:
                    color = Color.GREY

                x0 += dx
                y0 += dy
                x1 += dx
                y1 += dy

                x0i = int(x0)
                y0i = int(y0)
                x1i = int(x1)
                y1i = int(y1)

                # Делаем след шириной 2 пикселя: две параллельные линии.
                if x0 < cx:
                    line(x0i, y0i, x1i, y1i, color)
                    line(x0i + 1, y0i, x1i + 1, y1i, color)
                else:
                    line(x0i - 1, y0i, x1i - 1, y1i, color)
                    line(x0i, y0i, x1i, y1i, color)

                life -= 1
                self._skids[i] = (x0, y0, x1, y1, life)
                i += 1
            else:
                self._skids.pop(i)

        if not active:
            return

        back = int(TUNING.DRIVE.skid_back_px)
        wheel_dx = int(TUNING.DRIVE.skid_wheel_dx_px)
        seg = int(TUNING.DRIVE.skid_seg_len_px)

        # Небольшое смещение в сторону заноса, чтобы след “наклонялся”.
        slant = -int(TUNING.DRIVE.skid_slant_scale * (logic.v_side / denom))
        slant_max = int(TUNING.DRIVE.skid_slant_max)
        if slant > slant_max:
            slant = slant_max
        if slant < -slant_max:
            slant = -slant_max

        left_x = cx - wheel_dx
        right_x = cx + wheel_dx
        y0 = cy + back
        y1 = y0 + seg

        life = int(TUNING.DRIVE.skid_life_frames)
        self._skids.append((left_x, y0, left_x + slant, y1, life))
        self._skids.append((right_x, y0, right_x + slant, y1, life))
