# title:   Wyrdway
# author:  Marat Azizov, t.me/etomarat, @etomarat
# desc:    A content-driven road-trip roguelite game: drive between strange POIs, do quick loot raids, extract, and upgrade your car in the garage to survive escalating anomalies. 
# site:    https://github.com/etomarat
# license: MIT License (change this to your license of choice)
# version: 0.1
# script:  python

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import *
    from .core.debug import *
    from .core.scene_manager import *
    from .data.tuning import *
    from .scenes.drive_scene import *
    from .scenes.garage_scene import *
    from .scenes.poi_scene import *
    from .scenes.region_map_scene import *
    from .scenes.result_scene import *

include("data.tuning")
include("core.debug")
include("core.scene_manager")
include("scenes.drive_scene")
include("scenes.garage_scene")
include("scenes.poi_scene")
include("scenes.region_map_scene")
include("scenes.result_scene")

SCENE_GARAGE = "GARAGE"
SCENE_REGION_MAP = "REGION_MAP"
SCENE_DRIVE = "DRIVE"
SCENE_POI = "POI"
SCENE_RESULT = "RESULT"

def BOOT() -> None:
    debug_set_enabled(TUNING["DEBUG"]["overlay_default"])
    scene_manager_register(
        SCENE_GARAGE,
        {
            "enter": garage_scene_enter,
            "update": garage_scene_update,
            "draw": garage_scene_draw,
            "exit": garage_scene_exit,
        },
    )
    scene_manager_register(
        SCENE_REGION_MAP,
        {
            "enter": region_map_scene_enter,
            "update": region_map_scene_update,
            "draw": region_map_scene_draw,
            "exit": region_map_scene_exit,
        },
    )
    scene_manager_register(
        SCENE_DRIVE,
        {
            "enter": drive_scene_enter,
            "update": drive_scene_update,
            "draw": drive_scene_draw,
            "exit": drive_scene_exit,
        },
    )
    scene_manager_register(
        SCENE_POI,
        {
            "enter": poi_scene_enter,
            "update": poi_scene_update,
            "draw": poi_scene_draw,
            "exit": poi_scene_exit,
        },
    )
    scene_manager_register(
        SCENE_RESULT,
        {
            "enter": result_scene_enter,
            "update": result_scene_update,
            "draw": result_scene_draw,
            "exit": result_scene_exit,
        },
    )
    scene_manager_go(SCENE_GARAGE)


def TIC() -> None:
    dt = TUNING["CORE"]["dt"]

    debug_handle_input()
    current_scene = scene_manager_get_current_id()
    if current_scene == SCENE_GARAGE:
        if btnp(4):
            scene_manager_go(SCENE_REGION_MAP)
    elif current_scene == SCENE_REGION_MAP:
        if btnp(4):
            scene_manager_go(SCENE_DRIVE, {"mode": "travel"})
    elif current_scene == SCENE_DRIVE:
        if btnp(4):
            scene_manager_go(SCENE_POI)
    elif current_scene == SCENE_POI:
        if btnp(4):
            scene_manager_go(SCENE_RESULT, {"text": "LOOT OK"})
        elif btnp(5):
            scene_manager_go(SCENE_RESULT, {"text": "LEFT EARLY"})
    elif current_scene == SCENE_RESULT:
        if btnp(4):
            scene_manager_go(SCENE_GARAGE)
    scene_manager_update(dt)
    scene_manager_draw()

    debug_draw(
        [
            "scene=" + str(current_scene),
            "dt=" + str(dt),
        ]
    )
