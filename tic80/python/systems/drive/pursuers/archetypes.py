from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....contracts import PursuerVariantId
    from ....contracts import PursuerVariantIdValue
    from ....contracts import PursuerVariantTuning
    from ..pursuer_chase import PursuerState
    from ....scenes.drive.drive_topdown_renderer import DriveTopdownRenderer


class PursuerArchetype:
    __slots__ = ("variant_id", "profile")

    def __init__(self, variant_id: PursuerVariantIdValue, profile: PursuerVariantTuning) -> None:
        self.variant_id: PursuerVariantIdValue = variant_id
        self.profile = profile

    def display_name(self) -> str:
        return self.profile.name

    def draw_body(
        self,
        renderer: DriveTopdownRenderer,
        px: int,
        py: int,
        pursuer_state: PursuerState,
        seed_base: int,
        road_half_px: float
    ) -> None:
        renderer.draw_glitch_pursuer_body(
            px,
            py,
            pursuer_state,
            seed_base,
            road_half_px,
            self.profile
        )

    def draw_strike(
        self,
        renderer: DriveTopdownRenderer,
        px: int,
        py: int,
        tx: int,
        ty: int,
        flash_n: float,
        seed_base: int
    ) -> None:
        renderer.draw_glitch_pursuer_strike(
            px,
            py,
            tx,
            ty,
            flash_n,
            seed_base
        )


class EntityPursuerArchetype(PursuerArchetype):
    __slots__ = ()

    def __init__(self, profile: PursuerVariantTuning) -> None:
        PursuerArchetype.__init__(self, PursuerVariantId.ENTITY, profile)

    def draw_body(
        self,
        renderer: DriveTopdownRenderer,
        px: int,
        py: int,
        pursuer_state: PursuerState,
        seed_base: int,
        road_half_px: float
    ) -> None:
        renderer.draw_entity_pursuer_body(
            px,
            py,
            pursuer_state,
            seed_base,
            self.profile
        )

    def draw_strike(
        self,
        renderer: DriveTopdownRenderer,
        px: int,
        py: int,
        tx: int,
        ty: int,
        flash_n: float,
        seed_base: int
    ) -> None:
        renderer.draw_entity_pursuer_strike(
            px,
            py,
            tx,
            ty,
            flash_n,
            seed_base
        )


class PrimeEntityPursuerArchetype(PursuerArchetype):
    __slots__ = ()

    def __init__(self, profile: PursuerVariantTuning) -> None:
        PursuerArchetype.__init__(self, PursuerVariantId.PRIME_ENTITY, profile)

    def draw_body(
        self,
        renderer: DriveTopdownRenderer,
        px: int,
        py: int,
        pursuer_state: PursuerState,
        seed_base: int,
        road_half_px: float
    ) -> None:
        renderer.draw_prime_pursuer_body(
            px,
            py,
            pursuer_state,
            seed_base,
            road_half_px,
            self.profile
        )
