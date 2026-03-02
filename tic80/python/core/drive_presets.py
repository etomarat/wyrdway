from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Literal, TypeAlias

    DrivePresetId: TypeAlias = Literal[0, 1, 2]
else:
    DrivePresetId = int


class DrivePresetIdValues:
    HARD: DrivePresetId = 0
    NORMAL: DrivePresetId = 1
    EASY: DrivePresetId = 2


def drive_preset_is_valid(preset_id: int) -> bool:
    pid = int(preset_id)
    return (
        pid == int(DrivePresetIdValues.HARD)
        or pid == int(DrivePresetIdValues.NORMAL)
        or pid == int(DrivePresetIdValues.EASY)
    )


def drive_preset_clamp(preset_id: int) -> DrivePresetId:
    pid = int(preset_id)
    if pid == int(DrivePresetIdValues.NORMAL):
        return DrivePresetIdValues.NORMAL
    if pid == int(DrivePresetIdValues.EASY):
        return DrivePresetIdValues.EASY
    return DrivePresetIdValues.HARD


def drive_preset_label(preset_id: DrivePresetId) -> str:
    pid = drive_preset_clamp(int(preset_id))
    if pid == int(DrivePresetIdValues.NORMAL):
        return "NORMAL"
    if pid == int(DrivePresetIdValues.EASY):
        return "EASY"
    return "HARD"


def drive_preset_cycle(preset_id: DrivePresetId, forward: bool) -> DrivePresetId:
    order: list[DrivePresetId] = [
        DrivePresetIdValues.HARD,
        DrivePresetIdValues.NORMAL,
        DrivePresetIdValues.EASY
    ]
    idx = 0
    i = 0
    current = drive_preset_clamp(int(preset_id))
    while i < len(order):
        if int(order[i]) == int(current):
            idx = i
            break
        i += 1
    if forward:
        idx += 1
        if idx >= len(order):
            idx = 0
    else:
        idx -= 1
        if idx < 0:
            idx = len(order) - 1
    return order[idx]
