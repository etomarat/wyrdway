from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import line

    from ...core.palette import Color
    from ...data.tuning import TUNING
    from ...systems.drive.drive_fx import DriveFxProjector
    from ...systems.drive.drive_objects import DriveZone
    from ...systems.drive.road_model import RoadModel


class TopdownRoadDraw:
    def clamp_center_y(self, y: int) -> int:
        y0 = int(TUNING.DRIVE.view_center_y_min)
        y1 = int(TUNING.DRIVE.view_center_y_max)
        y = max(y0, min(y1, y))
        return y

    def visible_index_range(
        self,
        road: RoadModel,
        p_s: float,
        render_back_s: float | None = None,
        render_forward_s: float | None = None
    ) -> tuple[int, int]:
        n = road.center_points_len()
        d = TUNING.DRIVE
        back = float(d.render_back_s)
        fwd = float(d.render_forward_s)
        if render_back_s is not None:
            back = float(render_back_s)
        if render_forward_s is not None:
            fwd = float(render_forward_s)
        start_s = p_s - back
        end_s = p_s + fwd
        start = int(start_s / road.ds)
        end = int(end_s / road.ds)
        start = max(0, start)
        end = min(n - 1, end)
        return start, end

    def draw_road_edges_and_zones(
        self,
        road: RoadModel,
        zones: list[DriveZone],
        active_zone: DriveZone | None,
        start_idx: int,
        end_idx: int,
        proj: DriveFxProjector
    ) -> None:
        prev_lsx = None
        prev_lsy = None
        prev_rsx = None
        prev_rsy = None

        i = start_idx
        while i <= end_idx:
            cx, cy, dir_x, dir_y = road.center_point_at_index(i)
            half = road.width_at(i * road.ds) * 0.5
            nrm_x = -dir_y
            nrm_y = dir_x

            lx = cx - nrm_x * half
            ly = cy - nrm_y * half
            rx = cx + nrm_x * half
            ry = cy + nrm_y * half

            lsx, lsy = proj.world_to_screen(lx, ly)
            rsx, rsy = proj.world_to_screen(rx, ry)

            if prev_lsx is not None and prev_lsy is not None:
                line(int(prev_lsx), int(prev_lsy), int(
                    lsx), int(lsy), Color.LIGHT_GREEN)
            if prev_rsx is not None and prev_rsy is not None:
                line(int(prev_rsx), int(prev_rsy), int(
                    rsx), int(rsy), Color.LIGHT_GREEN)

            prev_lsx = lsx
            prev_lsy = lsy
            prev_rsx = rsx
            prev_rsy = rsy
            i += 1

        s_vis0 = start_idx * road.ds
        s_vis1 = end_idx * road.ds
        i = 0
        while i < len(zones):
            is_active = active_zone is not None and zones[i] is active_zone
            self._draw_booster_lane_edges(
                road,
                zones[i],
                is_active,
                s_vis0,
                s_vis1,
                proj
            )
            self._draw_zone_chevrons(
                road,
                zones[i],
                is_active,
                s_vis0,
                s_vis1,
                proj
            )
            i += 1

    def _draw_booster_lane_edges(
        self,
        road: RoadModel,
        z: DriveZone,
        is_active: bool,
        s_vis0: float,
        s_vis1: float,
        proj: DriveFxProjector
    ) -> None:
        s0 = z.s_start
        s1 = z.s_end
        s0 = max(s_vis0, s0)
        s1 = min(s_vis1, s1)
        if s1 <= s0:
            return

        d0 = z.d_center - z.radius
        d1 = z.d_center + z.radius

        step = road.ds * 0.5
        step = max(1.0, step)

        prev0x = None
        prev0y = None
        prev1x = None
        prev1y = None
        color = Color.GREEN
        if is_active:
            color = Color.WHITE

        s = s0
        while s <= s1:
            cx, cy = road.sample_centerline_interp(s)
            dx, dy = road.direction_at_interp(s)
            nrm_x = -dy
            nrm_y = dx

            wx0 = cx + nrm_x * d0
            wy0 = cy + nrm_y * d0
            wx1 = cx + nrm_x * d1
            wy1 = cy + nrm_y * d1
            zsx0, zsy0 = proj.world_to_screen(wx0, wy0)
            zsx1, zsy1 = proj.world_to_screen(wx1, wy1)
            if prev0x is not None and prev0y is not None:
                line(int(prev0x), int(prev0y), int(zsx0), int(zsy0), color)
            if prev1x is not None and prev1y is not None:
                line(int(prev1x), int(prev1y), int(zsx1), int(zsy1), color)

            prev0x = zsx0
            prev0y = zsy0
            prev1x = zsx1
            prev1y = zsy1
            s += step

    def _draw_zone_chevrons(
        self,
        road: RoadModel,
        zone: DriveZone,
        is_active: bool,
        s_vis0: float,
        s_vis1: float,
        proj: DriveFxProjector
    ) -> None:
        zone_len = zone.s_end - zone.s_start
        if zone_len <= 0.0:
            return

        chevron_len = TUNING.DRIVE.zone_chevron_length
        chevron_len = max(3.0, chevron_len)
        gap_len = TUNING.DRIVE.zone_chevron_gap
        gap_len = max(0.0, gap_len)
        pitch = chevron_len + gap_len
        if pitch <= 0.0:
            return

        chevrons_n = 1
        if zone_len > chevron_len and pitch > 0.0:
            chevrons_n += int((zone_len - chevron_len) / pitch)

        used_len = chevron_len + float(chevrons_n - 1) * pitch
        lead_in = (zone_len - used_len) * 0.5
        lead_in = max(0.0, lead_in)
        center_s = zone.s_start + lead_in + chevron_len * 0.5
        i = 0
        while i < chevrons_n:
            if center_s >= s_vis0 - chevron_len and center_s <= s_vis1 + chevron_len:
                self._draw_zone_chevron_at_s(
                    road,
                    zone,
                    is_active,
                    center_s,
                    chevron_len,
                    proj
                )
            center_s += pitch
            i += 1

    def _draw_zone_chevron_at_s(
        self,
        road: RoadModel,
        zone: DriveZone,
        is_active: bool,
        center_s: float,
        chevron_len: float,
        proj: DriveFxProjector
    ) -> None:
        half = road.width_at(center_s) * 0.5
        d0 = zone.d_center - zone.radius
        d1 = zone.d_center + zone.radius
        d0 = max(-half, min(half, d0))
        d1 = max(-half, min(half, d1))

        span_width = d1 - d0
        if span_width <= 2.0:
            return

        center_d = (d0 + d1) * 0.5
        back_len = chevron_len * 0.32
        arm_half = span_width * 0.34
        arm_half = max(2.0, min(4.0, arm_half))

        tail_s = center_s - back_len
        tip_s = center_s + chevron_len
        left_x, left_y = self._road_point_at_sd(
            road,
            tail_s,
            center_d - arm_half
        )
        right_x, right_y = self._road_point_at_sd(
            road,
            tail_s,
            center_d + arm_half
        )
        tip_x, tip_y = self._road_point_at_sd(
            road,
            tip_s,
            center_d
        )
        sx_tip, sy_tip = proj.world_to_screen(tip_x, tip_y)
        sx_left, sy_left = proj.world_to_screen(left_x, left_y)
        sx_right, sy_right = proj.world_to_screen(right_x, right_y)
        line(int(sx_left), int(sy_left), int(
            sx_tip), int(sy_tip), Color.YELLOW)
        line(int(sx_left), int(sy_left) + 1, int(
            sx_tip), int(sy_tip) + 1, Color.YELLOW)
        line(int(sx_right), int(sy_right), int(
            sx_tip), int(sy_tip), Color.YELLOW)
        line(int(sx_right), int(sy_right) + 1, int(
            sx_tip), int(sy_tip) + 1, Color.YELLOW)

    def _road_point_at_sd(self, road: RoadModel, s: float, d: float) -> tuple[float, float]:
        cx, cy = road.sample_centerline_interp(s)
        dir_x, dir_y = road.direction_at_interp(s)
        nrm_x = -dir_y
        nrm_y = dir_x
        return (cx + nrm_x * d, cy + nrm_y * d)
