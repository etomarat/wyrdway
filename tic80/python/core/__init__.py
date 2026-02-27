from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import include


include("core.debug")
include("core.version")
include("core.rich_tokens")
include("core.text_layout")
include("core.poi_text")
include("core.ui.__init__")
include("core.input_buttons")
include("core.controls.__init__")
include("core.perf_overlay")
include("core.save_system")
include("core.profile")
include("core.route_planner")
include("core.run_state.__init__")
include("core.game_state")
include("core.scene_ids")
include("core.scene_manager")
