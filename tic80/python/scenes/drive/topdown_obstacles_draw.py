from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import circb

    from ...core.palette import Color
    from ...data.tuning import TUNING
    from ...systems.drive.drive_objects import DriveObstacle
    from ...systems.drive.drive_fx import DriveFxProjector
    from ...systems.drive.road_model import RoadModel


class TopdownObstaclesDraw:
    def draw(
        self,
        obstacles: list[DriveObstacle],
        road: RoadModel,
        p_s: float,
        proj: DriveFxProjector
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
            sx, sy = proj.world_to_screen(wx, wy)
            circb(int(sx), int(sy), int(o.radius), Color.RED)
            i += 1
