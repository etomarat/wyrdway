from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..contracts import Tuning

TUNING: Tuning = Tuning()
# Поднимай версию при изменениях баланса (числа в TUNING).
TUNING.tuning_version = 9

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
TUNING.DRIVE.max_curvature = 0.02

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

# Управление/физика (arcade)

# max_speed — опорная скорость (road-space units/sec) для "кривых" управления.
#
# Важно: это НЕ "жёсткая максималка". Мы используем max_speed как нормализацию
# (speed_factor = speed / max_speed) для:
# - ослабления руления на скорости,
# - усиления заноса на скорости (side_slip_speed_mult),
# - порогов ручника и т.п.
#
# Жёсткий предохранитель скорости задаётся отдельно: `speed_cap`.
TUNING.DRIVE.max_speed = 100.0

# speed_cap — жёсткий предохранитель v_forward (чтобы симуляция не улетала).
#
# При наличии drag (drag_lin/drag_quad) фактическая "максималка" получается
# естественно: газ добавляет ускорение, drag его компенсирует и скорость выходит
# на плато.
#
# Пример оценки плато (без учета заноса и без клипа speed_cap):
# - при постоянном газе у нас v_fwd растёт примерно на `accel`,
# - drag тянет скорость вниз как: a_drag ≈ (drag_lin + drag_quad*|v|) * v
# - равновесие примерно при accel ≈ (drag_lin + drag_quad*v) * v
#   => drag_quad*v^2 + drag_lin*v - accel ≈ 0
#
# Если хочется, чтобы после 100 скорость росла дальше, но очень медленно:
# - держи max_speed=100 (чтобы управление осталось как настроено),
# - подними speed_cap (например 120..140),
# - и подбери drag_quad так, чтобы равновесие было чуть выше 100.
TUNING.DRIVE.speed_cap = 130.0

# Максимальная скорость заднего хода.
TUNING.DRIVE.max_reverse_speed = 18.0

# Разгон при газе (units/sec^2).
TUNING.DRIVE.accel = 40.0

# Торможение (units/sec^2). Должно быть заметно сильнее, чем accel, если хотим
# "аркадный" контроль.
TUNING.DRIVE.brake = 120.0

# Замедление при отпускании газа: как быстро скорость стремится к 0.
TUNING.DRIVE.coast_decel = 25.0

# Скорость поворота направления машины (радианы/сек).
# Больше = резче рулёжка, легче держать повороты.
TUNING.DRIVE.steer_rate = 1.3

# Как рулёжка зависит от скорости.
#
# Сейчас мы используем множитель `steer_scale`, который меняется от скорости:
# - на маленькой скорости руление сильнее (проще объезжать препятствия),
# - на высокой руление слабее (меньше “нервных” разворотов).
#
# Формула:
#   t = clamp(speed / max_speed, 0..1)
#   steer_scale = lerp(steer_scale_max, steer_scale_min, t)
#
# Порог: если speed < steer_min_speed, поворот выключен (не крутимся на месте).
TUNING.DRIVE.steer_scale_max = 1.0
TUNING.DRIVE.steer_scale_min = 0.55
TUNING.DRIVE.steer_min_speed = 0.6

# Мультипликатор поворота в заднем ходе (обычно хуже, чем вперёд).
TUNING.DRIVE.steer_reverse_mult = 0.7

# Ручник: “тормоз в занос”.
#
# Важно: если ручник только снижает сцепление (grip_mult), но не снижает скорость,
# он ощущается бесполезным: на высокой скорости нас и так несёт, а ручник лишь
# усугубляет занос.
#
# Поэтому ручник в m1.5:
# - снижает сцепление (см. handbrake_grip_mult),
# - добавляет замедление вперёд/назад (handbrake_decel),
# - и чуть усиливает руление (handbrake_steer_mult), чтобы “довернуть” в заносе.
#
# Замедление делаем зависимым от скорости через speed_factor (0..1):
#   amount = handbrake_decel * max(speed_factor, handbrake_decel_min_speed_factor)
# Так ручник заметнее на высокой скорости и не “убивает” манёвры на низкой.
TUNING.DRIVE.handbrake_decel = 70.0
TUNING.DRIVE.handbrake_decel_min_speed_factor = 0.25
TUNING.DRIVE.handbrake_decel_throttle_mult = 0.55

