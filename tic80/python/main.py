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
    from .data.tuning import *
    from .scenes.stub_scene import *

include("data.tuning")
include("core.debug")
include("scenes.stub_scene")

_debug_inited: bool = False


def TIC() -> None:
    global _debug_inited
    dt = TUNING["CORE"]["dt"]

    if not _debug_inited:
        debug_set_enabled(TUNING["DEBUG"]["overlay_default"])
        _debug_inited = True

    debug_handle_input()
    stub_scene_update(dt)
    stub_scene_draw()

    debug_draw(
        [
            "scene=STUB",
            "dt=" + str(dt),
        ]
    )
