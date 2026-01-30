# title:   Wyrdway
# author:  Marat Azizov, t.me/etomarat, @etomarat
# desc:    A content-driven road-trip roguelite game: drive between strange POIs, do quick loot raids, extract, and upgrade your car in the garage to survive escalating anomalies. 
# site:    https://github.com/etomarat
# license: MIT License (change this to your license of choice)
# version: 0.1
# script:  python

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import btnp, include

    from .core.debug import debug_draw, debug_handle_input, debug_set_enabled
    from .core.input_buttons import Button
    from .core.scene_ids import SceneId
    from .core.scene_manager import (
        scene_manager_draw,
        scene_manager_get_current_id,
        scene_manager_go,
        scene_manager_register,
        scene_manager_update
    )
    from .data.tuning import TUNING
    from .scenes.drive_scene import (
        drive_scene_draw,
        drive_scene_enter,
        drive_scene_exit,
        drive_scene_update
    )
    from .scenes.garage_scene import (
        garage_scene_draw,
        garage_scene_enter,
        garage_scene_exit,
        garage_scene_update
    )
    from .scenes.poi_scene import (
        poi_scene_draw,
        poi_scene_enter,
        poi_scene_exit,
        poi_scene_update
    )
    from .scenes.region_map_scene import (
        region_map_scene_draw,
        region_map_scene_enter,
        region_map_scene_exit,
        region_map_scene_update
    )
    from .scenes.result_scene import (
        result_scene_draw,
        result_scene_enter,
        result_scene_exit,
        result_scene_update
    )

include("data.tuning")
include("core.debug")
include("core.input_buttons")
include("core.scene_ids")
include("core.scene_manager")
include("scenes.drive_scene")
include("scenes.garage_scene")
include("scenes.poi_scene")
include("scenes.region_map_scene")
include("scenes.result_scene")

def BOOT() -> None:
    debug_set_enabled(TUNING["DEBUG"]["overlay_default"])
    scene_manager_register(
        SceneId.GARAGE,
        {
            "enter": garage_scene_enter,
            "update": garage_scene_update,
            "draw": garage_scene_draw,
            "exit": garage_scene_exit,
        },
    )
    scene_manager_register(
        SceneId.REGION_MAP,
        {
            "enter": region_map_scene_enter,
            "update": region_map_scene_update,
            "draw": region_map_scene_draw,
            "exit": region_map_scene_exit,
        },
    )
    scene_manager_register(
        SceneId.DRIVE,
        {
            "enter": drive_scene_enter,
            "update": drive_scene_update,
            "draw": drive_scene_draw,
            "exit": drive_scene_exit,
        },
    )
    scene_manager_register(
        SceneId.POI,
        {
            "enter": poi_scene_enter,
            "update": poi_scene_update,
            "draw": poi_scene_draw,
            "exit": poi_scene_exit,
        },
    )
    scene_manager_register(
        SceneId.RESULT,
        {
            "enter": result_scene_enter,
            "update": result_scene_update,
            "draw": result_scene_draw,
            "exit": result_scene_exit,
        },
    )
    scene_manager_go(SceneId.GARAGE)


def TIC() -> None:
    dt = TUNING["CORE"]["dt"]

    debug_handle_input()
    current_scene = scene_manager_get_current_id()
    if current_scene == SceneId.GARAGE:
        if btnp(Button.A):
            scene_manager_go(SceneId.REGION_MAP)
    elif current_scene == SceneId.REGION_MAP:
        if btnp(Button.A):
            scene_manager_go(SceneId.DRIVE, {"mode": "travel"})
    elif current_scene == SceneId.DRIVE:
        if btnp(Button.A):
            scene_manager_go(SceneId.POI)
    elif current_scene == SceneId.POI:
        if btnp(Button.A):
            scene_manager_go(SceneId.RESULT, {"text": "LOOT OK"})
        elif btnp(Button.B):
            scene_manager_go(SceneId.RESULT, {"text": "LEFT EARLY"})
    elif current_scene == SceneId.RESULT:
        if btnp(Button.A):
            scene_manager_go(SceneId.GARAGE)
    scene_manager_update(dt)
    scene_manager_draw()

    debug_draw(
        [
            "scene=" + (current_scene if current_scene else "None"),
            "dt=" + str(dt),
        ],
    )
