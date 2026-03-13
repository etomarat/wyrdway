from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...tuning import TUNING

# Визуализация векторов (для тюнинга управления).
#
# Рисуем из центра машины:
# - направление (heading),
# - скорость (velocity),
# - боковое ускорение (side accel) — насколько сильно “трение” гасит занос.
TUNING.DRIVE.debug_vectors_enabled = False
TUNING.DRIVE.debug_vectors_heading_len = 20.0
TUNING.DRIVE.debug_vectors_vel_scale = 0.35
TUNING.DRIVE.debug_vectors_accel_scale = 0.2

# Визуализация хитбоксов машины (для настройки коллизий).
TUNING.DRIVE.debug_hitboxes_enabled = False

# Телеметрия DRIVE (для отладки управления).
#
# Идея: мы пишем сэмплы не каждый кадр (чтобы не спамить консоль), а раз в N кадров,
# плюс отмечаем “события” (например, выезд на оффроуд).
# Лог печатается в консоль (через `trace`) при выходе из DRIVE (finish/evac).
TUNING.DRIVE.telemetry_enabled = False
TUNING.DRIVE.telemetry_every_frames = 20
TUNING.DRIVE.telemetry_max_lines = 140
