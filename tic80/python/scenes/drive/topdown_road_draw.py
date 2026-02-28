from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import line

    from ...core.palette import Color, ColorId
    from ...data.tuning import TUNING
    from ...systems.drive.drive_fx import DriveFxProjector
    from ...systems.drive.drive_objects import DriveZone
    from ...systems.drive.road_model import RoadModel


class TopdownRoadDraw:
    def clamp_center_y(self, y: int) -> int:
        y0 = int(TUNING.DRIVE.view_center_y_min)
        y1 = int(TUNING.DRIVE.view_center_y_max)
        if y < y0:
            y = y0
        if y > y1:
            y = y1
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
        if start < 0:
            start = 0
        if end > n - 1:
            end = n - 1
        return start, end

    def draw_road_edges_and_zones(
        self,
        road: RoadModel,
        zones: list[DriveZone],
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
                line(int(prev_lsx), int(prev_lsy), int(lsx), int(lsy), Color.LIGHT_GREEN)
            if prev_rsx is not None and prev_rsy is not None:
                line(int(prev_rsx), int(prev_rsy), int(rsx), int(rsy), Color.LIGHT_GREEN)

            self._draw_zone_stripe_at(
                road,
                zones,
                i,
                cx,
                cy,
                nrm_x,
                nrm_y,
                half,
                proj
            )

            prev_lsx = lsx
            prev_lsy = lsy
            prev_rsx = rsx
            prev_rsy = rsy
            i += 1

    def draw_zone_outline(
        self,
        road: RoadModel,
        z: DriveZone,
        start_idx: int,
        end_idx: int,
        proj: DriveFxProjector,
        color: ColorId
    ) -> None:
        s_vis0 = start_idx * road.ds
        s_vis1 = end_idx * road.ds
        s0 = z.s_start
        s1 = z.s_end
        if s0 < s_vis0:
            s0 = s_vis0
        if s1 > s_vis1:
            s1 = s_vis1
        if s1 <= s0:
            return

        d0 = z.d_center - z.radius
        d1 = z.d_center + z.radius

        step = road.ds * 2.0
        if step < road.ds:
            step = road.ds

        prev0x = None
        prev0y = None
        prev1x = None
        prev1y = None

        s = s0
        while s <= s1:
            cx, cy = road.sample_centerline(s)
            dx, dy = road.direction_at(s)
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

    def _draw_zone_stripe_at(
        self,
        road: RoadModel,
        zones: list[DriveZone],
        idx: int,
        cx: float,
        cy: float,
        nrm_x: float,
        nrm_y: float,
        half: float,
        proj: DriveFxProjector
    ) -> None:
        span = self._zone_span_at_s(idx * road.ds, zones)
        if span is None:
            return

        d0, d1 = span
        if d0 < -half:
            d0 = -half
        if d0 > half:
            d0 = half
        if d1 < -half:
            d1 = -half
        if d1 > half:
            d1 = half

        zx0 = cx + nrm_x * d0
        zy0 = cy + nrm_y * d0
        zx1 = cx + nrm_x * d1
        zy1 = cy + nrm_y * d1
        zsx0, zsy0 = proj.world_to_screen(zx0, zy0)
        zsx1, zsy1 = proj.world_to_screen(zx1, zy1)
        line(int(zsx0), int(zsy0), int(zsx1), int(zsy1), Color.YELLOW)

    def _zone_span_at_s(self, s: float, zones: list[DriveZone]) -> tuple[float, float] | None:
        i = 0
        while i < len(zones):
            z = zones[i]
            if s >= z.s_start and s <= z.s_end:
                return (z.d_center - z.radius, z.d_center + z.radius)
            i += 1
        return None
