from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...data.tuning import TUNING
    from ...systems.drive.drive_fx import TopdownProjector
    from ...systems.drive.drive_logic_core import DriveLogic


class CarPose2D:
    """Unified car pose for world/screen local-point transforms."""

    def __init__(
        self,
        logic: DriveLogic,
        proj: TopdownProjector,
        center_x: int,
        center_y: int
    ) -> None:
        self._world_x = float(logic.x)
        self._world_y = float(logic.y)
        self._world_fwd_x = float(logic.fwd_x)
        self._world_fwd_y = float(logic.fwd_y)
        self._world_right_x = -self._world_fwd_y
        self._world_right_y = self._world_fwd_x

        self._center_x = float(center_x)
        self._center_y = float(center_y)

        screen_fwd_x, screen_fwd_y = proj.world_vec_to_screen(
            self._world_fwd_x,
            self._world_fwd_y
        )
        l2 = screen_fwd_x * screen_fwd_x + screen_fwd_y * screen_fwd_y
        if l2 > 0.000001:
            inv = 1.0 / (l2 ** 0.5)
            screen_fwd_x *= inv
            screen_fwd_y *= inv
        else:
            screen_fwd_x = 0.0
            screen_fwd_y = -1.0

        self._screen_fwd_x = screen_fwd_x
        self._screen_fwd_y = screen_fwd_y
        self._screen_right_x = -screen_fwd_y
        self._screen_right_y = screen_fwd_x

    def screen_center(self) -> tuple[float, float]:
        return self._center_x, self._center_y

    def local_to_screen(self, local_x: float, local_back: float) -> tuple[float, float]:
        sx = self._center_x + self._screen_right_x * local_x - self._screen_fwd_x * local_back
        sy = self._center_y + self._screen_right_y * local_x - self._screen_fwd_y * local_back
        return sx, sy

    def local_to_world(self, local_x: float, local_back: float) -> tuple[float, float]:
        wx = self._world_x + self._world_right_x * local_x - self._world_fwd_x * local_back
        wy = self._world_y + self._world_right_y * local_x - self._world_fwd_y * local_back
        return wx, wy

    @staticmethod
    def legacy_center_shift() -> tuple[float, float]:
        """Shift from legacy center-based offsets (16,16) to current anchor."""
        anchor_x = float(TUNING.DRIVE.car_sprite_anchor_x)
        anchor_y = float(TUNING.DRIVE.car_sprite_anchor_y)
        return 16.0 - anchor_x, 16.0 - anchor_y
