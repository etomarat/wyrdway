from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..data.tuning import TUNING
    from .profile import Profile
    from .run_state import RunState


class GameState:
    __slots__ = ('_profile', '_run', '_seed_counter')

    def __init__(self) -> None:
        self._profile = Profile(
            TUNING.PROFILE.start_scrap,
            TUNING.PROFILE.start_garage_hp,
            TUNING.PROFILE.start_garage_fuel,
        )
        self._run: RunState | None = None
        self._seed_counter = 1

    @property
    def profile(self) -> Profile:
        return self._profile

    @property
    def run(self) -> RunState | None:
        return self._run

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
        self._run = None

    def require_run(self) -> RunState:
        if self._run is None:
            return self.start_run()
        return self._run
