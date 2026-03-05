from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import cls, print, trace

    from ..contracts import (
        DriveEnterParams,
        DriveTuning,
        PursuerVariantId,
        PursuerVariantTuning,
        SceneEnterParams,
        SceneNavigator
    )
    from ..core.controls.actions import Action
    from ..core.drive_presets import (
        DrivePresetId,
        DrivePresetIdValues,
        drive_preset_clamp
    )
    from ..core.palette import Color
    from ..core.scene_ids import SceneId
    from ..core.ui.prompts import (
        ui_prompt_for_action,
        ui_prompt_for_nav_hint,
        ui_prompt_with_text
    )
    from ..core.ui.release_latch import UiReleaseLatch
    from ..core.ui.rich_text import ui_rich_print
    from ..core.version import GAME_VERSION
    from ..data.tuning import TUNING
    from ..data.tuning.pursuers import (
        ENTITY_PURSUER_PROFILE,
        PRIME_ENTITY_PURSUER_PROFILE
    )


DRIVE_PHYSICS_FIELDS: list[str] = [
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

PURSUER_PROFILE_FIELDS: list[str] = [
    "base_speed"
]


class DrivePhysicsSnapshot:
    def __init__(self, drive: DriveTuning) -> None:
        self._values: list[tuple[str, float]] = []
        for name in DRIVE_PHYSICS_FIELDS:
            self._values.append((name, getattr(drive, name)))

    def apply(self, drive: DriveTuning) -> None:
        for name, value in self._values:
            setattr(drive, name, value)


class DrivePhysicsPreset:
    def __init__(
        self,
        option_id: DrivePresetId,
        name: str,
        label: str,
        drive_overrides: list[tuple[str, float]],
        pursuer_overrides: list[tuple[str, float]] | None = None
    ) -> None:
        self.option_id: DrivePresetId = drive_preset_clamp(int(option_id))
        self.name = name
        self.label = label
        self.drive_overrides = drive_overrides
        self.pursuer_overrides = []
        if pursuer_overrides is not None:
            self.pursuer_overrides = pursuer_overrides

    def apply(
        self,
        drive: DriveTuning,
        drive_baseline: DrivePhysicsSnapshot,
        pursuer_profile: PursuerVariantTuning,
        pursuer_baseline: "PursuerProfileSnapshot"
    ) -> None:
        drive_baseline.apply(drive)
        pursuer_baseline.apply(pursuer_profile)
        for name, value in self.drive_overrides:
            setattr(drive, name, value)
        for name, value in self.pursuer_overrides:
            setattr(pursuer_profile, name, value)

    def diff_lines(
        self,
        drive_baseline: DrivePhysicsSnapshot,
        drive: DriveTuning,
        pursuer_baseline: "PursuerProfileSnapshot",
        pursuer_profile: PursuerVariantTuning
    ) -> list[str]:
        diffs: list[str] = []
        for name, base_value in drive_baseline._values:
            current = getattr(drive, name)
            if current == base_value:
                continue
            diffs.append(
                "drive."
                + name
                + ": "
                + str(base_value)
                + " -> "
                + str(current)
            )
        for name, base_value in pursuer_baseline._values:
            current = getattr(pursuer_profile, name)
            if current == base_value:
                continue
            diffs.append(
                "pursuer."
                + name
                + ": "
                + str(base_value)
                + " -> "
                + str(current)
            )
        return diffs


class PursuerProfileSnapshot:
    def __init__(self, profile: PursuerVariantTuning) -> None:
        self._values: list[tuple[str, float]] = []
        for name in PURSUER_PROFILE_FIELDS:
            self._values.append((name, getattr(profile, name)))

    def apply(self, profile: PursuerVariantTuning) -> None:
        for name, value in self._values:
            setattr(profile, name, value)


def resolve_active_pursuer_profile() -> PursuerVariantTuning:
    variant = TUNING.PURSUER.active_variant
    if variant == PursuerVariantId.PRIME_ENTITY:
        return PRIME_ENTITY_PURSUER_PROFILE
    return ENTITY_PURSUER_PROFILE


class DrivePresetEngine:
    def __init__(self) -> None:
        self._drive_baseline: DrivePhysicsSnapshot | None = None
        self._pursuer_baseline: PursuerProfileSnapshot | None = None

    def capture_baseline(self) -> None:
        self._drive_baseline = DrivePhysicsSnapshot(TUNING.DRIVE)
        self._pursuer_baseline = PursuerProfileSnapshot(
            resolve_active_pursuer_profile()
        )

    def apply_preset(self, preset: DrivePhysicsPreset) -> list[str] | None:
        drive_baseline = self._drive_baseline
        pursuer_baseline = self._pursuer_baseline
        if drive_baseline is None or pursuer_baseline is None:
            return None

        pursuer_profile = resolve_active_pursuer_profile()
        preset.apply(
            TUNING.DRIVE,
            drive_baseline,
            pursuer_profile,
            pursuer_baseline
        )
        return preset.diff_lines(
            drive_baseline,
            TUNING.DRIVE,
            pursuer_baseline,
            pursuer_profile
        )


class DrivePresetScene:
    SCENE_ID = SceneId.DRIVE_PRESET

    def __init__(self, nav: SceneNavigator) -> None:
        self._nav = nav
        self._state = nav.state
        self._release = UiReleaseLatch()
        self._selected = 0
        self._engine = DrivePresetEngine()
        self._presets = [
            DrivePhysicsPreset(
                DrivePresetIdValues.HARD,
                "etomarat",
                "hard",
                []
            ),
            DrivePhysicsPreset(
                DrivePresetIdValues.NORMAL,
                "Skellybob56",
                "normal (slippy drift)",
                [
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
                ],
                # [("base_speed", 108.0)]
            ),
            # НЕ УДАЛЯТЬ: временно отключенный пресет easy accel.
            # DrivePhysicsPreset(
            #     DrivePresetIdValues.NORMAL,
            #     "bfeen",
            #     "easy accel (mid-speed steer+accel)",
            #     [
            #         ("accel", 65.0),
            #         ("steer_rate", 1.45),
            #         ("steer_scale_min", 0.65),
            #         ("steer_scale_max", 1.05),
            #         ("side_slip_speed_mult", 3.0),
            #         ("drag_quad", 0.005)
            #     ],
            #     # [("base_speed", 107.0)]
            # ),
            DrivePhysicsPreset(
                DrivePresetIdValues.EASY,
                "Masha",
                "easy",
                [
                    ("grip", 4.0),
                    ("side_friction", 7.0),
                    ("side_slip_speed_mult", 1.2),
                    ("handbrake_grip_mult", 0.7),
                    ("steer_scale_min", 0.7),
                    ("steer_rate", 1.45),
                    ("offroad_steer_mult", 0.9),
                    ("drag_quad", 0.006)
                ],
                [("base_speed", 95.0)]
            ),
        ]

    def enter(self, params: SceneEnterParams = None) -> None:
        self._release.sync_actions_from_controls(
            self._state.controls,
            [
                Action.NAV_LEFT,
                Action.NAV_UP,
                Action.NAV_RIGHT,
                Action.NAV_DOWN,
                Action.CONFIRM,
                Action.SECONDARY
            ]
        )
        self._state.end_run()
        self._engine.capture_baseline()
        self._selected = self._selected_index_for_state()

    def _selected_index_for_state(self) -> int:
        i = 0
        selected_id = drive_preset_clamp(int(self._state.drive_preset_id))
        while i < len(self._presets):
            if int(self._presets[i].option_id) == int(selected_id):
                return i
            i += 1
        return 0

    def _apply_selected_preset(self) -> bool:
        preset = self._presets[self._selected]
        diffs = self._engine.apply_preset(preset)
        if diffs is None:
            return False
        self._state.set_drive_preset_id(drive_preset_clamp(int(preset.option_id)))
        self._state.save_options()
        trace("drive preset: " + preset.name)
        if len(diffs) == 0:
            trace("drive preset: no changes")
        else:
            for line in diffs:
                trace("drive preset: " + line)
        return True

    def _start_chase_test(self) -> None:
        run = self._state.start_run()
        run.ensure_outbound_segment(1, float(TUNING.DRIVE.segment_total_length))
        run.ensure_return_from_active_outbound()
        test_scrap = run.run_scrap()
        if test_scrap < 20:
            run.add_item("scrap", 20 - test_scrap)
        trace("drive preset: chase test start")
        self._nav.go(SceneId.DRIVE, DriveEnterParams("extract"))

    def _chase_test_allowed(self) -> bool:
        return (
            self._state.debug_enabled
            and bool(TUNING.DEBUG.drive_preset_chase_test_enabled)
        )

    def update(self, dt: float) -> None:
        nav_left_released = self._release.poll(self._state.controls, Action.NAV_LEFT)
        nav_up_released = self._release.poll(self._state.controls, Action.NAV_UP)
        nav_right_released = self._release.poll(self._state.controls, Action.NAV_RIGHT)
        nav_down_released = self._release.poll(self._state.controls, Action.NAV_DOWN)
        confirm_released = self._release.poll(self._state.controls, Action.CONFIRM)
        secondary_released = self._release.poll(self._state.controls, Action.SECONDARY)

        if (
            nav_left_released
            or nav_up_released
        ):
            self._selected = (self._selected - 1) % len(self._presets)
        if (
            nav_right_released
            or nav_down_released
        ):
            self._selected = (self._selected + 1) % len(self._presets)
        if confirm_released:
            if not self._apply_selected_preset():
                return
            self._nav.go(SceneId.GARAGE)
        elif secondary_released:
            if not self._chase_test_allowed():
                return
            if not self._apply_selected_preset():
                return
            self._start_chase_test()

    def draw(self) -> None:
        cls(Color.BLACK)
        print("DRIVE PHYSICS PRESET (PLAYTEST)", 52, 34, Color.WHITE)
        y = 44
        for i, preset in enumerate(self._presets):
            marker = ">" if i == self._selected else " "
            print(marker + " " + preset.label, 52, y, Color.WHITE)
            y += 10
        ui_rich_print(ui_prompt_with_text(ui_prompt_for_nav_hint(self._state), "SELECT"), 52, 106, Color.LIGHT_GREY)
        ui_rich_print(ui_prompt_with_text(ui_prompt_for_action(self._state, Action.CONFIRM), "CONTINUE"), 52, 114, Color.LIGHT_GREY)
        if self._chase_test_allowed():
            ui_rich_print(ui_prompt_with_text(ui_prompt_for_action(self._state, Action.SECONDARY), "CHASE TEST"), 52, 122, Color.LIGHT_GREY)
        print("v" + GAME_VERSION, 0, 2, Color.GREY)

    def exit(self) -> None:
        pass


def make_drive_preset_scene(nav: SceneNavigator) -> DrivePresetScene:
    return DrivePresetScene(nav)
