from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import trace

    from ..contracts import PursuerVariantId
    from ..data.tuning import TUNING
    from .controls.bindings import make_default_bindings
    from .controls.input import Controls
    from .controls.modes import (
        InputDeviceMode,
        InputDeviceModeId,
        PromptGlyphDetail,
        PromptGlyphDetailId
    )
    from .drive_presets import (
        DrivePresetId,
        DrivePresetIdValues,
        drive_preset_clamp
    )
    from .profile import Profile
    from .run_state import RunState
    from .save_system import SaveSystem


class GameState:
    __slots__ = ('_profile', '_run', '_seed_counter', '_save',
                 '_profile_loaded', '_profile_tuning_mismatch',
                 '_profile_tuning_version', '_debug_lines',
                 '_debug_overlay_enabled', '_last_rollback_reason',
                 '_last_rollback_theseus_gain', '_input_device_mode',
                 '_prompt_glyph_detail', '_prompt_show_shoulders',
                 '_vibration_enabled', '_drive_preset_id', '_controls')

    def __init__(self) -> None:
        self._profile = Profile(
            TUNING.PROFILE.start_scrap,
            TUNING.PROFILE.start_garage_hp,
            TUNING.PROFILE.start_garage_fuel
        )
        self._save = SaveSystem()
        self._run: RunState | None = None
        self._seed_counter = 0
        self._profile_loaded = False
        self._profile_tuning_mismatch = False
        self._profile_tuning_version: int | None = None
        self._debug_lines: list[str] = []
        self._debug_overlay_enabled = False
        self._last_rollback_reason: str | None = None
        self._last_rollback_theseus_gain = 0
        # How we show control prompts in UI. This is a user preference; it does
        # not attempt to detect input device.
        self._input_device_mode: InputDeviceModeId = InputDeviceMode.BOTH
        self._prompt_glyph_detail: PromptGlyphDetailId = PromptGlyphDetail.ALL
        self._prompt_show_shoulders = False
        self._vibration_enabled = True
        self._drive_preset_id: DrivePresetId = DrivePresetIdValues.HARD
        self._controls = Controls(make_default_bindings())

    @property
    def profile(self) -> Profile:
        return self._profile

    @property
    def run(self) -> RunState | None:
        return self._run

    @property
    def profile_loaded(self) -> bool:
        return self._profile_loaded

    @property
    def seed_counter(self) -> int:
        return int(self._seed_counter)

    @property
    def debug_overlay_enabled(self) -> bool:
        return self._debug_overlay_enabled

    @property
    def debug_enabled(self) -> bool:
        return bool(TUNING.DEBUG.debug_enabled)

    @property
    def input_device_mode(self) -> InputDeviceModeId:
        return self._input_device_mode

    def set_input_device_mode(self, mode: InputDeviceModeId) -> None:
        self._input_device_mode = mode

    @property
    def prompt_glyph_detail(self) -> PromptGlyphDetailId:
        return self._prompt_glyph_detail

    def set_prompt_glyph_detail(self, detail: PromptGlyphDetailId) -> None:
        self._prompt_glyph_detail = detail

    @property
    def prompt_show_shoulders(self) -> bool:
        return bool(self._prompt_show_shoulders)

    def set_prompt_show_shoulders(self, enabled: bool) -> None:
        self._prompt_show_shoulders = bool(enabled)

    @property
    def vibration_enabled(self) -> bool:
        return bool(self._vibration_enabled)

    def set_vibration_enabled(self, enabled: bool) -> None:
        self._vibration_enabled = bool(enabled)

    @property
    def drive_preset_id(self) -> DrivePresetId:
        return self._drive_preset_id

    def set_drive_preset_id(self, preset_id: DrivePresetId) -> None:
        self._drive_preset_id = drive_preset_clamp(int(preset_id))

    @property
    def controls(self) -> Controls:
        return self._controls

    def set_debug_overlay_enabled(self, enabled: bool) -> None:
        if not self.debug_enabled:
            self._debug_overlay_enabled = False
            return
        self._debug_overlay_enabled = bool(enabled)

    @property
    def profile_tuning_mismatch(self) -> bool:
        return self._profile_tuning_mismatch

    @property
    def profile_tuning_version(self) -> int | None:
        return self._profile_tuning_version

    def clear_debug_lines(self) -> None:
        """Очищает debug-линии кадра.

        Вызов происходит один раз за кадр (в `main.TIC()`), чтобы сцены могли
        безопасно добавлять свои строки и не “залипать” между кадрами.
        """
        self._debug_lines = []

    def set_debug_lines(self, lines: list[str]) -> None:
        """Задаёт список строк, которые сцена хочет видеть в DebugOverlay."""
        self._debug_lines = list(lines)

    def debug_lines(self) -> list[str]:
        """Возвращает копию debug-линий текущего кадра."""
        return list(self._debug_lines)

    def _is_prime_entity_run_seed(self, run_seed: int) -> bool:
        period = int(TUNING.PURSUER.prime_entity_every_runs)
        if period <= 1:
            return True
        seed = int(run_seed)
        if seed <= 0:
            return False
        return (seed % period) == 0

    def _set_pursuer_variant_for_run_seed(self, run_seed: int) -> None:
        if self._is_prime_entity_run_seed(run_seed):
            TUNING.PURSUER.active_variant = PursuerVariantId.PRIME_ENTITY
            return
        TUNING.PURSUER.active_variant = PursuerVariantId.ENTITY

    def _set_pursuer_variant_for_next_run(self) -> None:
        self._set_pursuer_variant_for_run_seed(int(self._seed_counter) + 1)

    def start_run(self) -> RunState:
        self._seed_counter += 1
        self._set_pursuer_variant_for_run_seed(self._seed_counter)
        self._last_rollback_reason = None
        self._last_rollback_theseus_gain = 0
        self._run = RunState(self._seed_counter,
                             self._profile.garage_hp,
                             self._profile.garage_fuel)
        return self._run

    def end_run(self) -> None:
        self._run = None
        self._set_pursuer_variant_for_next_run()
        self._save.save_runtime_flags(False, False)

    def mark_run_active(self) -> None:
        self._save.save_runtime_flags(True, False)

    def mark_chase_active(self) -> None:
        run_active, _ = self._save.load_runtime_flags()
        self._save.save_runtime_flags(run_active or self._run is not None, True)

    def consume_rollback_notice(self) -> tuple[str | None, int]:
        reason = self._last_rollback_reason
        gain = self._last_rollback_theseus_gain
        self._last_rollback_reason = None
        self._last_rollback_theseus_gain = 0
        return (reason, gain)

    def rollback_notice(self) -> tuple[str | None, int]:
        return (self._last_rollback_reason, self._last_rollback_theseus_gain)

    def apply_run_results(self) -> None:
        run = self._run
        if run is None:
            return
        for item in run.inventory_items():
            if item.id == "scrap":
                self._profile.add_scrap(item.qty)

        self._profile.set_garage_stats(run.car_hp, run.car_fuel)
        self.save_profile()
        self.end_run()

    def rollback_to_last_save(self, reason: str, chase_contact: bool = False) -> int:
        data = self._save.load_profile()
        if data is None:
            self._profile.reset()
            self._seed_counter = 0
            self._profile_loaded = False
            self._profile_tuning_mismatch = False
            self._profile_tuning_version = None
        else:
            self._profile.apply_save(data.scrap, data.garage_hp, data.garage_fuel, data.theseus)
            self._seed_counter = data.seed_counter
            self._profile_loaded = True
            self._profile_tuning_version = data.tuning_version
            self._profile_tuning_mismatch = (
                data.tuning_version != int(TUNING.tuning_version)
            )
        gain = int(TUNING.PROFILE.rollback_theseus_gain)
        if chase_contact:
            gain += int(TUNING.PROFILE.rollback_theseus_chase_bonus)
        self._profile.add_theseus(gain)
        self._last_rollback_reason = str(reason)
        self._last_rollback_theseus_gain = gain
        self.end_run()
        self.save_profile()
        return gain

    def load_profile(self) -> None:
        data = self._save.load_profile()
        if data is None:
            self._seed_counter = 0
            self._set_pursuer_variant_for_next_run()
            self._profile_loaded = False
            self._profile_tuning_mismatch = False
            self._profile_tuning_version = None
            return
        self._profile.apply_save(data.scrap, data.garage_hp, data.garage_fuel, data.theseus)
        self._seed_counter = data.seed_counter
        self._set_pursuer_variant_for_next_run()
        self._profile_loaded = True
        self._profile_tuning_version = data.tuning_version
        self._profile_tuning_mismatch = (
            data.tuning_version != int(TUNING.tuning_version)
        )
        trace(
            "save loaded: scrap="
            + str(data.scrap)
            + " hp="
            + str(round(data.garage_hp, 2))
            + " fuel="
            + str(round(data.garage_fuel, 2))
            + " theseus="
            + str(data.theseus)
            + " tuning="
            + str(data.tuning_version)
        )
        if self._profile_tuning_mismatch:
            trace(
                "warning: tuning mismatch save="
                + str(data.tuning_version)
                + " current="
                + str(TUNING.tuning_version)
            )

    def save_profile(self) -> None:
        self._save.save_profile(
            self._profile.scrap,
            self._profile.garage_hp,
            self._profile.garage_fuel,
            self._profile.theseus,
            self._seed_counter
        )

    def load_options(self) -> None:
        data = self._save.load_options()
        if data is None:
            return
        self._input_device_mode = data.input_device_mode
        self._prompt_show_shoulders = bool(data.show_shoulders)
        self._vibration_enabled = bool(data.vibration_enabled)
        self._drive_preset_id = drive_preset_clamp(int(data.drive_preset_id))

    def save_options(self) -> None:
        self._save.save_options(
            self._input_device_mode,
            self._prompt_show_shoulders,
            self._vibration_enabled,
            self._drive_preset_id
        )

    def start_new_game(self) -> None:
        self._profile.reset()
        self._seed_counter = 0
        self._set_pursuer_variant_for_next_run()
        self._last_rollback_reason = None
        self._last_rollback_theseus_gain = 0
        self.end_run()
        self.save_profile()

    def recover_interrupted_session(self) -> bool:
        run_active, chase_active = self._save.load_runtime_flags()
        if not run_active and not chase_active:
            return False
        reason = "RUN INTERRUPTED"
        if chase_active:
            reason = "CHASE INTERRUPTED"
        self.rollback_to_last_save(reason, chase_active)
        return True

    def debug_set_active_run_seed(self, seed: int) -> None:
        next_seed = int(seed)
        if next_seed < 1:
            next_seed = 1
        run = self._run
        if run is None:
            car_hp = self._profile.garage_hp
            car_fuel = self._profile.garage_fuel
        else:
            car_hp = run.car_hp
            car_fuel = run.car_fuel
        self._run = RunState(next_seed, car_hp, car_fuel)
        self._seed_counter = next_seed
        self._set_pursuer_variant_for_run_seed(next_seed)

    def debug_shift_active_run_seed(self, delta: int) -> None:
        run = self._run
        current = self._seed_counter
        if run is not None:
            current = run.seed
        self.debug_set_active_run_seed(current + int(delta))

    def require_run(self) -> RunState:
        if self._run is None:
            return self.start_run()
        return self._run
