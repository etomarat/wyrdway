class PoiTuning:
    __slots__ = (
        "timer_seconds",
        "poi_type_weights",
        "gas_station_scrap_min",
        "gas_station_scrap_max",
        "gas_station_fuel_min",
        "gas_station_fuel_max",
        "scrapyard_scrap_min",
        "scrapyard_scrap_max",
        "scrapyard_fuel_min",
        "scrapyard_fuel_max",
        "depot_scrap_min",
        "depot_scrap_max",
        "depot_fuel_min",
        "depot_fuel_max"
    )

    def __init__(self) -> None:
        self.timer_seconds = 0.0
        self.poi_type_weights: list[float] = []
        self.gas_station_scrap_min = 0
        self.gas_station_scrap_max = 0
        self.gas_station_fuel_min = 0
        self.gas_station_fuel_max = 0
        self.scrapyard_scrap_min = 0
        self.scrapyard_scrap_max = 0
        self.scrapyard_fuel_min = 0
        self.scrapyard_fuel_max = 0
        self.depot_scrap_min = 0
        self.depot_scrap_max = 0
        self.depot_fuel_min = 0
        self.depot_fuel_max = 0
