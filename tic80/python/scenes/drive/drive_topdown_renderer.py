from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import spr

    from ...core.palette import Color
    from ...core.sprites import NIVA_TOPDOWN
    from ...data.tuning import TUNING
    from ...systems.drive.drive_fx import TopdownProjector
    from ...systems.drive.drive_logic_core import DriveLogic
    from ...systems.drive.drive_objects import DriveObjects, DriveZone
    from ...systems.drive.road_model import RoadModel
    from .topdown_debug_draw import TopdownDebugDraw
    from .topdown_fx_overlay import TopdownFxOverlay
    from .topdown_obstacles_draw import TopdownObstaclesDraw
    from .topdown_road_draw import TopdownRoadDraw
    from .topdown_skid_marks import TopdownSkidMarks


class DriveTopdownRenderer:
    """Рендер DRIVE в варианте A (top-down).

    Задача класса: только рисовать. Никаких изменений состояния RunState/DriveLogic.
    """

    def __init__(self) -> None:
        self._road_draw = TopdownRoadDraw()
        self._obstacles_draw = TopdownObstaclesDraw()
        self._skid_marks = TopdownSkidMarks()
        self._debug_draw = TopdownDebugDraw()
        self._fx_overlay = TopdownFxOverlay()

    def notify_obstacle_hit(
        self,
        contact_wx: float,
        contact_wy: float,
        normal_x: float,
        normal_y: float,
        impact: float,
        damage: float,
        hitbox_radius: float
    ) -> None:
        self._fx_overlay.notify_obstacle_hit(
            contact_wx,
            contact_wy,
            normal_x,
            normal_y,
            impact,
            damage,
            hitbox_radius
        )

    def draw(
        self,
        road: RoadModel,
        logic: DriveLogic,
        objects: DriveObjects,
        active_zone: DriveZone | None
    ) -> None:
        center_x = 120
        center_y = self._road_draw.clamp_center_y(int(TUNING.DRIVE.view_center_y))

        p_s = logic.road_s
        car_x = logic.x
        car_y = logic.y
        fwd_x = logic.fwd_x
        fwd_y = logic.fwd_y
        right_x = -fwd_y
        right_y = fwd_x

        proj = TopdownProjector(car_x, car_y, fwd_x, fwd_y, center_x, center_y)

        start_idx, end_idx = self._road_draw.visible_index_range(road, p_s)
        zones = objects.zones_items_view()
        self._road_draw.draw_road_edges_and_zones(
            road,
            zones,
            start_idx,
            end_idx,
            car_x,
            car_y,
            fwd_x,
            fwd_y,
            right_x,
            right_y,
            center_x,
            center_y
        )

        if TUNING.DRIVE.debug_zones_enabled:
            i = 0
            while i < len(zones):
                z = zones[i]
                color = Color.GREEN
                if active_zone is not None and z is active_zone:
                    color = Color.WHITE
                self._road_draw.draw_zone_outline(
                    road,
                    z,
                    start_idx,
                    end_idx,
                    car_x,
                    car_y,
                    fwd_x,
                    fwd_y,
                    right_x,
                    right_y,
                    center_x,
                    center_y,
                    color
                )
                i += 1

        obstacles = objects.obstacles_items_view()
        self._obstacles_draw.draw(
            obstacles,
            road,
            p_s,
            car_x,
            car_y,
            fwd_x,
            fwd_y,
            right_x,
            right_y,
            center_x,
            center_y
        )

        # FX/следы лучше рисовать ДО машины, чтобы кузов перекрывал их.
        start_move = self._fx_overlay.update(road, logic, center_x, center_y, proj)
        if start_move:
            self._skid_marks.trigger_start(float(TUNING.DRIVE.start_skid_seconds))
        self._skid_marks.update_and_draw(logic, center_x, center_y)

        # Следы шин должны быть ПОД пылью/дымом.
        self._fx_overlay.draw_world()

        # Стартовый дым/пыль рисуем ВЫШЕ skid marks, но НИЖЕ кузова.
        self._fx_overlay.draw_under_car()
        self._draw_car_sprite(logic.steer_input, center_x, center_y)
        self._fx_overlay.draw_over_car()

        if TUNING.DRIVE.debug_vectors_enabled:
            self._debug_draw.draw_vectors(logic, center_x, center_y)
        if TUNING.DRIVE.debug_hitboxes_enabled:
            self._debug_draw.draw_hitboxes(logic.steer_input, center_x, center_y)

    def _draw_car_sprite(self, steer_input: int, center_x: int, center_y: int) -> None:
        steer_input = 0
        ax = int(TUNING.DRIVE.car_sprite_anchor_x)
        ay = int(TUNING.DRIVE.car_sprite_anchor_y)
        NIVA_TOPDOWN.draw(steer_input, center_x - ax, center_y - ay)
