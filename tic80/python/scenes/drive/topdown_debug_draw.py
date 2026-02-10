from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import circb, line

    from ...core.palette import Color
    from ...data.tuning import TUNING
    from ...systems.drive.drive_fx import TopdownProjector
    from ...systems.drive.drive_logic_core import DriveLogic


class TopdownDebugDraw:
    def draw_vectors(self, logic: DriveLogic, cx: int, cy: int) -> None:
        d = TUNING.DRIVE
        h = d.debug_vectors_heading_len
        if h < 0.0:
            h = 0.0
        if h > 60.0:
            h = 60.0

        vel_scale = d.debug_vectors_vel_scale
        accel_scale = d.debug_vectors_accel_scale

        line(cx, cy, cx, int(cy - h), Color.WHITE)

        vx = logic.v_side * vel_scale
        vy = -logic.v_forward * vel_scale
        if vx > 60.0:
            vx = 60.0
        if vx < -60.0:
            vx = -60.0
        if vy > 60.0:
            vy = 60.0
        if vy < -60.0:
            vy = -60.0
        line(cx, cy, int(cx + vx), int(cy + vy), Color.CYAN)

        ax = logic.dbg_side_accel * accel_scale
        if ax > 60.0:
            ax = 60.0
        if ax < -60.0:
            ax = -60.0
        line(cx, cy, int(cx + ax), cy, Color.GREY)

    def draw_hitboxes(self, logic: DriveLogic, proj: TopdownProjector) -> None:
        rear_x, rear_y, rear_r, front_x, front_y, front_r = logic.hitbox_world_circles()
        rear_sx, rear_sy = proj.world_to_screen(rear_x, rear_y)
        front_sx, front_sy = proj.world_to_screen(front_x, front_y)

        line(int(rear_sx), int(rear_sy), int(front_sx), int(front_sy), Color.GREY)
        if rear_r > 0.0:
            circb(int(rear_sx), int(rear_sy), int(rear_r), Color.CYAN)
        if front_r > 0.0:
            circb(int(front_sx), int(front_sy), int(front_r), Color.WHITE)
