from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...data.tuning import Tuning
    from .drive_logic_core import DriveLogic
    from .drive_objects import DriveZone


def apply_zone_effects(logic: DriveLogic, zone: DriveZone | None, tuning: Tuning) -> None:
    """Применяет эффекты зоны к DriveLogic на следующий кадр.

    Вынесено из DriveScene, чтобы:
    - не раздувать сцену логикой drive-систем
    - держать “зоны” и их эффекты рядом с zone-логикой
    """
    if zone is None:
        logic.set_zone_grip_mult(1.0)
        logic.set_zone_boost(0.0, 0.0)
        logic.set_zone_antislip(0.0)
        logic.set_zone_grip_floor(0.0)
        return

    d = tuning.DRIVE
    logic.set_zone_grip_mult(zone.grip_mult)
    logic.set_zone_boost(d.zone_boost_forward_accel, d.zone_boost_center_accel)
    logic.set_zone_antislip(d.zone_antislip)
    logic.set_zone_grip_floor(d.zone_grip_floor)

