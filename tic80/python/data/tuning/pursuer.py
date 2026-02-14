from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...data.tuning import TUNING


# PURSUER (m1.8)
#
# Единицы:
# - расстояния/скорости в road-space units (те же, что у road_s / max_speed)
# - время в секундах
#
# Все ручки можно отключать:
# - enabled=False выключает механику целиком
# - offroad_catchup=0 выключает бонус догоняния за оффроад
# - boost_pushback_s=0 выключает отталкивание от бустеров
# - strike_min_speed=0 отключает порог минимальной скорости для укуса

# Главный флаг системы погони.
TUNING.PURSUER.enabled = True

# Grace-фаза: преследователь не давит сразу.
# Grace заканчивается, когда сработал ЛЮБОЙ порог:
# - проехали grace_meters
# - или прошло grace_seconds_cap
TUNING.PURSUER.grace_meters = 40.0
TUNING.PURSUER.grace_seconds_cap = 4.0

# Базовое отставание преследователя от машины в момент старта погони.
# Во время grace удерживаем этот gap стабильным, чтобы не было "рывка" дистанции.
TUNING.PURSUER.start_gap_s = 150.0

# Скорость преследователя:
# pursuer_speed = base_speed + slow_factor*slow_catchup + offroad_bonus
# где slow_factor = clamp(1 - speed/max_speed, 0..1)
#
# Примеры при max_speed=100:
# - speed=120: slow_factor=0.0 -> pursuer_speed=base_speed
# - speed=100: slow_factor=0.0 -> pursuer_speed=base_speed
# - speed=60:  slow_factor=0.4 -> pursuer_speed=base_speed + 0.4*slow_catchup
# - speed=0:   slow_factor=1.0 -> pursuer_speed=base_speed + slow_catchup
#
# Базовый смысл:
# - base_speed — "крейсерская" скорость погони;
# - slow_catchup — добавка, насколько сильнее догоняет при медленной езде игрока;
# - offroad_catchup — дополнительная прибавка, если игрок ушёл в оффроад.
TUNING.PURSUER.base_speed = 88.0
TUNING.PURSUER.slow_catchup = 24.0
TUNING.PURSUER.offroad_catchup = 8.0

# Пороги состояний:
# - FAR:   d > show_dist_s
# - CHASE: near_dist_s < d <= show_dist_s
# - NEAR:  d <= near_dist_s
#
# Бар HUD строится по диапазону [near..show], поэтому увеличение show делает
# нарастание более "плавным" и заметным заранее.
TUNING.PURSUER.show_dist_s = 210.0
TUNING.PURSUER.near_dist_s = 70.0

# Strike:
# - cooldown между укусами
# - сколько ресурсов снимаем за удар
# - окно вокруг центра дороги для детектора "пересёк ось"
TUNING.PURSUER.strike_cooldown_sec = 1.35
TUNING.PURSUER.strike_drain_amount = 2
TUNING.PURSUER.center_window_d = 6.0
# Защита от ложных укусов: пересечение центра считаем валидным только если
# хотя бы одна из точек (prev/curr) вышла на заметную амплитуду по |road_d|.
TUNING.PURSUER.center_cross_min_abs_d = 0.4

# Если True: в NEAR после latch укус может сработать просто по cooldown
# (без обязательного пересечения центра). Нужен как "страховка", чтобы укус
# не пропадал на прямой или при ровной езде.
TUNING.PURSUER.strike_auto_when_latched = True

# Минимальная скорость машины для срабатывания укуса.
# 0 = укусы возможны даже при почти нулевой скорости (более агрессивная погоня).
TUNING.PURSUER.strike_min_speed = 0.0

# После первой догонялки преследователь "липнет" к машине:
# - держим минимум на follow_gap_s позади,
# - при отставании догоняем с latched_follow_speed.
# Формула latched_follow_speed:
#   speed * latched_follow_speed_mult + latched_follow_speed_add
#
# Примеры:
# - при speed=60:  60*0.84 + 4 = 54.4
# - при speed=100: 100*0.84 + 4 = 88
# - при speed=120: 120*0.84 + 4 = 104.8
#
# То есть преследователь не обгоняет, но игрок может "вывозить" дистанцию
# длительной быстрой и ровной ездой.
TUNING.PURSUER.follow_gap_s = 16.0
# Порог выхода из latch: если дистанция выросла выше этого значения, считаем,
# что игрок оторвался и возвращаемся в обычный режим догонялки.
TUNING.PURSUER.latch_release_dist_s = 95.0
TUNING.PURSUER.latched_follow_speed_mult = 0.84
TUNING.PURSUER.latched_follow_speed_add = 4.0

# Насколько дорожный бустер отталкивает преследователя назад по s.
TUNING.PURSUER.boost_pushback_s = 22.0

# Визуальные множители.
# strike_shake_intensity прокидывается как "impact" в общий shake-hit канал.
# Важно: в shake используется квадратичная кривая trauma^2, поэтому маленькие
# значения почти незаметны. Для укуса держим impact выше "обычного удара".
TUNING.PURSUER.strike_shake_intensity = 12.0
TUNING.PURSUER.near_vignette = 0.25
TUNING.PURSUER.near_noise = 0.35
TUNING.PURSUER.strike_flash_seconds = 0.22
