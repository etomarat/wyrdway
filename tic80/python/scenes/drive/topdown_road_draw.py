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
        prev_turn_x = [0.0, 0.0]
        prev_turn_y = [0.0, 0.0]
        prev_turn_side = [0.0, 0.0]
        prev_turn_on = [False, False]

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

            turn_level, turn_side = self._turn_shoulder_level_and_side(road, i)
            lane = 0
            while lane < 2:
                if lane >= turn_level or turn_side == 0.0:
                    prev_turn_on[lane] = False
                    prev_turn_side[lane] = 0.0
                    lane += 1
                    continue

                if prev_turn_side[lane] != turn_side:
                    prev_turn_on[lane] = False

                s_turn = i * road.ds
                turn_half = road.width_at(s_turn) * 0.5
                turn_offset = 1.0 + float(lane)
                wx, wy = self._road_point_at_sd(
                    road,
                    s_turn,
                    turn_side * (turn_half + turn_offset)
                )
                wsx, wsy = proj.world_to_screen(wx, wy)
                if prev_turn_on[lane]:
                    line(
                        int(prev_turn_x[lane]),
                        int(prev_turn_y[lane]),
                        int(wsx),
                        int(wsy),
                        Color.LIGHT_GREY if lane == 0 else Color.GREY
                    )
                prev_turn_x[lane] = wsx
                prev_turn_y[lane] = wsy
                prev_turn_side[lane] = turn_side
                prev_turn_on[lane] = True
                lane += 1

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

        self._draw_start_road_tail(road, start_idx, end_idx, proj)

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

    # Experimental shoulder fringe kept only as a source note:
    # it read like some kind of worm, creepy and wrong for a normal shoulder.
    # Might be useful later for biome-specific roadside growth/corruption or
    # for showing visual progression of the world.
    #
    # def _draw_shoulder_fringe_at(
    #     self,
    #     road: RoadModel,
    #     i: int,
    #     side_sign: float,
    #     edge_x: float,
    #     edge_y: float,
    #     dir_x: float,
    #     dir_y: float,
    #     nrm_x: float,
    #     nrm_y: float,
    #     proj: DriveFxProjector
    # ) -> None:
    #     salt = 0
    #     if side_sign > 0.0:
    #         salt = 2
    #     pattern = (i + road.seed + salt) & 3
    #     if pattern >= 2:
    #         return
    #     skew = 1.25
    #     if ((i + road.seed + salt) & 4) != 0:
    #         skew = -skew
    #     mid_len = 4.0
    #     if pattern == 0:
    #         mid_len = 5.5
    #     outer_x = edge_x + side_sign * nrm_x * mid_len + dir_x * skew
    #     outer_y = edge_y + side_sign * nrm_y * mid_len + dir_y * skew
    #     sx0, sy0 = proj.world_to_screen(edge_x, edge_y)
    #     sx1, sy1 = proj.world_to_screen(outer_x, outer_y)
    #     line(int(sx0), int(sy0), int(sx1), int(sy1), Color.ORANGE)
    #     if pattern != 0:
    #         return
    #     far_len = mid_len + 3.5
    #     far_x = edge_x + side_sign * nrm_x * far_len + dir_x * skew * 1.2
    #     far_y = edge_y + side_sign * nrm_y * far_len + dir_y * skew * 1.2
    #     sx2, sy2 = proj.world_to_screen(far_x, far_y)
    #     line(int(sx1), int(sy1), int(sx2), int(sy2), Color.YELLOW)

    # Shoulder dots experiment kept only as source reference:
    # visually useful, but not stable enough yet for the default road read.
    # Could be reused later for sand shoulders, biome edges, or run-state
    # progression accents.
    #
    # def _draw_shoulder_dots_at(...): ...

    # def _draw_edge_shade_dots_at(...): ...

    def _turn_shoulder_level_and_side(
        self,
        road: RoadModel,
        i: int
    ) -> tuple[int, float]:
        s = i * road.ds
        curv_signed = road.curvature_at(s)
        curv = curv_signed
        if curv < 0.0:
            curv = -curv
        if curv <= 0.003:
            return (0, 0.0)

        side = 1.0
        if curv_signed > 0.0:
            side = -1.0

        if curv >= 0.005:
            return (2, side)
        return (1, side)

    def draw_finish_gate_back(
        self,
        road: RoadModel,
        start_idx: int,
        end_idx: int,
        proj: DriveFxProjector,
        anim_t: float
    ) -> None:
        seam_s, inner, outer = self._finish_gate_layout(road, start_idx, end_idx)
        if seam_s < 0.0:
            return
        self._draw_road_tail(road, seam_s, 1.0, proj)
        self._draw_finish_gate_posts(
            road,
            seam_s + 4.0,
            inner + 2.0,
            outer + 2.0,
            proj,
            Color.DARK_GREY,
            Color.GREY
        )

    def draw_finish_gate_front(
        self,
        road: RoadModel,
        start_idx: int,
        end_idx: int,
        proj: DriveFxProjector,
        anim_t: float
    ) -> None:
        seam_s, inner, outer = self._finish_gate_layout(road, start_idx, end_idx)
        if seam_s < 0.0:
            return
        self._draw_finish_gate_crossbar(road, seam_s + 5.5, inner, outer, proj)
        self._draw_finish_gate_field(road, seam_s, outer, proj, anim_t)

    def _finish_gate_layout(
        self,
        road: RoadModel,
        start_idx: int,
        end_idx: int
    ) -> tuple[float, float, float]:
        seam_s = road.segment_total_length
        margin = road.ds * 4.0
        s_vis0 = start_idx * road.ds
        s_vis1 = end_idx * road.ds
        if seam_s < s_vis0 - margin or seam_s > s_vis1 + margin:
            return -1.0, 0.0, 0.0
        half = road.width_at(seam_s) * 0.5
        return seam_s, half + 8.0, half + 18.0

    def _draw_finish_gate_posts(
        self,
        road: RoadModel,
        s: float,
        inner: float,
        outer: float,
        proj: DriveFxProjector,
        shade_a: int,
        shade_b: int
    ) -> None:
        side = -1.0
        while side <= 1.0:
            self._draw_world_segment(
                proj,
                self._road_point_at_sd(road, s - 20.0, side * outer),
                self._road_point_at_sd(road, s + 15.0, side * outer),
                shade_a
            )
            self._draw_world_segment(
                proj,
                self._road_point_at_sd(road, s - 20.0, side * (outer - 4.0)),
                self._road_point_at_sd(road, s + 15.0, side * (outer - 4.0)),
                shade_b
            )
            self._draw_world_segment(
                proj,
                self._road_point_at_sd(road, s - 12.0, side * (outer - 4.0)),
                self._road_point_at_sd(road, s - 1.5, side * inner),
                shade_a
            )
            self._draw_world_segment(
                proj,
                self._road_point_at_sd(road, s + 5.0, side * (outer - 4.0)),
                self._road_point_at_sd(road, s + 1.0, side * inner),
                shade_b
            )
            self._draw_world_segment(
                proj,
                self._road_point_at_sd(road, s - 20.0, side * (outer + 2.5)),
                self._road_point_at_sd(road, s - 13.0, side * (outer + 8.0)),
                shade_a
            )
            side += 2.0

    def _draw_finish_gate_crossbar(
        self,
        road: RoadModel,
        s: float,
        inner: float,
        outer: float,
        proj: DriveFxProjector
    ) -> None:
        left = self._road_point_at_sd(road, s, -outer - 1.0)
        right = self._road_point_at_sd(road, s, outer + 1.0)
        sx0, sy0 = proj.world_to_screen(left[0], left[1])
        sx1, sy1 = proj.world_to_screen(right[0], right[1])
        x0 = int(sx0)
        y0 = int(sy0)
        x1 = int(sx1)
        y1 = int(sy1)
        line(x0, y0 - 1, x1, y1 - 1, Color.DARK_GREY)
        line(x0, y0, x1, y1, Color.GREY)
        line(x0, y0 + 1, x1, y1 + 1, Color.LIGHT_GREY)

    def _draw_finish_gate_field(
        self,
        road: RoadModel,
        s: float,
        outer: float,
        proj: DriveFxProjector,
        anim_t: float
    ) -> None:
        frame = int(anim_t * 60.0)
        i = 0
        while i < 3:
            strand_s = s - 4.2 + i * 4.2
            color = Color.LIGHT_BLUE
            if (i & 1) != 0:
                color = Color.WHITE
            if i == 2:
                color = Color.CYAN
            self._draw_gate_strand(road, proj, road.seed, frame, i, strand_s, outer - 5.5, color)
            i += 1

    def _draw_gate_strand(
        self,
        road: RoadModel,
        proj: DriveFxProjector,
        seed: int,
        frame: int,
        strand_i: int,
        s: float,
        d: float,
        color: int
    ) -> None:
        j0 = self._gate_strand_jitter(seed, frame, strand_i, 0) * 0.35
        j1 = self._gate_strand_jitter(seed, frame, strand_i, 1)
        j2 = self._gate_strand_jitter(seed, frame, strand_i, 2)
        j3 = self._gate_strand_jitter(seed, frame, strand_i, 3) * 0.35
        p0 = self._road_point_at_sd(road, s + j0, -d)
        p1 = self._road_point_at_sd(road, s + j1, -d * 0.34)
        p2 = self._road_point_at_sd(road, s + j2, d * 0.34)
        p3 = self._road_point_at_sd(road, s + j3, d)
        self._draw_world_segment(proj, p0, p1, color)
        self._draw_world_segment(proj, p1, p2, color)
        self._draw_world_segment(proj, p2, p3, color)

    def _gate_strand_jitter(self, seed: int, frame: int, strand_i: int, point_i: int) -> float:
        h = (seed * 13 + frame * (strand_i * 9 + point_i * 7 + 5) + strand_i * 31 + point_i * 17) & 15
        return (h - 7.5) * 0.52

    def _draw_start_road_tail(
        self,
        road: RoadModel,
        start_idx: int,
        end_idx: int,
        proj: DriveFxProjector
    ) -> None:
        margin = road.ds * 4.0
        s_vis0 = start_idx * road.ds
        if 0.0 < s_vis0 - margin:
            return
        self._draw_road_tail(road, 0.0, -1.0, proj)

    def _draw_road_tail(
        self,
        road: RoadModel,
        seam_s: float,
        dir_sign: float,
        proj: DriveFxProjector
    ) -> None:
        stable_len = 16.0
        fade_len = 22.0
        dot_len = 14.0
        step = 3.8
        s = 0.0
        while s < stable_len:
            self._draw_tail_span(
                road,
                seam_s + dir_sign * s,
                seam_s + dir_sign * (s + step),
                proj
            )
            s += step
        s = stable_len
        while s < stable_len + fade_len:
            t = (s - stable_len) / fade_len
            seg = step * (1.0 - t * 0.90)
            if seg > 0.45:
                self._draw_tail_span(
                    road,
                    seam_s + dir_sign * s,
                    seam_s + dir_sign * (s + seg),
                    proj
                )
            s += step * 1.08
        s = stable_len + fade_len
        while s < stable_len + fade_len + dot_len:
            self._draw_tail_dot(road, seam_s + dir_sign * s, proj)
            s += step * 1.20

    def _draw_tail_span(
        self,
        road: RoadModel,
        s0: float,
        s1: float,
        proj: DriveFxProjector
    ) -> None:
        width0 = road.width_at(s0) * 0.5
        width1 = road.width_at(s1) * 0.5
        left0 = self._road_point_at_sd(road, s0, -width0)
        left1 = self._road_point_at_sd(road, s1, -width1)
        right0 = self._road_point_at_sd(road, s0, width0)
        right1 = self._road_point_at_sd(road, s1, width1)
        self._draw_world_segment(proj, left0, left1, Color.LIGHT_GREEN)
        self._draw_world_segment(proj, right0, right1, Color.LIGHT_GREEN)

    def _draw_tail_dot(self, road: RoadModel, s: float, proj: DriveFxProjector) -> None:
        width = road.width_at(s) * 0.5
        left = self._road_point_at_sd(road, s, -width)
        right = self._road_point_at_sd(road, s, width)
        self._draw_world_point(proj, left, Color.LIGHT_GREEN)
        self._draw_world_point(proj, right, Color.LIGHT_GREEN)

    def _draw_world_segment(
        self,
        proj: DriveFxProjector,
        a: tuple[float, float],
        b: tuple[float, float],
        color: int
    ) -> None:
        sx0, sy0 = proj.world_to_screen(a[0], a[1])
        sx1, sy1 = proj.world_to_screen(b[0], b[1])
        line(int(sx0), int(sy0), int(sx1), int(sy1), color)

    def _draw_world_point(
        self,
        proj: DriveFxProjector,
        a: tuple[float, float],
        color: int
    ) -> None:
        sx, sy = proj.world_to_screen(a[0], a[1])
        line(int(sx), int(sy), int(sx), int(sy), color)

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
        total = road.segment_total_length
        cx = 0.0
        cy = 0.0
        dir_x = 1.0
        dir_y = 0.0
        if s <= 0.0:
            cx, cy = road.sample_centerline_interp(0.0)
            dir_x, dir_y = road.direction_at_interp(0.0)
            cx += dir_x * s
            cy += dir_y * s
        elif s >= total:
            cx, cy = road.sample_centerline_interp(total)
            dir_x, dir_y = road.direction_at_interp(total)
            extra = s - total
            cx += dir_x * extra
            cy += dir_y * extra
        else:
            cx, cy = road.sample_centerline_interp(s)
            dir_x, dir_y = road.direction_at_interp(s)
        nrm_x = -dir_y
        nrm_y = dir_x
        return (cx + nrm_x * d, cy + nrm_y * d)
