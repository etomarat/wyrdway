# title:   Wyrdway
# author:  Marat Azizov, t.me/etomarat, @etomarat
# desc:    A content-driven road-trip roguelite game: drive between strange POIs, do quick loot raids, extract, and upgrade your car in the garage to survive escalating anomalies.  # noqa: E501
# site:    https://github.com/etomarat
# license: MIT License (change this to your license of choice)
# version: 0.1
# script:  python

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import include, keyp

    from .core.debug import DebugOverlay
    from .core.perf_overlay import PerfOverlay
    from .core.scene_ids import SceneId
    from .core.scene_manager import SceneManager
    from .data.tuning import TUNING
    from .scenes.drive_preset_scene import make_drive_preset_scene
    from .scenes.drive_scene import make_drive_scene
    from .scenes.garage_scene import make_garage_scene
    from .scenes.poi_scene import make_poi_scene
    from .scenes.region_map_scene import make_region_map_scene
    from .scenes.result_scene import make_result_scene

include("contracts.__init__")
include("core.palette")
include("data.tuning.__init__")
include("core.__init__")
include("systems.fx.__init__")
include("systems.drive.__init__")
include("scenes.drive.__init__")
include("scenes.drive_scene")
include("scenes.drive_preset_scene")
include("scenes.garage_scene")
include("scenes.poi_scene")
include("scenes.region_map_scene")
include("scenes.result_scene")


SCENE_MANAGER = SceneManager()
DEBUG = DebugOverlay()
PERF = PerfOverlay()


def _boot_debug_state() -> None:
    debug_enabled = bool(TUNING.DEBUG.debug_enabled)
    if not debug_enabled:
        TUNING.DRIVE.debug_vectors_enabled = False
        TUNING.DRIVE.debug_hitboxes_enabled = False
        TUNING.DRIVE.debug_zones_enabled = False
        TUNING.DRIVE.telemetry_enabled = False
    DEBUG.set_enabled(debug_enabled and TUNING.DEBUG.overlay_default)
    SCENE_MANAGER.state.set_debug_overlay_enabled(DEBUG.enabled)
    PERF.set_enabled(TUNING.DEBUG.perf_overlay_default)


def _update_debug_input() -> None:
    if not SCENE_MANAGER.state.debug_enabled:
        SCENE_MANAGER.state.set_debug_overlay_enabled(False)
        return

    if keyp(4):
        debug_enabled = (
            TUNING.DRIVE.debug_vectors_enabled
            or TUNING.DRIVE.debug_hitboxes_enabled
        )
        new_state = not debug_enabled
        TUNING.DRIVE.debug_vectors_enabled = new_state
        TUNING.DRIVE.debug_hitboxes_enabled = new_state

    DEBUG.handle_input()
    SCENE_MANAGER.state.set_debug_overlay_enabled(DEBUG.enabled)


def _draw_debug_overlay(dt: float) -> None:
    if not SCENE_MANAGER.state.debug_enabled:
        return
    lines = [
        "scene=" + str(SCENE_MANAGER.current_id),
        "dt=" + str(dt),
        "profile=" +
        ("loaded" if SCENE_MANAGER.state.profile_loaded else "new")
    ]
    if SCENE_MANAGER.state.profile_tuning_mismatch:
        lines.append(
            "tuning mismatch: save="
            + str(SCENE_MANAGER.state.profile_tuning_version)
            + " cur="
            + str(TUNING.tuning_version)
        )
    lines.extend(SCENE_MANAGER.state.debug_lines())
    DEBUG.draw(lines)


def BOOT() -> None:
    _boot_debug_state()

    SCENE_MANAGER.state.load_profile()
    SCENE_MANAGER.register(SceneId.DRIVE_PRESET, make_drive_preset_scene)
    SCENE_MANAGER.register(SceneId.GARAGE, make_garage_scene)
    SCENE_MANAGER.register(SceneId.REGION_MAP, make_region_map_scene)
    SCENE_MANAGER.register(SceneId.DRIVE, make_drive_scene)
    SCENE_MANAGER.register(SceneId.POI, make_poi_scene)
    SCENE_MANAGER.register(SceneId.RESULT, make_result_scene)
    SCENE_MANAGER.go(SceneId.DRIVE_PRESET)


def TIC() -> None:
    dt = TUNING.CORE.dt

    PERF.handle_input()
    PERF.begin_frame()

    SCENE_MANAGER.state.clear_debug_lines()
    _update_debug_input()
    SCENE_MANAGER.update(dt)
    SCENE_MANAGER.draw()

    _draw_debug_overlay(dt)

    PERF.end_frame()
    PERF.draw()
