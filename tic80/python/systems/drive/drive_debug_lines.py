from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...core.run_state import RunState
    from ...data.tuning import Tuning
    from .drive_logic_core import DriveLogic
    from .drive_objects import DriveObjects
    from .road_model import RoadModel


def drive_debug_lines(
    road: RoadModel,
    logic: DriveLogic,
    run: RunState,
    objects: DriveObjects,
    tuning: Tuning
) -> list[str]:
    """Строки для DebugOverlay, чтобы HUD не накладывался на оверлей."""

    def f2(v: float) -> str:
        return f"{v:.2f}"

    vmax_road = logic.estimated_vmax_road()
    vmax_off = logic.estimated_vmax_offroad()

    lines = [
        "drive seed=" + str(run.seed) + " obs=" +
        str(objects.obstacles_count())
        + " zones=" + str(objects.zones_count()),
        "drive s=" + str(int(logic.road_s)) + "/" +
        str(int(road.segment_total_length)),
        "drive d=" + f2(logic.road_d),
        "drive v=" + f2(logic.v_forward) + " side=" + f2(logic.v_side),
        "drive spd=" + f2(logic.speed) + " vmax=" +
        f2(vmax_road) + "/" + f2(vmax_off),
        "drive surf=" + ("OFF" if logic.offroad else "ROAD")
        + " sf=" + f2(logic.dbg_speed_factor)
        + " ss=" + f2(logic.dbg_steer_scale)
        + " hb=" + f2(logic.dbg_handbrake_decel),
        "drive grip=" + f2(logic.dbg_effective_grip) +
        " damp=" + f2(logic.dbg_side_damp)
        + " rec=" + f2(logic.dbg_side_recovery)
        + " fuel/s=" + f2(logic.dbg_fuel_per_sec),
        "drive boost fwd=" + f2(logic.dbg_zone_boost_forward)
        + " ctr=" + f2(logic.dbg_zone_boost_center)
        + " as=" + f2(logic.dbg_zone_antislip),
        "drive fuel=" + f2(run.car_fuel),
        "drive hp=" + f2(run.car_hp)
    ]
    if logic.offroad:
        lines.append("drive OFFROAD")
    return lines

