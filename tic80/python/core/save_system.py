from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import pmem, trace

    from ..data.tuning import TUNING


# Версия схемы сохранения профиля (менять при несовместимых изменениях).
# Поднимать, если меняется формат/слоты/интерпретация данных:
# - добавили/удалили/переименовали поля
# - изменили масштаб/единицы хранения
# - поменяли смысл значения
SAVE_SCHEMA_VERSION = 6
# Магическая сигнатура, чтобы отличать наш сейв от "мусора".
SAVE_MAGIC = 0x57595244  # "WYRD"

# Индексы pmem-слотов (0..255). Храним только профиль (без run).
PMEM_MAGIC_SLOT = 0               # сигнатура сейва
PMEM_SCHEMA_SLOT = 1              # версия схемы
# Это именно индекс слота, а не значение версии. Саму версию берём из TUNING.
PMEM_TUNING_VERSION_SLOT = 2
PMEM_PROFILE_SEED_COUNTER_SLOT = 3  # последний seed_counter для новых run
PMEM_PROFILE_SCRAP_SLOT = 10      # scrap (int)
PMEM_PROFILE_GARAGE_HP_X100_SLOT = 11  # hp гаражной машины * 100 (int)
PMEM_PROFILE_GARAGE_FUEL_X100_SLOT = 12  # fuel * 100 (int), т.к. pmem = int
PMEM_PROFILE_THESEUS_SLOT = 13  # индекс "переписывания" героя (int)
PMEM_RUN_ACTIVE_SLOT = 20  # флаг "ран в процессе" (1/0)
PMEM_CHASE_ACTIVE_SLOT = 21  # флаг "контакт с сущностью в процессе" (1/0)

# Единый коэффициент масштаба для float-полей (храним float как int).
FLOAT_SCALE = 100.0


class SaveProfileData:
    __slots__ = ("scrap", "garage_hp", "garage_fuel", "theseus", "tuning_version", "seed_counter")

    def __init__(
        self,
        scrap: int,
        garage_hp: float,
        garage_fuel: float,
        theseus: int,
        tuning_version: int,
        seed_counter: int
    ) -> None:
        self.scrap = scrap
        self.garage_hp = garage_hp
        self.garage_fuel = garage_fuel
        self.theseus = max(0, int(theseus))
        self.tuning_version = tuning_version
        self.seed_counter = max(0, int(seed_counter))


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
        theseus = int(pmem(PMEM_PROFILE_THESEUS_SLOT))
        if theseus < 0:
            theseus = 0
        tuning_version = int(pmem(PMEM_TUNING_VERSION_SLOT))
        seed_counter = int(pmem(PMEM_PROFILE_SEED_COUNTER_SLOT))
        if seed_counter < 0:
            seed_counter = 0

        return SaveProfileData(scrap, garage_hp, garage_fuel, theseus, tuning_version, seed_counter)

    def save_profile(self, scrap: int, garage_hp: float, garage_fuel: float, theseus: int, seed_counter: int) -> None:
        # Заголовок сейва.
        pmem(PMEM_MAGIC_SLOT, SAVE_MAGIC)
        pmem(PMEM_SCHEMA_SLOT, SAVE_SCHEMA_VERSION)
        pmem(PMEM_TUNING_VERSION_SLOT, int(TUNING.tuning_version))
        pmem(PMEM_PROFILE_SEED_COUNTER_SLOT, max(0, int(seed_counter)))

        # Поля профиля.
        pmem(PMEM_PROFILE_SCRAP_SLOT, max(0, int(scrap)))
        hp_raw = int(round(garage_hp * FLOAT_SCALE))
        pmem(PMEM_PROFILE_GARAGE_HP_X100_SLOT, max(0, hp_raw))

        # Топливо храним как int (float * FLOAT_SCALE).
        fuel_raw = int(round(garage_fuel * FLOAT_SCALE))
        pmem(PMEM_PROFILE_GARAGE_FUEL_X100_SLOT, max(0, fuel_raw))
        pmem(PMEM_PROFILE_THESEUS_SLOT, max(0, int(theseus)))

    def load_runtime_flags(self) -> tuple[bool, bool]:
        run_active = int(pmem(PMEM_RUN_ACTIVE_SLOT)) != 0
        chase_active = int(pmem(PMEM_CHASE_ACTIVE_SLOT)) != 0
        return (run_active, chase_active)

    def save_runtime_flags(self, run_active: bool, chase_active: bool) -> None:
        pmem(PMEM_RUN_ACTIVE_SLOT, 1 if run_active else 0)
        pmem(PMEM_CHASE_ACTIVE_SLOT, 1 if chase_active else 0)