# Как ручник влияет на руление.
#
# Важно: усиление руления от ручника должно зависеть от скорости:
# - на низкой скорости ручник не должен помогать завернуть (иначе это “чит”),
# - на высокой скорости ручник нужен, чтобы “довернуть” и пройти поворот.
#
# Реализация в DriveLogic:
# - берём max-буст `handbrake_steer_mult`,
# - включаем его только после порога `handbrake_steer_min_speed_factor`,
# - и линейно наращиваем до 1.0 (full boost) к speed_factor=1.
TUNING.DRIVE.handbrake_steer_mult = 1.55
TUNING.DRIVE.handbrake_steer_min_speed_factor = 0.35

# Dash/рывок (кнопка `A`).
#
# По умолчанию выключено (0.0), потому что это больше похоже на “аномалию/апгрейд”,
# чем на базовое поведение ручника/вождения.
TUNING.DRIVE.dash_impulse = 0.0
TUNING.DRIVE.dash_cooldown = 0.8

# Мультипликатор руления на оффроуде (обычно хуже, чем на дороге).
TUNING.DRIVE.offroad_steer_mult = 0.80

# "Сцепление" как множитель. Меньше = сильнее занос (больше d при том же рулении).
# В формуле это часть `effective_grip`:
#   side_damp = 1 - side_friction * effective_grip * dt
# Где `effective_grip` стартует с `grip` и модифицируется ручником/оффроудом.
TUNING.DRIVE.grip = 3.2
# TUNING.DRIVE.grip = 1.5

# Боковое трение: чем больше, тем быстрее “гасится” боковая скорость (меньше заноса).
# Это второй множитель в той же формуле (см. `grip` выше).
# TUNING.DRIVE.side_friction = 5.0
TUNING.DRIVE.side_friction = 3.0

# Насколько “сильнее занос” на высокой скорости.
#
# Реализация в коде делает боковое трение слабее с ростом скорости:
#   slip = 1 + side_slip_speed_mult * speed_factor
#   side_damp = 1 - (side_friction * effective_grip * dt) / slip
#
# То есть:
# - 0.0: занос не зависит от скорости
# - больше: на высокой скорости боковую скорость гасит заметно хуже (сложнее, но “тяжелее”)
# TUNING.DRIVE.side_slip_speed_mult = 1.8
TUNING.DRIVE.side_slip_speed_mult = 3

# Мультипликатор сцепления при ручнике (`B`): меньше = более "дрифтово".
# TUNING.DRIVE.handbrake_grip_mult = 0.85
TUNING.DRIVE.handbrake_grip_mult = 0.5

# Мультипликатор сцепления на оффроуде.
TUNING.DRIVE.offroad_grip_mult = 0.85

# Оффроуд — отдельная "поверхность".
#
# Цель: "иногда выгодно (срезать/объехать), но дороже".
# - на высокой скорости оффроуд быстро съедает темп (вязкий песок/грязь),
# - на низкой даёт возможность вернуться на дорогу (не стена).
#
# Реализация:
#   dv/dt = -C_lin * v - C_quad * v * |v|
# Дискретно в коде: v *= clamp(1 - (C_lin + C_quad*|v|) * dt, 0..1)

# offroad_drag_lin:
# - линейное сопротивление (как “вязкость”/трение качения в грязи),
# - сильнее ощущается на низкой/средней скорости,
# - если сделать слишком большим, машина будет “вязнуть” сразу после съезда.
# Совет: уменьши, если оффроуд слишком резко тормозит даже на маленькой скорости.
TUNING.DRIVE.offroad_drag_lin = 0.25

