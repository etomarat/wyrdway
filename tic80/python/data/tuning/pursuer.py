from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...contracts import PursuerVariantId
    from ...data.tuning import TUNING


# PURSUER
#
# Варианты:
# - entity: базовая "малая" сущность (дефолт)
# - prime_entity: усиленная финальная версия

# Главный флаг системы погони.
TUNING.PURSUER.enabled = True

# Grace-фаза: преследователь не давит сразу.
# Grace заканчивается, когда сработал ЛЮБОЙ порог:
# - проехали grace_meters
# - или прошло grace_seconds_cap
TUNING.PURSUER.grace_meters = 20.0
TUNING.PURSUER.grace_seconds_cap = 4.0

# Текущий активный вариант ("entity" или "prime_entity").
TUNING.PURSUER.active_variant = PursuerVariantId.ENTITY
