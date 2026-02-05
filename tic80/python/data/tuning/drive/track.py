from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...tuning import TUNING

# Длина сегмента (условные метры road-space). Увеличение делает DRIVE длиннее.
TUNING.DRIVE.segment_total_length = 2000.0

# Safe start: первые метры почти прямые (без серьёзных поворотов и будущих спавнов).
TUNING.DRIVE.safe_start_length = 120.0

# Ширина дороги (константа на m1.5). Увеличение даёт больше места для манёвра.
TUNING.DRIVE.road_width = 60.0

# Шаг дискретизации профиля дороги (curvature samples).
# Меньше = плавнее и "дороже" по памяти/CPU.
# Пример: ds=1.0 -> 200 сэмплов на 200 метров; ds=4.0 -> 50 сэмплов.
TUNING.DRIVE.ds = 5.0

# Длины кусков дороги (сколько держится одна "цель" кривизны).
# Увеличение max_piece_length делает дорогу более "длинноволновой".
TUNING.DRIVE.min_piece_length = 40.0
TUNING.DRIVE.max_piece_length = 220.0

# Максимальная кривизна дороги (ограничение "невозможных" поворотов).
# Чем больше, тем резче повороты.
TUNING.DRIVE.max_curvature = 0.019

# Доля "прямых" кусков (когда target curvature близка к 0).
#
# Зачем: иначе дорога получается “вечно поворачивающей”, потому что target
# кривизна выбирается равномерно из [-max_curvature..+max_curvature].
#
# Реализация:
# - с вероятностью `straight_piece_chance` выбираем target из маленького диапазона
#   [-straight_max_curvature..+straight_max_curvature]
# - иначе выбираем target из полного диапазона.
TUNING.DRIVE.straight_piece_chance = 0.35
TUNING.DRIVE.straight_max_curvature = 0.002

# Доля куска, которая уходит на плавный вход/выход в поворот.
# 0.1 = почти ступеньки, 0.5 = очень плавно.
TUNING.DRIVE.ramp_fraction = 0.4
