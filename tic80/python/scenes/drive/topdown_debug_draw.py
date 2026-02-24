from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import circb, line

    from ...core.palette import Color
    from ...data.tuning import TUNING
    from ...systems.drive.drive_fx import TopdownProjector
    from ...systems.drive.drive_logic_core import DriveLogic
    from ...systems.drive.road_model import RoadModel


class TopdownDebugDraw:
    def draw_vectors(self, logic: DriveLogic, proj: TopdownProjector, cx: int, cy: int) -> None:
        d = TUNING.DRIVE
        h = d.debug_vectors_heading_len
        if h < 0.0:
            h = 0.0
        if h > 60.0:
            h = 60.0

        vel_scale = d.debug_vectors_vel_scale
        accel_scale = d.debug_vectors_accel_scale

        hx, hy = proj.world_vec_to_screen(logic.fwd_x, logic.fwd_y)
        hx, hy = self._normalize_or_fallback(hx, hy, 0.0, -1.0)
        line(cx, cy, int(cx + hx * h), int(cy + hy * h), Color.WHITE)

        vx, vy = proj.world_vec_to_screen(logic.vx, logic.vy)
        vx *= vel_scale
        vy *= vel_scale
        vx = self._clamp(vx, -60.0, 60.0)
        vy = self._clamp(vy, -60.0, 60.0)
        line(cx, cy, int(cx + vx), int(cy + vy), Color.CYAN)

        right_x = -logic.fwd_y
        right_y = logic.fwd_x
        acc_wx = right_x * logic.dbg_side_accel
        acc_wy = right_y * logic.dbg_side_accel
        ax, ay = proj.world_vec_to_screen(acc_wx, acc_wy)
        ax *= accel_scale
        ay *= accel_scale
        ax = self._clamp(ax, -60.0, 60.0)
        ay = self._clamp(ay, -60.0, 60.0)
        line(cx, cy, int(cx + ax), int(cy + ay), Color.GREY)

    def draw_hitboxes(self, logic: DriveLogic, proj: TopdownProjector) -> None:
        rear_x, rear_y, rear_r, front_x, front_y, front_r = logic.hitbox_world_circles()
        rear_sx, rear_sy = proj.world_to_screen(rear_x, rear_y)
        front_sx, front_sy = proj.world_to_screen(front_x, front_y)

        line(int(rear_sx), int(rear_sy), int(front_sx), int(front_sy), Color.GREY)
        if rear_r > 0.0:
            circb(int(rear_sx), int(rear_sy), int(rear_r), Color.CYAN)
        if front_r > 0.0:
            circb(int(front_sx), int(front_sy), int(front_r), Color.WHITE)

    def draw_pursuer_strike_range(
        self,
        road: RoadModel,
        proj: TopdownProjector,
        car_s: float,
        strike_dist_s: float
    ) -> None:
        start_s = float(car_s) - float(strike_dist_s)
        if start_s < 0.0:
            start_s = 0.0
        seg_total = float(road.segment_total_length)
        if start_s > seg_total:
            start_s = seg_total
        cx, cy = road.sample_centerline(start_s)
        dir_x, dir_y = road.direction_at(start_s)
        right_x = -dir_y
        right_y = dir_x
        half_w = road.width_at(start_s) * 0.5 + 1.0

        # Полоса поперёк дороги в точке начала strike-дистанции.
        o = -1
        while o <= 1:
            ox = dir_x * float(o)
            oy = dir_y * float(o)
            lx = cx - right_x * half_w + ox
            ly = cy - right_y * half_w + oy
            rx = cx + right_x * half_w + ox
            ry = cy + right_y * half_w + oy
            slx, sly = proj.world_to_screen(lx, ly)
            srx, sry = proj.world_to_screen(rx, ry)
            c = Color.RED
            if o == 0:
                c = Color.WHITE
            line(int(slx), int(sly), int(srx), int(sry), c)
            o += 1

    @staticmethod
    def _normalize_or_fallback(
        x: float,
        y: float,
        fallback_x: float,
        fallback_y: float
    ) -> tuple[float, float]:
        l2 = x * x + y * y
        if l2 > 0.000001:
            inv = 1.0 / (l2 ** 0.5)
            return x * inv, y * inv
        return fallback_x, fallback_y

    @staticmethod
    def _clamp(value: float, min_value: float, max_value: float) -> float:
        if value < min_value:
            return min_value
        if value > max_value:
            return max_value
        return value
