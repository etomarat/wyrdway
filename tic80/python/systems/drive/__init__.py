from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import include


include("systems.drive.rng")
include("systems.drive.road_model")
include("systems.drive.drive_logic_projection")
include("systems.drive.drive_logic_state")
include("systems.drive.drive_logic_accessors")
include("systems.drive.drive_logic_utils")
include("systems.drive.drive_logic_controls")
include("systems.drive.drive_logic_lateral")
include("systems.drive.drive_logic_post_step")
include("systems.drive.drive_logic_core")
include("systems.drive.drive_telemetry")
include("systems.drive.drive_objects")
include("systems.drive.drive_zones")
include("systems.drive.drive_input")
include("systems.drive.drive_zone_effects")
include("systems.drive.drive_debug_lines")
include("systems.drive.pursuer_chase")
include("systems.drive.fx_particles")
include("systems.drive.drive_fx_factories")
include("systems.drive.drive_fx")
include("systems.drive.drive_obstacle_hits")
include("systems.drive.drive_screen_shake")
