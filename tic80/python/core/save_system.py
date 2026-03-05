from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import pmem, trace

    from ..data.tuning import TUNING
    from .campaign_seed import hash_seed_text_u32, normalize_seed_text
    from .controls.modes import InputDeviceMode, InputDeviceModeId
    from .drive_presets import DrivePresetId, drive_preset_clamp


# Версия схемы сохранения профиля (менять при несовместимых изменениях).
# Поднимать, если меняется формат/слоты/интерпретация данных:
# - добавили/удалили/переименовали поля
# - изменили масштаб/единицы хранения
# - поменяли смысл значения
SAVE_SCHEMA_VERSION = 7
# Магическая сигнатура, чтобы отличать наш сейв от "мусора".
SAVE_MAGIC = 0x57595244  # "WYRD"
OPTIONS_SCHEMA_VERSION = 1
OPTIONS_MAGIC = 0x4F505453  # "OPTS"

# Индексы pmem-слотов (0..255). Профиль, runtime-флаги и отдельный блок опций.
PMEM_MAGIC_SLOT = 0               # сигнатура сейва
PMEM_SCHEMA_SLOT = 1              # версия схемы
# Это именно индекс слота, а не значение версии. Саму версию берём из TUNING.
PMEM_TUNING_VERSION_SLOT = 2
PMEM_PROFILE_RUN_INDEX_SLOT = 3  # количество запущенных run в кампании
PMEM_PROFILE_CAMPAIGN_SEED_U32_SLOT = 4
PMEM_PROFILE_CAMPAIGN_SEED_LEN_SLOT = 5
PMEM_PROFILE_SCRAP_SLOT = 10      # scrap (int)
PMEM_PROFILE_GARAGE_HP_X100_SLOT = 11  # hp гаражной машины * 100 (int)
PMEM_PROFILE_GARAGE_FUEL_X100_SLOT = 12  # fuel * 100 (int), т.к. pmem = int
PMEM_PROFILE_THESEUS_SLOT = 13  # индекс "переписывания" героя (int)
PMEM_PROFILE_SEED_TEXT_BASE_SLOT = 40
PMEM_PROFILE_SEED_TEXT_MAX_CHARS = 16
PMEM_RUN_ACTIVE_SLOT = 20  # флаг "ран в процессе" (1/0)
PMEM_CHASE_ACTIVE_SLOT = 21  # флаг "контакт с сущностью в процессе" (1/0)
PMEM_OPTIONS_MAGIC_SLOT = 30
PMEM_OPTIONS_SCHEMA_SLOT = 31
PMEM_OPTIONS_INPUT_MODE_SLOT = 32
PMEM_OPTIONS_SHOW_SHOULDERS_SLOT = 33
PMEM_OPTIONS_VIBRATION_SLOT = 34
PMEM_OPTIONS_DRIVE_PRESET_SLOT = 35

# Единый коэффициент масштаба для float-полей (храним float как int).
FLOAT_SCALE = 100.0


def normalize_input_device_mode(mode: int) -> InputDeviceModeId:
    mode_i = int(mode)
    if mode_i == int(InputDeviceMode.GAMEPAD):
        return InputDeviceMode.GAMEPAD
    if mode_i == int(InputDeviceMode.KEYBOARD):
        return InputDeviceMode.KEYBOARD
    return InputDeviceMode.BOTH


class SaveProfileData:
    __slots__ = (
        "scrap",
        "garage_hp",
        "garage_fuel",
        "theseus",
        "tuning_version",
        "run_index",
        "campaign_seed_text",
        "campaign_seed_u32"
    )

    def __init__(
        self,
        scrap: int,
        garage_hp: float,
        garage_fuel: float,
        theseus: int,
        tuning_version: int,
        run_index: int,
        campaign_seed_text: str,
        campaign_seed_u32: int
    ) -> None:
        self.scrap = scrap
        self.garage_hp = garage_hp
        self.garage_fuel = garage_fuel
        self.theseus = max(0, int(theseus))
        self.tuning_version = tuning_version
        self.run_index = max(0, int(run_index))
        self.campaign_seed_text = normalize_seed_text(campaign_seed_text)
        h = int(campaign_seed_u32) & 0xFFFFFFFF
        if h == 0:
            h = hash_seed_text_u32(self.campaign_seed_text)
        self.campaign_seed_u32 = int(h)