# offroad_drag_quad:
# - квадратичное сопротивление (как воздух/глубокий песок, растёт с |v|),
# - почти не мешает на малой скорости, но резко давит на высокой,
# - если сделать большим, оффроуд станет “жёстким лимитом” скорости.
# Совет: уменьши, если на оффроуде скорость падает слишком быстро именно на "крейсере".
TUNING.DRIVE.offroad_drag_quad = 0.012

# На оффроуде расход топлива дороже.
TUNING.DRIVE.offroad_fuel_mult = 1.8

# Общие сопротивления (вторая очередь после базовой управляемости).
#
# Цель: убрать ощущение “стены” от max_speed и сделать естественную максималку:
# чем быстрее едем, тем сильнее сопротивления тянут скорость вниз.
#
# Модель такая же как у оффроуда, но мягче:
#   dv/dt = -C_lin * v - C_quad * v * |v|
#
# drag_lin:
# - линейное сопротивление (похоже на rolling resistance / потери трансмиссии)
# - ощущается на малой/средней скорости (накат/торможение двигателем)
TUNING.DRIVE.drag_lin = 0.10
#
# drag_quad:
# - квадратичное сопротивление (аэродраг), почти не мешает на малой скорости,
#   но сильно влияет на высоких скоростях и формирует “плато” максималки.
TUNING.DRIVE.drag_quad = 0.003

# Ресурсы

# Расход топлива в простое (units/sec).
TUNING.DRIVE.fuel_per_sec_idle = 0.1

# Доп. расход топлива при газе (units/sec).
TUNING.DRIVE.fuel_per_sec_throttle = 1.0

# Top-down рендер: окно видимости дороги (в road-space "метрах" по s).
# Если дорога “обрывается” сзади/спереди — увеличивай эти значения.
TUNING.DRIVE.render_back_s = 300.0
TUNING.DRIVE.render_forward_s = 350.0

# Позиция машины на экране в top-down: Y ниже центра = видно больше дороги впереди.
TUNING.DRIVE.view_center_y = 130.0

# Где у машины “опорная точка” физики на спрайте (top-down).
#
# Мы считаем физику в одной точке (x,y). В рендере мы можем совместить эту точку
# с “задней осью”, с “центром массы” или с “передней осью”.
#
# Сейчас: физическую точку совмещаем с задней осью:
# - X: центр спрайта,
# - Y: ближе к низу спрайта.
TUNING.DRIVE.car_sprite_anchor_x = 16.0
TUNING.DRIVE.car_sprite_anchor_y = 24.0  # центр на задней оси
# TUNING.DRIVE.car_sprite_anchor_y = 8.0  # центр на передней оси
# TUNING.DRIVE.car_sprite_anchor_y = 16.0  # центр в центре

# Визуализация векторов (для тюнинга управления).
#
# Рисуем из центра машины:
# - направление (heading),
# - скорость (velocity),
# - боковое ускорение (side accel) — насколько сильно “трение” гасит занос.
TUNING.DRIVE.debug_vectors_enabled = False
TUNING.DRIVE.debug_vectors_heading_len = 20.0
TUNING.DRIVE.debug_vectors_vel_scale = 0.35
TUNING.DRIVE.debug_vectors_accel_scale = 0.02

# Телеметрия DRIVE (для отладки управления).
#
# Идея: мы пишем сэмплы не каждый кадр (чтобы не спамить консоль), а раз в N кадров,
# плюс отмечаем “события” (например, выезд на оффроуд).
# Лог печатается в консоль (через `trace`) при выходе из DRIVE (finish/evac).
TUNING.DRIVE.telemetry_enabled = False
TUNING.DRIVE.telemetry_every_frames = 20
TUNING.DRIVE.telemetry_max_lines = 140

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
TUNING.DRIVE.obstacle_radius = 2.0

# Радиус опасной зоны (по d). Чем больше, тем шире зона на дороге.
TUNING.DRIVE.zone_radius = 6.0

# Длина опасной зоны по s.
TUNING.DRIVE.zone_length = 40.0

TUNING.POI.timer_seconds = 10.0
TUNING.POI.scrap_per_loot = 5
