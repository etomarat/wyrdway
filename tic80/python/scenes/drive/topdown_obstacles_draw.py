from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import circb

    from ...core.palette import Color
    from ...data.tuning import TUNING
    from ...systems.drive.drive_objects import DriveObstacle
    from ...systems.drive.road_model import RoadModel


class TopdownObstaclesDraw:
    def draw(
        self,
        obstacles: list[DriveObstacle],
        road: RoadModel,
        p_s: float,
        p_x: float,
        p_y: float,
        fwd_x: float,
        fwd_y: float,
        right_x: float,
        right_y: float,
        center_x: int,
        center_y: int
    ) -> None:
        d = TUNING.DRIVE
        max_ds = d.obstacle_render_range_s
        if max_ds < 0.0:
            max_ds = 0.0

        i = 0
        while i < len(obstacles):
            o = obstacles[i]
            if o.hit:
                i += 1
                continue
            if abs(o.s - p_s) > max_ds:
                i += 1
                continue

            cx, cy = road.sample_centerline(o.s)
            dx, dy = road.direction_at(o.s)
            nrm_x = -dy
            nrm_y = dx

            wx = cx + nrm_x * o.d
            wy = cy + nrm_y * o.d
            sx, sy = self._world_to_screen(
                wx, wy, p_x, p_y, fwd_x, fwd_y, right_x, right_y, center_x, center_y
            )
            circb(int(sx), int(sy), int(o.radius), Color.RED)
            i += 1

    def _world_to_screen(
        self,
        wx: float,
        wy: float,
        px: float,
        py: float,
        fwd_x: float,
        fwd_y: float,
        right_x: float,
        right_y: float,
        sx0: int,
        sy0: int
    ) -> tuple[float, float]:
        vx = wx - px
        vy = wy - py
        local_fwd = vx * fwd_x + vy * fwd_y
        local_right = vx * right_x + vy * right_y
        sx = sx0 + local_right
        sy = sy0 - local_fwd
        return sx, sy
