# title:   Wyrdway
# author:  Marat Azizov, t.me/etomarat, @etomarat
# desc:    A content-driven road-trip roguelite game: drive between strange POIs, do quick loot raids, extract, and upgrade your car in the garage to survive escalating anomalies.  # noqa: E501
# site:    https://github.com/etomarat
# license: MIT License (change this to your license of choice)
# version: 0.1
# script:  python

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import include

    from .core.class_probe import class_probe_get_lines
    from .core.debug import debug_draw, debug_handle_input, debug_set_enabled
    from .core.scene_ids import SceneId
    from .core.scene_manager import SceneManager
    from .data.tuning import TUNING
    from .scenes.drive_scene import make_drive_scene
    from .scenes.garage_scene import make_garage_scene
    from .scenes.poi_scene import make_poi_scene
    from .scenes.region_map_scene import make_region_map_scene
    from .scenes.result_scene import make_result_scene

include("contracts")
include("data.tuning")
include("core.class_probe")
include("core.debug")
include("core.input_buttons")
include("core.game_state")
include("core.scene_ids")
include("core.scene_manager")
include("scenes.drive_scene")
include("scenes.garage_scene")
include("scenes.poi_scene")
include("scenes.region_map_scene")
include("scenes.result_scene")


SCENE_MANAGER = SceneManager()


def BOOT() -> None:
    debug_set_enabled(TUNING.DEBUG.overlay_default)
    SCENE_MANAGER.register(SceneId.GARAGE, make_garage_scene)
    SCENE_MANAGER.register(SceneId.REGION_MAP, make_region_map_scene)
    SCENE_MANAGER.register(SceneId.DRIVE, make_drive_scene)
    SCENE_MANAGER.register(SceneId.POI, make_poi_scene)
    SCENE_MANAGER.register(SceneId.RESULT, make_result_scene)
    SCENE_MANAGER.go(SceneId.GARAGE)


def TIC() -> None:
    dt = TUNING.CORE.dt

    debug_handle_input()
    SCENE_MANAGER.update(dt)
    SCENE_MANAGER.draw()

    lines = [
        "scene=" + str(SCENE_MANAGER.current_id),
        "dt=" + str(dt),
    ]
    lines.extend(class_probe_get_lines())
    debug_draw(lines)
