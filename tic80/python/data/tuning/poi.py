from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..tuning import TUNING


TUNING.POI.timer_seconds = 10.0

# Весы выбора типа POI: [gas_station, scrapyard, depot]
TUNING.POI.poi_type_weights = [35.0, 35.0, 30.0]

# gas_station: fuel-heavy
TUNING.POI.gas_station_scrap_min = 1
TUNING.POI.gas_station_scrap_max = 6
TUNING.POI.gas_station_fuel_min = 24
TUNING.POI.gas_station_fuel_max = 40

# scrapyard: scrap-heavy
TUNING.POI.scrapyard_scrap_min = 20
TUNING.POI.scrapyard_scrap_max = 34
TUNING.POI.scrapyard_fuel_min = 0
TUNING.POI.scrapyard_fuel_max = 2

# depot: balanced
TUNING.POI.depot_scrap_min = 10
TUNING.POI.depot_scrap_max = 16
TUNING.POI.depot_fuel_min = 10
TUNING.POI.depot_fuel_max = 16
