from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import btnp, cls, print, trace

    from ..contracts import DriveEnterParams, SceneNavigator
    from ..core.input_buttons import Button
    from ..core.palette import Color
    from ..core.scene_ids import SceneId
    from ..data.tuning import TUNING


DRIVE_PHYSICS_FIELDS = [
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


class DrivePhysicsSnapshot:
    def __init__(self, drive) -> None:
        self._values = []
        for name in DRIVE_PHYSICS_FIELDS:
            self._values.append((name, getattr(drive, name)))

    def apply(self, drive) -> None:
        for name, value in self._values:
            setattr(drive, name, value)


class DrivePhysicsPreset:
    def __init__(self, name: str, label: str, overrides: list[tuple[str, float]]) -> None:
        self.name = name
        self.label = label
        self.overrides = overrides

    def apply(self, drive, baseline: DrivePhysicsSnapshot) -> None:
        baseline.apply(drive)
        for name, value in self.overrides:
            setattr(drive, name, value)

    def diff_lines(self, baseline: DrivePhysicsSnapshot, drive) -> list[str]:
        base = baseline._values
        diffs: list[str] = []
        for name, base_value in base:
            current = getattr(drive, name)
            if current == base_value:
                continue
            diffs.append(
                name
                + ": "
                + str(base_value)
                + " -> "
                + str(current)
            )
        return diffs


class DrivePresetScene:
    SCENE_ID = SceneId.DRIVE_PRESET

    def __init__(self, nav: SceneNavigator) -> None:
        self._nav = nav
        self._state = nav.state
        self._selected = 0
        self._baseline: DrivePhysicsSnapshot | None = None
        self._presets = [
            DrivePhysicsPreset(
                "etomarat",
                "etomarat (default)",
                []
            ),
            DrivePhysicsPreset(
                "Masha",
                "Masha (easy)",
                [
                    ("grip", 4.0),
                    ("side_friction", 7.0),
                    ("side_slip_speed_mult", 1.2),
                    ("handbrake_grip_mult", 0.7),
                    ("steer_scale_min", 0.7),
                    ("steer_rate", 1.45),
                    ("offroad_steer_mult", 0.9),
                    ("drag_quad", 0.006)
                ]
            ),
            DrivePhysicsPreset(
                "Skellybob56",
                "Skellybob56 (slippy drift)",
                [
                    ("grip", 2.9),
                    ("side_friction", 4.1),
                    ("side_slip_speed_mult", 4.2),
                    ("handbrake_grip_mult", 0.35),
                    ("side_recovery_mult", 0.55),
                    ("side_recovery_max_add", 5.0),
                    ("handbrake_steer_mult", 1.8),
                    ("handbrake_steer_min_speed_factor", 0.2),
                    ("steer_rate", 1.45),
                    ("steer_scale_min", 0.65)
                ]
            ),
            DrivePhysicsPreset(
                "Boris",
                "Boris (mid-speed steer+accel)",
                [
                    ("accel", 65.0),
                    ("steer_rate", 1.45),
                    ("steer_scale_min", 0.65),
                    ("steer_scale_max", 1.05),
                    ("side_slip_speed_mult", 3.0),
                    ("drag_quad", 0.005)
                ]
            )
        ]

    def enter(self, params: object | None = None) -> None:
        self._state.end_run()
        self._baseline = DrivePhysicsSnapshot(TUNING.DRIVE)
        self._selected = 0

    def update(self, dt: float) -> None:
        if btnp(Button.LEFT) or btnp(Button.UP):
            self._selected = (self._selected - 1) % len(self._presets)
        if btnp(Button.RIGHT) or btnp(Button.DOWN):
            self._selected = (self._selected + 1) % len(self._presets)
        if btnp(Button.A):
            baseline = self._baseline
            if baseline is None:
                return
            preset = self._presets[self._selected]
            preset.apply(TUNING.DRIVE, baseline)
            diffs = preset.diff_lines(baseline, TUNING.DRIVE)
            trace("drive preset: " + preset.name)
            if len(diffs) == 0:
                trace("drive preset: no changes")
            else:
                for line in diffs:
                    trace("drive preset: " + line)
            self._nav.go(SceneId.DRIVE, DriveEnterParams("travel", "topdown"))

    def draw(self) -> None:
        cls(Color.BLACK)
        print('!!!DRIVING PLAYTEST MODE!!!', 52, 14, Color.WHITE)
        print("DRIVE PHYSICS PRESET", 52, 34, Color.WHITE)
        y = 44
        for i, preset in enumerate(self._presets):
            marker = ">" if i == self._selected else " "
            print(marker + " " + preset.label, 50, y, Color.WHITE)
            y += 10
        print("ARROWS: SELECT", 60, 112, Color.LIGHT_GREY)
        print("A (Z): START", 70, 122, Color.LIGHT_GREY)

    def exit(self) -> None:
        pass


def make_drive_preset_scene(nav: SceneNavigator) -> "DrivePresetScene":
    return DrivePresetScene(nav)
