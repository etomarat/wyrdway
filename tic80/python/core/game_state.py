from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..contracts import Profile, RunState
    from ..data.tuning import TUNING


class GameState:
    __slots__ = ("profile", "run", "_seed_counter")

    def __init__(self) -> None:
        self.profile = Profile(
            TUNING.PROFILE.start_money,
            TUNING.PROFILE.start_garage_hp,
            TUNING.PROFILE.start_garage_fuel,
        )
        self.run: RunState | None = None
        self._seed_counter = 1

    def start_run(self) -> RunState:
        seed = self._seed_counter
        self._seed_counter += 1
        self.run = RunState(seed, self.profile.garage_hp, self.profile.garage_fuel)
        return self.run

    def end_run(self) -> None:
        self.run = None

    def require_run(self) -> RunState:
        if self.run is None:
            return self.start_run()
        return self.run
