import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import clip, time

    from ..core.run_state import RunState
    from ..data.tuning import TUNING
    from ..systems.drive.drive_logic_core import DriveLogic
    from ..systems.drive.drive_objects import DriveObjects
    from ..systems.drive.road_model import RoadModel
    from ..systems.drive.rng import lcg_next_u32
    from .drive.drive_topdown_renderer import DriveTopdownRenderer


class MainMenuBackdrop:
    """Background contract for the main menu."""

    def enter(self) -> None:
        return

    def update(self, dt: float) -> None:
        return

    def draw(self, x: int, y: int, w: int, h: int) -> None:
        return


class SimpleRoadBackdrop(MainMenuBackdrop):
    """Drive renderer backdrop with smoother road and scripted movement."""
    _MENU_VIEW_CENTER_Y_N = 0.50
    _MENU_RENDER_BACK_S = 160.0
    _MENU_RENDER_FORWARD_S = 210.0
    _MENU_SIDE_TURN_START_N = 0.20
    _MENU_SIDE_RATIO_BASE = 0.03
    _MENU_SIDE_RATIO_ADD = 0.11
    _MENU_SKID_SLIP_THRESHOLD = 0.09
    _MENU_SKID_MIN_SPEED = 3.0
    _MENU_LANE_SWAY_N = 0.18
    _MENU_LANE_SWAY_FREQ = 0.010
    _MENU_SPEED_ACCEL_PER_SEC = 108.0
    _MENU_SPEED_DECEL_PER_SEC = 168.0

    def __init__(self) -> None:
        self._renderer = DriveTopdownRenderer()
        self._run: RunState | None = None
        self._road: RoadModel | None = None
        self._logic: DriveLogic | None = None
        self._objects: DriveObjects | None = None
        self._seed = 0
        self._seed_nonce = 0
        self._progress_s = 0.0
        self._speed_min = 84.0
        self._speed_max = 126.0
        self._speed_now = 0.0
        self._speed_phase = 0.0
        self._menu_max_curv = 0.008

    def enter(self) -> None:
        self._seed = self._next_seed()
        self._init_world(self._seed)

    def update(self, dt: float) -> None:
        dt = max(0.0, dt)
        road = self._road
        logic = self._logic
        if road is None or logic is None:
            self._seed = self._next_seed()
            self._init_world(self._seed)
            road = self._road
            logic = self._logic
            if road is None or logic is None:
                return

        self._speed_phase += dt * 0.55
        curvature_now = road.curvature_at(self._progress_s)
        target_speed = self._target_speed_for_curvature(curvature_now)
        speed_now = self._speed_now
        if speed_now < target_speed:
            speed_now += self._MENU_SPEED_ACCEL_PER_SEC * dt
            if speed_now > target_speed:
                speed_now = target_speed
        else:
            speed_now -= self._MENU_SPEED_DECEL_PER_SEC * dt
            if speed_now < target_speed:
                speed_now = target_speed
        speed_now = max(0.0, speed_now)
        self._speed_now = speed_now
        self._progress_s += speed_now * dt
        if self._progress_s > road.segment_total_length - 160.0:
            self._seed = self._next_seed()
            self._init_world(self._seed)
            road = self._road
            logic = self._logic
            if road is None or logic is None:
                return

        s = self._progress_s
        cx, cy, dir_x, dir_y = self._sample_centerline_and_dir(road, s)
        right_x = -dir_y
        right_y = dir_x

        # Small scripted lane motion so the car actually "drives" and turns,
        # instead of looking like static road scrolling under it.
        lane_amp = road.width_at(s) * self._MENU_LANE_SWAY_N
        desired_d = lane_amp * math.sin(s * self._MENU_LANE_SWAY_FREQ)
        wx = cx + right_x * desired_d
        wy = cy + right_y * desired_d

        s_ahead = s + 28.0
        s_ahead = min(road.segment_total_length, s_ahead)
        cx2, cy2, dir2_x, dir2_y = self._sample_centerline_and_dir(road, s_ahead)
        right2_x = -dir2_y
        right2_y = dir2_x
        desired_d2 = (
            road.width_at(s_ahead)
            * self._MENU_LANE_SWAY_N
            * math.sin(s_ahead * self._MENU_LANE_SWAY_FREQ)
        )
        wx2 = cx2 + right2_x * desired_d2
        wy2 = cy2 + right2_y * desired_d2

        raw_fwd_x = wx2 - wx
        raw_fwd_y = wy2 - wy
        raw_l2 = raw_fwd_x * raw_fwd_x + raw_fwd_y * raw_fwd_y
        if raw_l2 > 0.0001:
            inv_raw = 1.0 / (raw_l2 ** 0.5)
            raw_fwd_x *= inv_raw
            raw_fwd_y *= inv_raw
        else:
            raw_fwd_x = dir_x
            raw_fwd_y = dir_y

        fwd_x = logic.fwd_x + (raw_fwd_x - logic.fwd_x) * 0.22
        fwd_y = logic.fwd_y + (raw_fwd_y - logic.fwd_y) * 0.22
        l2 = fwd_x * fwd_x + fwd_y * fwd_y
        if l2 > 0.0001:
            inv = 1.0 / (l2 ** 0.5)
            fwd_x *= inv
            fwd_y *= inv
        else:
            fwd_x = raw_fwd_x
            fwd_y = raw_fwd_y

        turn_n = self._curvature_n(curvature_now)
        side_ratio = self._menu_side_ratio(turn_n)
        # For menu-autopilot drift visualization we intentionally invert
        # curvature->side-slip sign to match skid slant direction in top-down view.
        turn_sign = -1.0
        if curvature_now < 0.0:
            turn_sign = 1.0
        right_fwd_x = -fwd_y
        right_fwd_y = fwd_x
        side_speed = self._speed_now * side_ratio * turn_sign
        vx = fwd_x * self._speed_now + right_fwd_x * side_speed
        vy = fwd_y * self._speed_now + right_fwd_y * side_speed
        # Menu preview is scripted: keep handbrake debug channel neutral.
        logic.set_preview_motion_state(wx, wy, fwd_x, fwd_y, vx, vy, 0.0)

    def draw(self, x: int, y: int, w: int, h: int) -> None:
        road = self._road
        logic = self._logic
        objects = self._objects
        if road is None or logic is None or objects is None:
            return
        if w <= 0 or h <= 0:
            return

        clip(x, y, w, h)
        panel_center_x = x + int(w * 0.5)
        panel_center_y = y + int(h * self._MENU_VIEW_CENTER_Y_N)
        self._renderer.draw(
            road,
            logic,
            objects,
            None,
            None,
            None,
            0.0,
            0.0,
            False,
            panel_center_x,
            panel_center_y,
            self._MENU_RENDER_BACK_S,
            self._MENU_RENDER_FORWARD_S,
            self._MENU_SKID_SLIP_THRESHOLD,
            self._MENU_SKID_MIN_SPEED
        )
        clip(0, 0, 240, 136)

    def _sample_centerline_and_dir(
        self,
        road: RoadModel,
        s: float
    ) -> tuple[float, float, float, float]:
        if s <= 0.0:
            cx0, cy0, dx0, dy0 = road.center_point_at_index(0)
            return cx0, cy0, dx0, dy0

        ds = float(road.ds)
        if ds <= 0.0:
            ds = 1.0

        n = road.center_points_len()
        if n <= 1:
            cx0, cy0, dx0, dy0 = road.center_point_at_index(0)
            return cx0, cy0, dx0, dy0

        pos = s / ds
        i0 = int(pos)
        i0 = max(0, i0)
        if i0 >= n - 1:
            i0 = n - 1
        i1 = i0 + 1
        if i1 >= n:
            i1 = n - 1

        t = pos - float(i0)
        t = max(0.0, min(1.0, t))

        x0, y0, d0x, d0y = road.center_point_at_index(i0)
        x1, y1, d1x, d1y = road.center_point_at_index(i1)
        cx = x0 + (x1 - x0) * t
        cy = y0 + (y1 - y0) * t
        dx = d0x + (d1x - d0x) * t
        dy = d0y + (d1y - d0y) * t
        l2 = dx * dx + dy * dy
        if l2 > 0.0001:
            inv = 1.0 / (l2 ** 0.5)
            dx *= inv
            dy *= inv
        else:
            dx = d0x
            dy = d0y
        return cx, cy, dx, dy

    def _next_seed(self) -> int:
        self._seed_nonce = (self._seed_nonce + 1) & 0xFFFFFFFF
        mixed = (int(time()) ^ self._seed_nonce ^ int(self._seed)) & 0xFFFFFFFF
        seed = lcg_next_u32(mixed)
        if seed == 0:
            seed = 0x12345678
        return seed

    def _build_menu_road(self, seed: int) -> RoadModel:
        d = TUNING.DRIVE
        max_curv = float(d.max_curvature) * 0.44 * 1.30
        max_curv = max(0.0007, min(float(d.max_curvature), max_curv))
        self._menu_max_curv = max_curv
        straight_curv = max_curv * 0.50
        straight_curv = max(0.00025, straight_curv)
        return RoadModel(
            seed,
            6400.0,
            float(d.safe_start_length) + 200.0,
            float(d.ds),
            float(d.road_width),
            float(d.min_piece_length) * 1.5,
            float(d.max_piece_length) * 2.2,
            max_curv,
            0.74,
            straight_curv,
            0.35
        )

    def _init_world(self, seed: int) -> None:
        hp = float(TUNING.PROFILE.start_garage_hp)
        fuel = float(TUNING.PROFILE.start_garage_fuel) * 30.0
        self._run = RunState(seed, hp, fuel)
        self._road = self._build_menu_road(seed)
        self._logic = DriveLogic(self._run, self._road, TUNING)
        self._objects = DriveObjects([], [])
        self._progress_s = 0.0
        self._speed_now = 0.0
        self._speed_phase = 0.0
        if self._logic is not None:
            self._logic.refresh_road_projection()

    def _curvature_n(self, curvature: float) -> float:
        c = curvature
        if c < 0.0:
            c = -c
        ref = self._menu_max_curv
        ref = max(0.0001, ref)
        n = c / ref
        n = max(0.0, min(1.0, n))
        return n

    def _target_speed_for_curvature(self, curvature: float) -> float:
        turn_n = self._curvature_n(curvature)
        straight_n = 1.0 - turn_n
        base = self._speed_min + (self._speed_max - self._speed_min) * straight_n
        pulse = math.sin(self._speed_phase)
        pulse_amp = 0.04 + 0.06 * straight_n
        speed = base * (1.0 + pulse * pulse_amp)
        if turn_n > 0.75:
            speed -= (turn_n - 0.75) * (self._speed_max - self._speed_min) * 0.35
        speed = max(self._speed_min, min(self._speed_max, speed))
        return speed

    def _menu_side_ratio(self, turn_n: float) -> float:
        side_slip_n = (turn_n - self._MENU_SIDE_TURN_START_N) / (1.0 - self._MENU_SIDE_TURN_START_N)
        side_slip_n = max(0.0, min(1.0, side_slip_n))
        if side_slip_n <= 0.0:
            return 0.0
        # Keep menu skid close to in-game look: mild side slip, no extreme drift.
        return self._MENU_SIDE_RATIO_BASE + side_slip_n * self._MENU_SIDE_RATIO_ADD

def make_main_menu_backdrop() -> MainMenuBackdrop:
    return SimpleRoadBackdrop()
