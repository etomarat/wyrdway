from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import circb, line

    from ...core.palette import Color
    from ...data.tuning import TUNING
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

    def draw_hitboxes(self, steer_input: int, center_x: int, center_y: int) -> None:
        d = TUNING.DRIVE
        steer_input = 0

        ax = d.car_sprite_anchor_x
        ay = d.car_sprite_anchor_y

        rear_px = d.hitbox_rear_px
        rear_py = d.hitbox_rear_py
        front_px = d.hitbox_front_px
        front_py = d.hitbox_front_py

        rear_r = d.hitbox_rear_radius
        front_r = d.hitbox_front_radius
        if rear_r < 0.0:
            rear_r = 0.0
        if front_r < 0.0:
            front_r = 0.0

        rear_x = center_x + (rear_px - ax)
        rear_y = center_y + (rear_py - ay)
        front_x = center_x + (front_px - ax)
        front_y = center_y + (front_py - ay)

        if rear_r > 0.0:
            circb(int(rear_x), int(rear_y), int(rear_r), Color.CYAN)
        if front_r > 0.0:
            circb(int(front_x), int(front_y), int(front_r), Color.WHITE)
