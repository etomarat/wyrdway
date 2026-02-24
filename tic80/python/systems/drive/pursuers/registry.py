from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....contracts import PursuerVariantId
    from ....contracts import PursuerVariantIdValue
    from ....contracts import PursuerVariantTuning
    from ....data.tuning import TUNING
    from ....data.tuning.pursuers import pursuer_profile_for_variant as pursuer_profile_for_variant
    from .archetypes import EntityPursuerArchetype as EntityPursuerArchetype
    from .archetypes import PrimeEntityPursuerArchetype as PrimeEntityPursuerArchetype
    from .archetypes import PursuerArchetype


def _create_entity_archetype(profile: PursuerVariantTuning) -> PursuerArchetype:
    archetype: PursuerArchetype = EntityPursuerArchetype(profile)
    return archetype


def _create_prime_entity_archetype(profile: PursuerVariantTuning) -> PursuerArchetype:
    archetype: PursuerArchetype = PrimeEntityPursuerArchetype(profile)
    return archetype


_ARCHETYPE_FACTORIES = {
    PursuerVariantId.ENTITY: _create_entity_archetype,
    PursuerVariantId.PRIME_ENTITY: _create_prime_entity_archetype
}


def _create_for_variant(
    variant: PursuerVariantIdValue,
    profile: PursuerVariantTuning
) -> PursuerArchetype:
    factory = _ARCHETYPE_FACTORIES.get(variant)
    if factory is None:
        factory = _ARCHETYPE_FACTORIES[PursuerVariantId.ENTITY]
    archetype: PursuerArchetype = factory(profile)
    return archetype


def create_pursuer_archetype(variant: PursuerVariantIdValue) -> PursuerArchetype:
    profile = pursuer_profile_for_variant(variant)
    return _create_for_variant(variant, profile)


def create_active_pursuer_archetype() -> PursuerArchetype:
    return create_pursuer_archetype(TUNING.PURSUER.active_variant)


def active_pursuer_name() -> str:
    return create_active_pursuer_archetype().display_name()


def active_pursuer_name_color() -> int:
    return int(create_active_pursuer_archetype().profile.name_color)
