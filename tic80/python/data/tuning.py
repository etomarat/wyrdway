from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..contracts import Tuning

TUNING: Tuning = Tuning()
# Поднимай версию при изменениях баланса (числа в TUNING).
TUNING.tuning_version = 3

# Fixed timestep in seconds (TIC-80 runs at 60 FPS by default).
TUNING.CORE.dt = 1 / 60

# Initial debug overlay state on boot.
TUNING.DEBUG.overlay_default = True

TUNING.PROFILE.start_scrap = 0
TUNING.PROFILE.start_garage_hp = 100.0
TUNING.PROFILE.start_garage_fuel = 50.0
TUNING.PROFILE.repair_cost = 10
TUNING.PROFILE.repair_hp = 20.0
TUNING.PROFILE.evac_fuel_pct = 0.1
TUNING.PROFILE.evac_fuel_min = 5.0
TUNING.PROFILE.evac_scrap_loss = 5

# DRIVE (m1.5)
#
# Базовые единицы:
# - `dt` — секунды (см. CORE.dt)
# - `s` — прогресс по дороге в условных "метрах" (road-space)
# - `d` — смещение в сторону в тех же единицах, что и `road_width`
# - `speed` — "метры в секунду" в road-space

# Длина сегмента (условные метры road-space). Увеличение делает DRIVE длиннее.
TUNING.DRIVE.segment_total_length = 600.0

# Safe start: первые метры почти прямые (без серьёзных поворотов и будущих спавнов).
TUNING.DRIVE.safe_start_length = 40.0

# Ширина дороги (константа на m1.5). Увеличение даёт больше места для манёвра.
TUNING.DRIVE.road_width = 40.0

# Шаг дискретизации профиля дороги (curvature samples).
# Меньше = плавнее и "дороже" по памяти/CPU.
# Пример: ds=1.0 -> 200 сэмплов на 200 метров; ds=4.0 -> 50 сэмплов.
TUNING.DRIVE.ds = 2.0

# Длины кусков дороги (сколько держится одна "цель" кривизны).
# Увеличение max_piece_length делает дорогу более "длинноволновой".
TUNING.DRIVE.min_piece_length = 30.0
TUNING.DRIVE.max_piece_length = 80.0

# Максимальная кривизна дороги (ограничение "невозможных" поворотов).
# Чем больше, тем резче повороты.
TUNING.DRIVE.max_curvature = 0.03

# Доля куска, которая уходит на плавный вход/выход в поворот.
# 0.1 = почти ступеньки, 0.5 = очень плавно.
TUNING.DRIVE.ramp_fraction = 0.3

# Управление/физика (arcade)

# Максимальная скорость (road-space units/sec).
TUNING.DRIVE.max_speed = 60.0

# Разгон при газе (units/sec^2).
TUNING.DRIVE.accel = 80.0

# Торможение (units/sec^2). Должно быть заметно сильнее, чем accel, если хотим
# "аркадный" контроль.
TUNING.DRIVE.brake = 120.0

# Скорость изменения бокового смещения от руля (чем больше, тем резче рулёжка).
TUNING.DRIVE.steer_rate = 25.0

# "Сцепление" как множитель. Меньше = сильнее занос (больше d при том же рулении).
TUNING.DRIVE.grip = 1.0

# Мультипликатор сцепления при ручнике (`B`): меньше = более "дрифтово".
TUNING.DRIVE.handbrake_grip_mult = 0.4

# Мультипликатор сцепления на оффроуде.
TUNING.DRIVE.offroad_grip_mult = 0.6

# Замедление скорости на оффроуде (скорость *= 1 - offroad_slowdown*dt).
TUNING.DRIVE.offroad_slowdown = 1.5

# “Вынос” на поворотах: насколько сильно кривизна дороги будет сдвигать `d`,
# если не рулить. Чем больше, тем меньше “автопилота” и тем чаще нужно
# подруливать в поворотах.
TUNING.DRIVE.curve_drift_mult = -10.0

# Ресурсы

# Расход топлива в простое (units/sec).
TUNING.DRIVE.fuel_per_sec_idle = 0.2

# Доп. расход топлива при газе (units/sec).
TUNING.DRIVE.fuel_per_sec_throttle = 1.0

# Объекты на дороге (m1.5)
#
# Плотности задаются "на 100 метров": 1.0 означает "в среднем 1 объект на 100м".
# Количество на сегмент берём примерно как: (total_length / 100) * density.
#
# Важно: объекты сейчас спавнятся детерминированно по seed и учитывают safe start.

# Средняя плотность препятствий.
TUNING.DRIVE.obstacles_per_100m = 2.0

# Средняя плотность опасных зон.
TUNING.DRIVE.zones_per_100m = 1.0

# Минимальная дистанция между объектами (по s).
TUNING.DRIVE.spawn_min_distance_between = 25.0

# Отступ от краёв дороги, чтобы не спавнить объекты вплотную к обочине.
TUNING.DRIVE.spawn_min_distance_from_edges = 6.0

# Радиус препятствия (в road-space единицах).
TUNING.DRIVE.obstacle_radius = 3.0

# Радиус опасной зоны (по d). Чем больше, тем шире зона на дороге.
TUNING.DRIVE.zone_radius = 6.0

# Длина опасной зоны по s.
TUNING.DRIVE.zone_length = 40.0

TUNING.POI.timer_seconds = 10.0
TUNING.POI.scrap_per_loot = 5