class SaveOptionsData:
    __slots__ = ("input_device_mode", "show_shoulders", "vibration_enabled", "drive_preset_id")

    def __init__(
        self,
        input_device_mode: InputDeviceModeId,
        show_shoulders: bool,
        vibration_enabled: bool,
        drive_preset_id: DrivePresetId
    ) -> None:
        mode = normalize_input_device_mode(int(input_device_mode))
        self.input_device_mode = mode
        self.show_shoulders = bool(show_shoulders)
        self.vibration_enabled = bool(vibration_enabled)
        self.drive_preset_id = drive_preset_clamp(int(drive_preset_id))


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
        run_index = int(pmem(PMEM_PROFILE_RUN_INDEX_SLOT))
        if run_index < 0:
            run_index = 0

        campaign_seed_u32 = int(pmem(PMEM_PROFILE_CAMPAIGN_SEED_U32_SLOT)) & 0xFFFFFFFF
        seed_len = int(pmem(PMEM_PROFILE_CAMPAIGN_SEED_LEN_SLOT))
        if seed_len < 0:
            seed_len = 0
        if seed_len > PMEM_PROFILE_SEED_TEXT_MAX_CHARS:
            seed_len = PMEM_PROFILE_SEED_TEXT_MAX_CHARS
        campaign_seed_text = ""
        i = 0
        while i < seed_len:
            code = int(pmem(PMEM_PROFILE_SEED_TEXT_BASE_SLOT + i)) & 0xFF
            if code != 0:
                campaign_seed_text += chr(code)
            i += 1
        campaign_seed_text = normalize_seed_text(campaign_seed_text)
        if campaign_seed_u32 == 0:
            campaign_seed_u32 = hash_seed_text_u32(campaign_seed_text)

        return SaveProfileData(
            scrap,
            garage_hp,
            garage_fuel,
            theseus,
            tuning_version,
            run_index,
            campaign_seed_text,
            campaign_seed_u32
        )

    def save_profile(
        self,
        scrap: int,
        garage_hp: float,
        garage_fuel: float,
        theseus: int,
        run_index: int,
        campaign_seed_text: str,
        campaign_seed_u32: int
    ) -> None:
        # Заголовок сейва.
        normalized_seed = normalize_seed_text(campaign_seed_text)
        seed_u32 = int(campaign_seed_u32) & 0xFFFFFFFF
        if seed_u32 == 0:
            seed_u32 = hash_seed_text_u32(normalized_seed)

        pmem(PMEM_MAGIC_SLOT, SAVE_MAGIC)
        pmem(PMEM_SCHEMA_SLOT, SAVE_SCHEMA_VERSION)
        pmem(PMEM_TUNING_VERSION_SLOT, int(TUNING.tuning_version))
        pmem(PMEM_PROFILE_RUN_INDEX_SLOT, max(0, int(run_index)))
        pmem(PMEM_PROFILE_CAMPAIGN_SEED_U32_SLOT, int(seed_u32))
        pmem(PMEM_PROFILE_CAMPAIGN_SEED_LEN_SLOT, len(normalized_seed))
        i = 0
        while i < PMEM_PROFILE_SEED_TEXT_MAX_CHARS:
            code = 0
            if i < len(normalized_seed):
                code = ord(normalized_seed[i]) & 0xFF
            pmem(PMEM_PROFILE_SEED_TEXT_BASE_SLOT + i, code)
            i += 1

        # Поля профиля.
        pmem(PMEM_PROFILE_SCRAP_SLOT, max(0, int(scrap)))
        hp_raw = int(round(garage_hp * FLOAT_SCALE))
        pmem(PMEM_PROFILE_GARAGE_HP_X100_SLOT, max(0, hp_raw))

        # Топливо храним как int (float * FLOAT_SCALE).
        fuel_raw = int(round(garage_fuel * FLOAT_SCALE))
        pmem(PMEM_PROFILE_GARAGE_FUEL_X100_SLOT, max(0, fuel_raw))
        pmem(PMEM_PROFILE_THESEUS_SLOT, max(0, int(theseus)))

    def load_options(self) -> SaveOptionsData | None:
        if pmem(PMEM_OPTIONS_MAGIC_SLOT) != OPTIONS_MAGIC:
            return None
        if pmem(PMEM_OPTIONS_SCHEMA_SLOT) != OPTIONS_SCHEMA_VERSION:
            return None

        mode = normalize_input_device_mode(int(pmem(PMEM_OPTIONS_INPUT_MODE_SLOT)))
        show_shoulders = int(pmem(PMEM_OPTIONS_SHOW_SHOULDERS_SLOT)) != 0
        vibration_enabled = int(pmem(PMEM_OPTIONS_VIBRATION_SLOT)) != 0
        drive_preset_id = drive_preset_clamp(int(pmem(PMEM_OPTIONS_DRIVE_PRESET_SLOT)))

        if mode != int(InputDeviceMode.GAMEPAD):
            show_shoulders = False
        if mode == int(InputDeviceMode.KEYBOARD):
            vibration_enabled = False

        return SaveOptionsData(
            mode,
            show_shoulders,
            vibration_enabled,
            drive_preset_id
        )

    def save_options(
        self,
        input_device_mode: InputDeviceModeId,
        show_shoulders: bool,
        vibration_enabled: bool,
        drive_preset_id: DrivePresetId
    ) -> None:
        mode = normalize_input_device_mode(int(input_device_mode))

        shoulders_int = 1 if bool(show_shoulders) else 0
        if mode != int(InputDeviceMode.GAMEPAD):
            shoulders_int = 0

        vibration_int = 1 if bool(vibration_enabled) else 0
        if mode == int(InputDeviceMode.KEYBOARD):
            vibration_int = 0

        pmem(PMEM_OPTIONS_MAGIC_SLOT, OPTIONS_MAGIC)
        pmem(PMEM_OPTIONS_SCHEMA_SLOT, OPTIONS_SCHEMA_VERSION)
        pmem(PMEM_OPTIONS_INPUT_MODE_SLOT, mode)
        pmem(PMEM_OPTIONS_SHOW_SHOULDERS_SLOT, shoulders_int)
        pmem(PMEM_OPTIONS_VIBRATION_SLOT, vibration_int)
        pmem(PMEM_OPTIONS_DRIVE_PRESET_SLOT, int(drive_preset_clamp(int(drive_preset_id))))

    def load_runtime_flags(self) -> tuple[bool, bool]:
        run_active = int(pmem(PMEM_RUN_ACTIVE_SLOT)) != 0
        chase_active = int(pmem(PMEM_CHASE_ACTIVE_SLOT)) != 0
        return (run_active, chase_active)

    def save_runtime_flags(self, run_active: bool, chase_active: bool) -> None:
        pmem(PMEM_RUN_ACTIVE_SLOT, 1 if run_active else 0)
        pmem(PMEM_CHASE_ACTIVE_SLOT, 1 if chase_active else 0)
