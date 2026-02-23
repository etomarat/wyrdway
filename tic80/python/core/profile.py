class Profile:
    __slots__ = ("_scrap", "_garage_hp", "_garage_fuel", "_theseus", "_upgrades",
                 "_start_scrap", "_start_garage_hp", "_start_garage_fuel", "_start_theseus")

    def __init__(self, scrap: int, garage_hp: float, garage_fuel: float) -> None:
        self._scrap = scrap
        self._garage_hp = garage_hp
        self._garage_fuel = garage_fuel
        self._theseus = 0
        self._upgrades: list[str] = []
        self._start_scrap = scrap
        self._start_garage_hp = garage_hp
        self._start_garage_fuel = garage_fuel
        self._start_theseus = 0

    @property
    def scrap(self) -> int:
        return self._scrap

    @property
    def garage_hp(self) -> float:
        return self._garage_hp

    @property
    def garage_fuel(self) -> float:
        return self._garage_fuel

    @property
    def theseus(self) -> int:
        return self._theseus

    @property
    def upgrades(self) -> list[str]:
        return self._upgrades

    def add_scrap(self, qty: int) -> None:
        self._scrap = max(0, self._scrap + qty)

    def spend_scrap(self, cost: int) -> bool:
        if self._scrap < cost:
            return False
        self._scrap -= cost
        return True

    def add_theseus(self, qty: int) -> None:
        self._theseus = max(0, self._theseus + int(qty))

    def set_garage_stats(self, hp: float, fuel: float) -> None:
        self._garage_hp = max(0.0, float(hp))
        self._garage_fuel = max(0.0, float(fuel))

    def repair(self, cost: int, hp_gain: float, hp_max: float) -> bool:
        if self._garage_hp >= hp_max:
            return False
        if not self.spend_scrap(cost):
            return False
        self._garage_hp = min(hp_max, self._garage_hp + hp_gain)
        return True

    def apply_save(self, scrap: int, garage_hp: float, garage_fuel: float, theseus: int) -> None:
        self._scrap = max(0, int(scrap))
        self._garage_hp = max(0.0, float(garage_hp))
        self._garage_fuel = max(0.0, float(garage_fuel))
        self._theseus = max(0, int(theseus))

    def reset(self) -> None:
        self.apply_save(
            self._start_scrap,
            self._start_garage_hp,
            self._start_garage_fuel,
            self._start_theseus
        )
