from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import pmem, trace

    from ..data.tuning import TUNING


# Версия схемы сохранения профиля (менять при несовместимых изменениях).
# Поднимать, если меняется формат/слоты/интерпретация данных:
# - добавили/удалили/переименовали поля
# - изменили масштаб/единицы хранения
# - поменяли смысл значения
SAVE_SCHEMA_VERSION = 3
# Магическая сигнатура, чтобы отличать наш сейв от "мусора".
SAVE_MAGIC = 0x57595244  # "WYRD"

# Индексы pmem-слотов (0..255). Храним только профиль (без run).
PMEM_MAGIC_SLOT = 0               # сигнатура сейва
PMEM_SCHEMA_SLOT = 1              # версия схемы
# Это именно индекс слота, а не значение версии. Саму версию берём из TUNING.
PMEM_TUNING_VERSION_SLOT = 2
PMEM_PROFILE_SCRAP_SLOT = 10      # scrap (int)
PMEM_PROFILE_GARAGE_HP_X100_SLOT = 11  # hp гаражной машины * 100 (int)
PMEM_PROFILE_GARAGE_FUEL_X100_SLOT = 12  # fuel * 100 (int), т.к. pmem = int

# Единый коэффициент масштаба для float-полей (храним float как int).
FLOAT_SCALE = 100.0


class SaveProfileData:
    __slots__ = ("scrap", "garage_hp", "garage_fuel", "tuning_version")

    def __init__(
        self,
        scrap: int,
        garage_hp: float,
        garage_fuel: float,
        tuning_version: int
    ) -> None:
        self.scrap = scrap
        self.garage_hp = garage_hp
        self.garage_fuel = garage_fuel
        self.tuning_version = tuning_version


class SaveSystem:
    """Минимальный профиль-сейв на pmem (M1)."""

    def load_profile(self) -> SaveProfileData | None:
        # Проверяем, что сейв "наш" и нужной версии.
        if pmem(PMEM_MAGIC_SLOT) != SAVE_MAGIC:
            trace("save: no magic, treat as new")
            return None
        if pmem(PMEM_SCHEMA_SLOT) != SAVE_SCHEMA_VERSION:
            trace(
                "save: schema mismatch "
                + str(pmem(PMEM_SCHEMA_SLOT))
                + " != "
                + str(SAVE_SCHEMA_VERSION)
            )
            return None

        # Читаем поля профиля.
        scrap = int(pmem(PMEM_PROFILE_SCRAP_SLOT))
        hp_raw = int(pmem(PMEM_PROFILE_GARAGE_HP_X100_SLOT))
        garage_hp = hp_raw / FLOAT_SCALE
        fuel_raw = int(pmem(PMEM_PROFILE_GARAGE_FUEL_X100_SLOT))
        garage_fuel = fuel_raw / FLOAT_SCALE
        tuning_version = int(pmem(PMEM_TUNING_VERSION_SLOT))

        return SaveProfileData(scrap, garage_hp, garage_fuel, tuning_version)

    def save_profile(self, scrap: int, garage_hp: float, garage_fuel: float) -> None:
        # Заголовок сейва.
        pmem(PMEM_MAGIC_SLOT, SAVE_MAGIC)
        pmem(PMEM_SCHEMA_SLOT, SAVE_SCHEMA_VERSION)
        pmem(PMEM_TUNING_VERSION_SLOT, int(TUNING.tuning_version))

        # Поля профиля.
        pmem(PMEM_PROFILE_SCRAP_SLOT, max(0, int(scrap)))
        hp_raw = int(round(garage_hp * FLOAT_SCALE))
        pmem(PMEM_PROFILE_GARAGE_HP_X100_SLOT, max(0, hp_raw))

        # Топливо храним как int (float * FLOAT_SCALE).
        fuel_raw = int(round(garage_fuel * FLOAT_SCALE))
        pmem(PMEM_PROFILE_GARAGE_FUEL_X100_SLOT, max(0, fuel_raw))
