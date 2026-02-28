from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Final

class SceneId:
    MAIN_MENU: Final = "MAIN_MENU"
    GARAGE: Final = "GARAGE"
    REGION_MAP: Final = "REGION_MAP"
    DRIVE_PRESET: Final = "DRIVE_PRESET"
    DRIVE: Final = "DRIVE"
    POI: Final = "POI"
    RESULT: Final = "RESULT"
