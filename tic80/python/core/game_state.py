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
                 '_playtest_enabled', '_playtest_time', '_playtest_segments',
                 '_debug_overlay_enabled')

    def __init__(self) -> None:
        self._profile = Profile(
            TUNING.PROFILE.start_scrap,
            TUNING.PROFILE.start_garage_hp,
            TUNING.PROFILE.start_garage_fuel
        )
        self._save = SaveSystem()
        self._run: RunState | None = None
        self._seed_counter = 1
        self._profile_loaded = False
        self._profile_tuning_mismatch = False
        self._profile_tuning_version: int | None = None
        self._debug_lines: list[str] = []
        self._playtest_enabled = False
        self._playtest_time = 0.0
        self._playtest_segments = 0
        self._debug_overlay_enabled = False

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
    def playtest_enabled(self) -> bool:
        return self._playtest_enabled

    @property
    def debug_overlay_enabled(self) -> bool:
        return self._debug_overlay_enabled

    def set_debug_overlay_enabled(self, enabled: bool) -> None:
        self._debug_overlay_enabled = bool(enabled)

    def playtest_begin(self) -> None:
        """Сбрасывает статистику DRIVE-плейтеста (режим “одна дорога за другой”)."""
        self._playtest_enabled = True
        self._playtest_time = 0.0
        self._playtest_segments = 0

    def playtest_add_time(self, dt: float) -> None:
        """Добавляет время плейтеста (секунды)."""
        if not self._playtest_enabled:
            return
        self._playtest_time += float(dt)

    def playtest_finish_segment(self) -> None:
        """Отмечает, что одна дорога пройдена до конца."""
        if not self._playtest_enabled:
            return
        self._playtest_segments += 1

    def playtest_stats(self) -> tuple[int, float]:
        """Возвращает (segments, seconds)."""
        return (self._playtest_segments, self._playtest_time)

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
        self._run = RunState(self._seed_counter,
                             self._profile.garage_hp,
                             self._profile.garage_fuel)
        return self._run

    def end_run(self) -> None:
        self._run = None

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
        self._run = None

    def rollback_to_last_save(self) -> None:
        data = self._save.load_profile()
        if data is None:
            self._profile.reset()
            self._profile_loaded = False
            self._profile_tuning_mismatch = False
            self._profile_tuning_version = None
        else:
            self._profile.apply_save(data.scrap, data.garage_hp, data.garage_fuel)
            self._profile_loaded = True
            self._profile_tuning_version = data.tuning_version
            self._profile_tuning_mismatch = (
                data.tuning_version != int(TUNING.tuning_version)
            )
        self._run = None

    def load_profile(self) -> None:
        data = self._save.load_profile()
        if data is None:
            self._profile_loaded = False
            self._profile_tuning_mismatch = False
            self._profile_tuning_version = None
            return
        self._profile.apply_save(data.scrap, data.garage_hp, data.garage_fuel)
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
            self._profile.garage_fuel
        )

    def require_run(self) -> RunState:
        if self._run is None:
            return self.start_run()
        return self._run
