from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import include

    from ...contracts import Tuning


TUNING: Tuning = Tuning()
# Поднимай версию при изменениях баланса (числа в TUNING).
TUNING.tuning_version = 16

include("data.tuning.core")
include("data.tuning.profile")
include("data.tuning.poi")
include("data.tuning.pursuer")
include("data.tuning.debug")
include("data.tuning.drive.physics")
include("data.tuning.drive.track")
include("data.tuning.drive.visual")
include("data.tuning.drive.fx")
include("data.tuning.drive.objects")
include("data.tuning.drive.debug")
