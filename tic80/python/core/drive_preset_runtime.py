from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..contracts import PursuerVariantId
    from ..contracts import PursuerVariantTuning
    from ..contracts import DriveTuning
    from .drive_presets import DrivePresetId
    from ..data.tuning import TUNING
    from ..data.tuning.pursuers import (
        ENTITY_PURSUER_PROFILE,
        PRIME_ENTITY_PURSUER_PROFILE
    )
    from .drive_presets import (
        DrivePresetIdValues,
        drive_preset_clamp
    )


_DRIVE_FIELDS: list[str] = [
    "slip_eps_speed",
    "max_speed",
    "speed_cap",
    "max_reverse_speed",
    "accel",
    "brake",
    "coast_decel",
    "steer_rate",
    "steer_scale_max",
    "steer_scale_min",
    "steer_min_speed",
    "steer_reverse_mult",
    "handbrake_decel",
    "handbrake_decel_min_speed_factor",
    "handbrake_decel_throttle_turn_mult",
    "handbrake_decel_throttle_straight_mult",
    "handbrake_steer_mult",
    "handbrake_steer_min_speed_factor",
    "side_recovery_mult",
    "side_recovery_max_add",
    "side_recovery_min_speed_factor",
    "dash_impulse",
    "dash_cooldown",
    "offroad_steer_mult",
    "grip",
    "side_friction",
    "side_slip_speed_mult",
    "handbrake_grip_mult",
    "offroad_grip_mult",
    "offroad_drag_lin",
    "offroad_drag_quad",
    "offroad_fuel_mult",
    "offroad_damage_per_sec",
    "offroad_damage_min_speed",
    "drag_lin",
    "drag_quad",
    "fuel_per_sec_idle",
    "fuel_per_sec_throttle"
]

_PURSUER_FIELDS: list[str] = [
    "base_speed"
]

_DRIVE_OVERRIDES_NORMAL: list[tuple[str, float]] = [
    ("grip", 2.9),
    ("side_friction", 4.1),
    ("side_slip_speed_mult", 4.2),
    ("handbrake_grip_mult", 0.35),
    ("side_recovery_mult", 0.38),
    ("side_recovery_max_add", 3.2),
    ("handbrake_steer_mult", 1.8),
    ("handbrake_steer_min_speed_factor", 0.2),
    ("steer_rate", 1.45),
    ("steer_scale_min", 0.65)
]

_DRIVE_OVERRIDES_EASY: list[tuple[str, float]] = [
    ("grip", 4.0),
    ("side_friction", 7.0),
    ("side_slip_speed_mult", 1.2),
    ("handbrake_grip_mult", 0.7),
    ("steer_scale_min", 0.7),
    ("steer_rate", 1.45),
    ("offroad_steer_mult", 0.9),
    ("drag_quad", 0.006)
]

_PURSUER_OVERRIDES_EASY: list[tuple[str, float]] = [
    ("base_speed", 95.0)
]


class DrivePresetRuntime:
    def __init__(self) -> None:
        self._drive_baseline: list[tuple[str, float]] | None = None
        self._entity_baseline: list[tuple[str, float]] | None = None
        self._prime_baseline: list[tuple[str, float]] | None = None

    def capture_baseline_once(self) -> None:
        if self._drive_baseline is not None:
            return
        self._drive_baseline = _capture_drive(TUNING.DRIVE)
        self._entity_baseline = _capture_pursuer(ENTITY_PURSUER_PROFILE)
        self._prime_baseline = _capture_pursuer(PRIME_ENTITY_PURSUER_PROFILE)

    def apply_by_id(self, preset_id: DrivePresetId) -> None:
        self.capture_baseline_once()
        pid = drive_preset_clamp(int(preset_id))
        drive_baseline = self._drive_baseline
        entity_baseline = self._entity_baseline
        prime_baseline = self._prime_baseline
        if drive_baseline is None:
            return
        if entity_baseline is None:
            return
        if prime_baseline is None:
            return

        _apply_drive_baseline(TUNING.DRIVE, drive_baseline)
        _apply_pursuer_baseline(ENTITY_PURSUER_PROFILE, entity_baseline)
        _apply_pursuer_baseline(PRIME_ENTITY_PURSUER_PROFILE, prime_baseline)

        if pid == int(DrivePresetIdValues.NORMAL):
            _apply_overrides(TUNING.DRIVE, _DRIVE_OVERRIDES_NORMAL)
            return
        if pid == int(DrivePresetIdValues.EASY):
            _apply_overrides(TUNING.DRIVE, _DRIVE_OVERRIDES_EASY)
            active = _resolve_active_pursuer_profile()
            _apply_overrides(active, _PURSUER_OVERRIDES_EASY)


def _resolve_active_pursuer_profile() -> PursuerVariantTuning:
    variant = TUNING.PURSUER.active_variant
    if variant == PursuerVariantId.PRIME_ENTITY:
        return PRIME_ENTITY_PURSUER_PROFILE
    return ENTITY_PURSUER_PROFILE


def _capture_drive(drive: DriveTuning) -> list[tuple[str, float]]:
    out: list[tuple[str, float]] = []
    i = 0
    while i < len(_DRIVE_FIELDS):
        name = _DRIVE_FIELDS[i]
        out.append((name, getattr(drive, name)))
        i += 1
    return out


def _capture_pursuer(profile: PursuerVariantTuning) -> list[tuple[str, float]]:
    out: list[tuple[str, float]] = []
    i = 0
    while i < len(_PURSUER_FIELDS):
        name = _PURSUER_FIELDS[i]
        out.append((name, getattr(profile, name)))
        i += 1
    return out


def _apply_drive_baseline(drive: DriveTuning, baseline: list[tuple[str, float]]) -> None:
    _apply_overrides(drive, baseline)


def _apply_pursuer_baseline(profile: PursuerVariantTuning, baseline: list[tuple[str, float]]) -> None:
    _apply_overrides(profile, baseline)


def _apply_overrides(target: object, overrides: list[tuple[str, float]]) -> None:
    i = 0
    while i < len(overrides):
        name, value = overrides[i]
        setattr(target, name, value)
        i += 1
