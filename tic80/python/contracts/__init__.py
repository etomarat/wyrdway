from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import include

    from .scene import (
        DriveMode as DriveMode,
        DriveVariant as DriveVariant,
        DriveEnterParams as DriveEnterParams,
        ResultEnterParams as ResultEnterParams,
        SceneEnterParams as SceneEnterParams,
        Scene as Scene,
        SceneKeyNoParams as SceneKeyNoParams,
        SceneKeyDrive as SceneKeyDrive,
        SceneKeyResult as SceneKeyResult,
        SceneNavigator as SceneNavigator,
        SceneFactory as SceneFactory
    )
    from .tuning import (
        CoreTuning as CoreTuning,
        DebugTuning as DebugTuning,
        ProfileTuning as ProfileTuning,
        DriveTuning as DriveTuning,
        PoiTuning as PoiTuning,
        PursuerVariantId as PursuerVariantId,
        PursuerVariantTuning as PursuerVariantTuning,
        PursuerTuning as PursuerTuning,
        Tuning as Tuning
    )


include("contracts.tuning")
include("contracts.scene")
