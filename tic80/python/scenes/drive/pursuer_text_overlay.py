from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import print

    from ...contracts import PursuerVariantId
    from ...core.palette import Color
    from ...core.text_layout import text_right_x
    from ...systems.drive.rng import lcg_next_u32
    from .pursuer_text_bank import PursuerTextBank


class PursuerTextOverlay:
    __slots__ = (
        "_text_bank",
        "_error_text",
        "_error_t",
        "_error_color",
        "_error_seed"
    )

    def __init__(self, text_bank: PursuerTextBank) -> None:
        self._text_bank = text_bank
        self._error_text = ""
        self._error_t = 0.0
        self._error_color = Color.RED
        self._error_seed = 0x13579BDF

    @staticmethod
    def _lcg(seed: int) -> int:
        return lcg_next_u32(seed)

    def update(self, dt: float) -> None:
        if self._error_t <= 0.0:
            return
        self._error_t -= dt
        if self._error_t <= 0.0:
            self._error_t = 0.0
            self._error_text = ""

    def queue_error_text(self, variant_id: str, anim_t: float) -> None:
        seed = self._error_seed ^ int(anim_t * 1000.0)
        seed = self._lcg(seed)
        self._error_seed = seed
        if variant_id == PursuerVariantId.ENTITY:
            self._error_text = self._text_bank.entity_error_text(seed)
            self._error_color = Color.ORANGE
        else:
            self._error_text = self._text_bank.prime_error_text(seed)
            self._error_color = Color.RED
        self._error_t = 0.55

    def draw(self, screen_glitch_active: bool) -> None:
        if not screen_glitch_active:
            return
        if self._error_t <= 0.0:
            return
        txt = self._error_text
        if txt == "":
            return
        tx = text_right_x(txt, 239 - 4, 6, 0)
        ty = 136 - 4 - 6
        print(txt, tx, ty, self._error_color, True, 1, False)
