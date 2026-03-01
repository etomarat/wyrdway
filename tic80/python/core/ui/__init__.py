from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import include


include("core.ui.rich_text")
include("core.ui.overlay_layout")
include("core.ui.overlay_modal")
include("core.ui.overlay_footer")
include("core.ui.panel")
include("core.ui.text")
include("core.ui.meter")
include("core.ui.prompts")
