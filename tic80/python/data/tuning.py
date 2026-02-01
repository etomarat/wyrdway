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
TUNING.PROFILE.start_garage_fuel = 100.0
TUNING.PROFILE.repair_cost = 10
TUNING.PROFILE.repair_hp = 20.0
TUNING.PROFILE.evac_fuel_pct = 0.1
TUNING.PROFILE.evac_fuel_min = 5.0
TUNING.PROFILE.evac_scrap_loss = 5

# DRIVE (m1.5)
#
# Важно: текущая модель DRIVE — world-space.
#
# Базовые единицы:
# - `dt` — секунды (см. CORE.dt)
# - `(x, y)` — позиция машины в мире (условные “метры”)
# - `(fwd_x, fwd_y)` — направление машины как unit-вектор
# - `(vx, vy)` — скорость как вектор (может быть не сонаправлена направлению => занос)
#
# “Дорога” всё ещё живёт в road-space (s, d) и используется как ориентир:
# - `road_s` — прогресс по centerline (для “финиша” и режима extract)
# - `road_d` — смещение относительно центра (для оффроуда/штрафов)

# Длина сегмента (условные метры road-space). Увеличение делает DRIVE длиннее.
TUNING.DRIVE.segment_total_length = 2000.0

# Safe start: первые метры почти прямые (без серьёзных поворотов и будущих спавнов).
TUNING.DRIVE.safe_start_length = 40.0

# Ширина дороги (константа на m1.5). Увеличение даёт больше места для манёвра.
TUNING.DRIVE.road_width = 60.0

# Шаг дискретизации профиля дороги (curvature samples).
# Меньше = плавнее и "дороже" по памяти/CPU.
# Пример: ds=1.0 -> 200 сэмплов на 200 метров; ds=4.0 -> 50 сэмплов.
TUNING.DRIVE.ds = 4.0

# Длины кусков дороги (сколько держится одна "цель" кривизны).
# Увеличение max_piece_length делает дорогу более "длинноволновой".
TUNING.DRIVE.min_piece_length = 30.0
TUNING.DRIVE.max_piece_length = 160.0

# Максимальная кривизна дороги (ограничение "невозможных" поворотов).
# Чем больше, тем резче повороты.
TUNING.DRIVE.max_curvature = 0.02

# Доля куска, которая уходит на плавный вход/выход в поворот.
# 0.1 = почти ступеньки, 0.5 = очень плавно.
TUNING.DRIVE.ramp_fraction = 0.4

# Управление/физика (arcade)

# Максимальная скорость (road-space units/sec).
TUNING.DRIVE.max_speed = 80.0

# Максимальная скорость заднего хода.
TUNING.DRIVE.max_reverse_speed = 18.0

# Разгон при газе (units/sec^2).
TUNING.DRIVE.accel = 30.0

# Торможение (units/sec^2). Должно быть заметно сильнее, чем accel, если хотим
# "аркадный" контроль.
TUNING.DRIVE.brake = 120.0

# Замедление при отпускании газа: как быстро скорость стремится к 0.
TUNING.DRIVE.coast_decel = 25.0

# Скорость поворота направления машины (радианы/сек).
# Больше = резче рулёжка, легче держать повороты.
TUNING.DRIVE.steer_rate = 1.2

# "Сцепление" как множитель. Меньше = сильнее занос (больше d при том же рулении).
# В формуле это часть `effective_grip`:
#   side_damp = 1 - side_friction * effective_grip * dt
# Где `effective_grip` стартует с `grip` и модифицируется ручником/оффроудом.
TUNING.DRIVE.grip = 2.0

# Боковое трение: чем больше, тем быстрее “гасится” боковая скорость (меньше заноса).
# Это второй множитель в той же формуле (см. `grip` выше).
TUNING.DRIVE.side_friction = 6.0

# Насколько “сильнее занос” на высокой скорости.
#
# Реализация в коде делает боковое трение слабее с ростом скорости:
#   slip = 1 + side_slip_speed_mult * speed_factor
#   side_damp = 1 - (side_friction * effective_grip * dt) / slip
#
# То есть:
# - 0.0: занос не зависит от скорости
# - больше: на высокой скорости боковую скорость гасит заметно хуже (сложнее, но “тяжелее”)
TUNING.DRIVE.side_slip_speed_mult = 3.0

# Мультипликатор сцепления при ручнике (`B`): меньше = более "дрифтово".
TUNING.DRIVE.handbrake_grip_mult = 0.4

# Мультипликатор сцепления на оффроуде.
TUNING.DRIVE.offroad_grip_mult = 2

# Замедление скорости на оффроуде (скорость *= 1 - offroad_slowdown*dt).
# Не связано напрямую с `coast_decel`:
# - `coast_decel` — как быстро гасим продольную скорость, когда отпускаем газ;
# - `offroad_slowdown` — дополнительный “drag” на всем векторе скорости, если вне дороги.
TUNING.DRIVE.offroad_slowdown = 1.5

# Ресурсы

# Расход топлива в простое (units/sec).
TUNING.DRIVE.fuel_per_sec_idle = 0.1

# Доп. расход топлива при газе (units/sec).
TUNING.DRIVE.fuel_per_sec_throttle = 1.0

# Top-down рендер: окно видимости дороги (в road-space "метрах" по s).
# Если дорога “обрывается” сзади/спереди — увеличивай эти значения.
TUNING.DRIVE.render_back_s = 180.0
TUNING.DRIVE.render_forward_s = 200.0

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
