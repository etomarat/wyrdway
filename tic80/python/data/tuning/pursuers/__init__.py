from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import include

    from ....contracts import PursuerVariantId
    from ....contracts import PursuerVariantTuning
    from .entity import ENTITY_PURSUER_PROFILE as ENTITY_PURSUER_PROFILE
    from .prime_entity import PRIME_ENTITY_PURSUER_PROFILE as PRIME_ENTITY_PURSUER_PROFILE


include("data.tuning.pursuers.entity")
include("data.tuning.pursuers.prime_entity")


def pursuer_profile_for_variant(variant: str) -> PursuerVariantTuning:
    if variant == PursuerVariantId.PRIME_ENTITY:
        return PRIME_ENTITY_PURSUER_PROFILE
    return ENTITY_PURSUER_PROFILE
