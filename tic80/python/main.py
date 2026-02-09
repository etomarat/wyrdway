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

    from .contracts import DriveEnterParams
    from .core.debug import DebugOverlay
    from .core.scene_ids import SceneId
    from .core.scene_manager import SceneManager
    from .data.tuning import TUNING
    from .scenes.drive_scene import make_drive_scene
    from .scenes.garage_scene import make_garage_scene
    from .scenes.poi_scene import make_poi_scene
    from .scenes.region_map_scene import make_region_map_scene
    from .scenes.result_scene import make_result_scene

IS_DRIVE_PLAYTEST = True

include("core.palette")
include("contracts")
include("data.tuning.__init__")
include("core.debug")
include("core.input_buttons")
include("core.save_system")
include("core.profile")
include("core.run_state")
include("core.game_state")
include("core.scene_ids")
include("core.scene_manager")
include("core.sprites")
include("systems.fx.fx_ids")
include("systems.fx.fx_manager")
include("systems.fx.fx_registry")
include("systems.fx.vendor.vand_particles")
include("systems.fx.vendor.viza_pslib")
include("systems.fx.vendor.viza_presets")
include("systems.drive.rng")
include("systems.drive.road_model")
include("systems.drive.drive_logic_projection")
include("systems.drive.drive_logic_core")
include("systems.drive.drive_telemetry")
include("systems.drive.drive_objects")
include("systems.drive.drive_zones")
include("systems.drive.drive_input")
include("systems.drive.fx_particles")
include("systems.drive.drive_fx")
include("systems.drive.drive_obstacle_hits")
include("scenes.drive.topdown_road_draw")
include("scenes.drive.topdown_obstacles_draw")
include("scenes.drive.topdown_skid_marks")
include("scenes.drive.topdown_debug_draw")
include("scenes.drive.topdown_fx_overlay")
include("scenes.drive.drive_topdown_renderer")
include("scenes.drive.drive_ui")
include("scenes.drive_scene")
include("scenes.garage_scene")
include("scenes.poi_scene")
include("scenes.region_map_scene")
include("scenes.result_scene")


SCENE_MANAGER = SceneManager()
DEBUG = DebugOverlay()


def BOOT() -> None:
    DEBUG.set_enabled(TUNING.DEBUG.overlay_default)
    if IS_DRIVE_PLAYTEST:
        DEBUG.set_enabled(False)
        SCENE_MANAGER.state.profile.reset()
        SCENE_MANAGER.state.end_run()
        SCENE_MANAGER.state.playtest_begin()
        SCENE_MANAGER.register(SceneId.DRIVE, make_drive_scene)
        SCENE_MANAGER.register(SceneId.RESULT, make_result_scene)
        # В плейтесте нам нужен “замкнутый” цикл DRIVE<->RESULT без POI/гаража.
        # Режим оставляем "travel" (без расширения Literal), а логику развилки держим
        # в DriveScene через state.playtest_enabled.
        SCENE_MANAGER.go("DRIVE", DriveEnterParams("travel", "topdown"))
        return

    SCENE_MANAGER.state.load_profile()
    SCENE_MANAGER.register(SceneId.GARAGE, make_garage_scene)
    SCENE_MANAGER.register(SceneId.REGION_MAP, make_region_map_scene)
    SCENE_MANAGER.register(SceneId.DRIVE, make_drive_scene)
    SCENE_MANAGER.register(SceneId.POI, make_poi_scene)
    SCENE_MANAGER.register(SceneId.RESULT, make_result_scene)
    SCENE_MANAGER.go(SceneId.GARAGE)


def TIC() -> None:
    dt = TUNING.CORE.dt

    SCENE_MANAGER.state.clear_debug_lines()
    if not IS_DRIVE_PLAYTEST:
        DEBUG.handle_input()
    SCENE_MANAGER.update(dt)
    SCENE_MANAGER.draw()

    if not IS_DRIVE_PLAYTEST:
        lines = [
            "scene=" + str(SCENE_MANAGER.current_id),
            "dt=" + str(dt),
            "profile=" + ("loaded" if SCENE_MANAGER.state.profile_loaded else "new")
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
