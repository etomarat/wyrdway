from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....contracts import PursuerVariantId
    from ....contracts import PursuerVariantTuning
    from ....data.tuning import TUNING
    from ....data.tuning.pursuers import pursuer_profile_for_variant as pursuer_profile_for_variant
    from .archetypes import EntityPursuerArchetype as EntityPursuerArchetype
    from .archetypes import PrimeEntityPursuerArchetype as PrimeEntityPursuerArchetype
    from .archetypes import PursuerArchetype


def _profile_for_variant(variant: str) -> PursuerVariantTuning:
    profile: PursuerVariantTuning = pursuer_profile_for_variant(variant)
    return profile


def create_pursuer_archetype(variant: str) -> PursuerArchetype:
    profile = _profile_for_variant(variant)
    if variant == PursuerVariantId.PRIME_ENTITY:
        prime_archetype: PursuerArchetype = PrimeEntityPursuerArchetype(profile)
        return prime_archetype
    entity_archetype: PursuerArchetype = EntityPursuerArchetype(profile)
    return entity_archetype


def create_active_pursuer_archetype() -> PursuerArchetype:
    return create_pursuer_archetype(str(TUNING.PURSUER.active_variant))


def active_pursuer_name() -> str:
    return create_active_pursuer_archetype().display_name()
