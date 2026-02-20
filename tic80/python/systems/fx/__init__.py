from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import include


include("systems.fx.fx_ids")
include("systems.fx.fx_manager")
include("systems.fx.fx_registry")
include("systems.fx.vendor.__init__")
