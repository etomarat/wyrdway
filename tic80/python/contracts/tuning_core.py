class CoreTuning:
    __slots__ = ["dt"]

    def __init__(self) -> None:
        self.dt = 0.0


class DebugTuning:
    __slots__ = ["debug_enabled", "overlay_default", "perf_overlay_default"]

    def __init__(self) -> None:
        self.debug_enabled = False
        self.overlay_default = False
        self.perf_overlay_default = False


class ProfileTuning:
    __slots__ = (
        "start_scrap",
        "start_garage_hp",
        "start_garage_fuel",
        "repair_cost",
        "repair_hp",
        "evac_fuel_pct",
        "evac_fuel_min",
        "evac_scrap_loss",
        "rollback_theseus_gain",
        "rollback_theseus_chase_bonus"
    )

    def __init__(self) -> None:
        self.start_scrap = 0
        self.start_garage_hp = 0.0
        self.start_garage_fuel = 0.0
        self.repair_cost = 0
        self.repair_hp = 0.0
        self.evac_fuel_pct = 0.0
        self.evac_fuel_min = 0.0
        self.evac_scrap_loss = 0
        self.rollback_theseus_gain = 0
        self.rollback_theseus_chase_bonus = 0
