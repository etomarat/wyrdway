from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...data.tuning.pursuers.texts import PURSUER_ENTITY_ERRORS as PURSUER_ENTITY_ERRORS
    from ...data.tuning.pursuers.texts import PURSUER_ENTITY_WORDS as PURSUER_ENTITY_WORDS
    from ...data.tuning.pursuers.texts import PURSUER_PRIME_ERRORS as PURSUER_PRIME_ERRORS
    from ...data.tuning.pursuers.texts import PURSUER_PRIME_WORDS as PURSUER_PRIME_WORDS


class PursuerTextBank:
    __slots__ = ()

    @staticmethod
    def _pick_text(items: list[str], idx: int) -> str:
        n = len(items)
        if n <= 0:
            return ""
        return items[idx % n]

    def code_shard_text(self, idx: int) -> str:
        return self._pick_text(PURSUER_PRIME_WORDS, idx)

    def entity_whisper_text(self, idx: int) -> str:
        return self._pick_text(PURSUER_ENTITY_WORDS, idx)

    def entity_error_text(self, idx: int) -> str:
        return self._pick_text(PURSUER_ENTITY_ERRORS, idx)

    def prime_error_text(self, idx: int) -> str:
        return self._pick_text(PURSUER_PRIME_ERRORS, idx)
