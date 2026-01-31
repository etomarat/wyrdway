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
                 '_profile_tuning_version')

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
    def profile_tuning_mismatch(self) -> bool:
        return self._profile_tuning_mismatch

    @property
    def profile_tuning_version(self) -> int | None:
        return self._profile_tuning_version

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
        final_fuel = run.car_fuel

        if failed:
            fuel_loss = max(TUNING.PROFILE.evac_fuel_min,
                            final_fuel * TUNING.PROFILE.evac_fuel_pct)
            final_fuel = max(0.0, final_fuel - fuel_loss)
            self._profile.add_scrap(-TUNING.PROFILE.evac_scrap_loss)
        else:
            for item in run.inventory_items():
                if item.id == "scrap":
                    self._profile.add_scrap(item.qty)

        self._profile.set_garage_stats(run.car_hp, final_fuel)
        self.save_profile()
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
