from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import include

    from ....contracts import PursuerVariantId
    from ....contracts import PursuerVariantTuning
    from .texts import PURSUER_ENTITY_ERRORS as PURSUER_ENTITY_ERRORS
    from .texts import PURSUER_ENTITY_WORDS as PURSUER_ENTITY_WORDS
    from .texts import PURSUER_PRIME_ERRORS as PURSUER_PRIME_ERRORS
    from .texts import PURSUER_PRIME_WORDS as PURSUER_PRIME_WORDS
    from .entity import ENTITY_PURSUER_PROFILE as ENTITY_PURSUER_PROFILE
    from .prime_entity import PRIME_ENTITY_PURSUER_PROFILE as PRIME_ENTITY_PURSUER_PROFILE


include("data.tuning.pursuers.texts")
include("data.tuning.pursuers.entity")
include("data.tuning.pursuers.prime_entity")


def _base_pursuer_profile_for_variant(variant: str) -> PursuerVariantTuning:
    if variant == PursuerVariantId.PRIME_ENTITY:
        return PRIME_ENTITY_PURSUER_PROFILE
    return ENTITY_PURSUER_PROFILE


def clone_pursuer_profile(profile: PursuerVariantTuning) -> PursuerVariantTuning:
    clone = PursuerVariantTuning()
    fields = list(PursuerVariantTuning.__slots__)
    i = 0
    while i < len(fields):
        name = fields[i]
        setattr(clone, name, getattr(profile, name))
        i += 1
    return clone


def pursuer_profile_for_variant(variant: str) -> PursuerVariantTuning:
    base = _base_pursuer_profile_for_variant(variant)
    return clone_pursuer_profile(base)
