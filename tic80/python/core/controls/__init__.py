from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import include


include("core.controls.modes")
include("core.controls.actions")
include("core.controls.bindings")
include("core.controls.prompts")

