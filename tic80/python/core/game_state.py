from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import trace

    from ..data.tuning import TUNING
    from .profile import Profile
    from .run_state import RunState
    from .save_system import SaveSystem


class GameState:
    __slots__ = ('_profile', '_run', '_seed_counter', '_save',
                 '_profile_loaded', '_profile_tuning_mismatch',
                 '_profile_tuning_version', '_debug_lines',
                 '_debug_overlay_enabled', '_last_rollback_reason',
                 '_last_rollback_theseus_gain')

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
    def debug_overlay_enabled(self) -> bool:
        return self._debug_overlay_enabled

    @property
    def debug_enabled(self) -> bool:
        return bool(TUNING.DEBUG.debug_enabled)

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

    def start_run(self) -> RunState:
        self._seed_counter += 1
        self._last_rollback_reason = None
        self._last_rollback_theseus_gain = 0
        self._run = RunState(self._seed_counter,
                             self._profile.garage_hp,
                             self._profile.garage_fuel)
        return self._run

    def end_run(self) -> None:
        self._run = None
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
        delta = run.delta
        failed = delta is not None and delta.escape_outcome == "fail"
        if not failed:
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
            self._profile_loaded = False
            self._profile_tuning_mismatch = False
            self._profile_tuning_version = None
            return
        self._profile.apply_save(data.scrap, data.garage_hp, data.garage_fuel, data.theseus)
        self._seed_counter = data.seed_counter
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

    def start_new_game(self) -> None:
        self._profile.reset()
        self._seed_counter = 0
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
