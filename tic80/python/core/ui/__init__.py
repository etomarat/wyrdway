from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import include


include("core.ui.rich_text")
include("core.ui.panel")
include("core.ui.modal")
include("core.ui.text")
include("core.ui.meter")
include("core.ui.prompts")
