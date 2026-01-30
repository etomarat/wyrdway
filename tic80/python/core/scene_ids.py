from enum import Enum


class SceneId(str, Enum):
    GARAGE = "GARAGE"
    REGION_MAP = "REGION_MAP"
    DRIVE = "DRIVE"
    POI = "POI"
    RESULT = "RESULT"
