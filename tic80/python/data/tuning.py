from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..contracts import Tuning
    from ..core.palette import Color

TUNING: Tuning = Tuning()
# Поднимай версию при изменениях баланса (числа в TUNING).
TUNING.tuning_version = 9

# Fixed timestep in seconds (TIC-80 runs at 60 FPS by default).
TUNING.CORE.dt = 1 / 60

# Initial debug overlay state on boot.
TUNING.DEBUG.overlay_default = False

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

# Метрика заноса (slip) использует деление на (abs(v_forward) + eps).
# Эту "подпорку" (eps) держим в тюнинге, чтобы не было скачков на нулевой скорости.
TUNING.DRIVE.slip_eps_speed = 5.0

# Следы шин (skid marks): screen-space фидбек заноса.
#
# Параметры подобраны “по ощущению” и легко тюнятся:
# - skid_slip_threshold: с какого slip начинать рисовать следы
# - skid_min_speed: не рисовать следы на почти нулевой скорости
# - skid_back_px / skid_wheel_dx_px / skid_seg_len_px: геометрия относительно центра машины
# - skid_life_frames: длина хвоста (сколько кадров живёт сегмент)
# - skid_slant_scale / skid_slant_max: насколько сильно наклоняем след по v_side
TUNING.DRIVE.skid_slip_threshold = 0.25
TUNING.DRIVE.skid_min_speed = 5.0
TUNING.DRIVE.skid_back_px = 12.0
TUNING.DRIVE.skid_wheel_dx_px = 5.0
TUNING.DRIVE.skid_seg_len_px = 8.0
TUNING.DRIVE.skid_life_frames = 24
# Начиная с какого возраста (в кадрах жизни сегмента) переключаем цвет следа на более светлый.
# Меньше значение => светлый цвет появится раньше (будет заметнее).
TUNING.DRIVE.skid_light_after_frames = 18
TUNING.DRIVE.skid_slant_scale = 16.0
TUNING.DRIVE.skid_slant_max = 16.0

# FX частицы (пыль + speed-lines).
#
# Цвета:
# - пыль/грязь выбираем жёлто-оранжевую гамму (чтобы отличаться от зелёной дороги и серых следов)
#   SWEETIE-16: ORANGE=3, YELLOW=4 (см. `docs/30_style/0_palette_sweetie16.md`)
#
# Механика:
# - стартовая пыль: короткий “пух” при начале движения (speed 0 -> >0)
# - оффроад пыль: постоянный сигнал OFFROAD
# - speed-lines: эффект высокой скорости (speed_factor > порога)
TUNING.DRIVE.fx_particles_max = 80
# Стартовая пыль на дороге (серые тона).
TUNING.DRIVE.fx_start_dust_color_a = Color.DARK_GREY
TUNING.DRIVE.fx_start_dust_color_b = Color.GREY
# Оффроад пыль (жёлто-оранжевые тона).
TUNING.DRIVE.fx_offroad_dust_color_a = Color.YELLOW
TUNING.DRIVE.fx_offroad_dust_color_b = Color.ORANGE
TUNING.DRIVE.fx_start_dust_seconds = 1
TUNING.DRIVE.start_skid_seconds = 1.5
TUNING.DRIVE.fx_damage_dust_seconds = 0.25
TUNING.DRIVE.fx_damage_dust_rate = 120.0
TUNING.DRIVE.fx_dust_life_frames = 24
# Длина “палочки” пыли (в пикселях).
# - 0 => точки (самый читаемый вариант; похоже на песок/грязь)
# - >0 => короткие штрихи (может выглядеть как “хлопушки”, если слишком длинно)
TUNING.DRIVE.fx_dust_len_px = 0.0
TUNING.DRIVE.fx_dust_rate_start = 100.0
TUNING.DRIVE.fx_dust_rate_offroad = 60.0
TUNING.DRIVE.fx_dust_min_speed = 8.0
# Откуда спавним пыль относительно центра машины на экране (top-down).
# Эти параметры НЕ связаны со skid marks: следы — это “хвост”, а пыль — “частицы из-под колёс”.
#
# Если кажется, что пыль выходит “из кузова”, увеличивай fx_dust_back_px (сдвиг вниз).
TUNING.DRIVE.fx_dust_wheel_dx_px = 5.0
TUNING.DRIVE.fx_dust_back_px = 12.0
# Небольшой шум, чтобы пыль не была идеальными столбиками.
TUNING.DRIVE.fx_dust_jitter_x_px = 5.0
TUNING.DRIVE.fx_dust_jitter_y_px = 4.0
TUNING.DRIVE.fx_dust_spread_vx = 80.0
TUNING.DRIVE.fx_dust_spread_vy = 40.0

TUNING.DRIVE.fx_speedlines_min_speed_factor = 1.05
TUNING.DRIVE.fx_speedlines_rate = 35.0
TUNING.DRIVE.fx_speedlines_life_frames = 18
TUNING.DRIVE.fx_speedlines_len_px = 6.0
TUNING.DRIVE.fx_speedlines_vy = 180.0
TUNING.DRIVE.fx_speedlines_x_spread = 16.0
# Вертикальный диапазон speed-lines относительно машины: за машиной (ниже по Y).
# 0..20 = в районе кузова, 20..80 = “хвост” за машиной.
TUNING.DRIVE.fx_speedlines_back_y0 = 0.0
TUNING.DRIVE.fx_speedlines_back_y1 = 20.0
TUNING.DRIVE.fx_speedlines_color_a = Color.WHITE
TUNING.DRIVE.fx_speedlines_color_b = Color.LIGHT_BLUE

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
TUNING.DRIVE.speed_cap = 200.0

# Максимальная скорость заднего хода.
TUNING.DRIVE.max_reverse_speed = 18.0

# Разгон при газе (units/sec^2).
TUNING.DRIVE.accel = 50.0

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
#
# Где handbrake_decel_min_speed_factor — нижний предел для множителя:
# - БОЛЬШЕ значение => ручник сильнее тормозит даже на низкой скорости
#   (и вообще “больше похож на тормоз”).
# - МЕНЬШЕ значение => на низкой скорости ручник тормозит слабее
#   (и больше остаётся “инструментом заноса”, а не стоп-кнопкой).
#
# Если одновременно зажат газ (throttle), мы выбираем множитель по ситуации:
# - если ещё и поворачиваем (steer_input != 0), ручник больше “про дрифт” и
#   замедляет слабее:
#     amount *= handbrake_decel_throttle_turn_mult
# - если газуем прямо, ручник должен быть “дорогим” режимом (иначе его можно держать
#   всегда), поэтому тормозим сильнее:
#     amount *= handbrake_decel_throttle_straight_mult
#
# Важно: оба *_mult — это множители ТОРМОЖЕНИЯ (меньше => меньше замедляет).
TUNING.DRIVE.handbrake_decel = 70.0
TUNING.DRIVE.handbrake_decel_min_speed_factor = 0.15
TUNING.DRIVE.handbrake_decel_throttle_turn_mult = 0.01
TUNING.DRIVE.handbrake_decel_throttle_straight_mult = 0.75

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

# Восстановление скорости из заноса (“дрифт быстрее”).
#
# Проблема: в текущей модели при повороте появляется боковая скорость `v_side`, и мы её
# гасим трением. Это уменьшает модуль скорости, и игрок ощущает, что “в повороте тормозит”,
# даже если он держит газ.
#
# Решение (аркадное): часть “схлопнутой” боковой скорости переводим в продольную (v_forward),
# но только когда игрок держит газ. Это делает дрифт тактически полезным: на правильной линии
# ты меньше теряешь темп.
#
# Математика:
#   removed = abs(v_side_before) - abs(v_side_after)   (>=0)
#   v_forward += clamp(removed * side_recovery_mult, 0..side_recovery_max_add)
#
# Параметры:
# - side_recovery_mult: доля восстановления (0..1). Больше => меньше потерь скорости в заносе.
# - side_recovery_max_add: потолок добавки за кадр (units/sec), чтобы не было “рывков” при
#   резком отпускании ручника.
# - side_recovery_min_speed_factor: порог по скорости (0..1), ниже которого восстановление
#   выключено (чтобы на малой скорости не было странных эффектов).
TUNING.DRIVE.side_recovery_mult = 0.35
TUNING.DRIVE.side_recovery_max_add = 3.0
TUNING.DRIVE.side_recovery_min_speed_factor = 0.25

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
TUNING.DRIVE.side_friction = 5.0
# TUNING.DRIVE.side_friction = 3.0

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
TUNING.DRIVE.side_slip_speed_mult = 3.5

# Мультипликатор сцепления при ручнике (`B`): меньше = более "дрифтово".
# TUNING.DRIVE.handbrake_grip_mult = 0.85
TUNING.DRIVE.handbrake_grip_mult = 0.4

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
TUNING.DRIVE.drag_lin = 0.15
#
# drag_quad:
# - квадратичное сопротивление (аэродраг), почти не мешает на малой скорости,
#   но сильно влияет на высоких скоростях и формирует “плато” максималки.
TUNING.DRIVE.drag_quad = 0.003

# Ресурсы

# Расход топлива в простое (units/sec).
TUNING.DRIVE.fuel_per_sec_idle = 0.05

# Доп. расход топлива при газе (units/sec).
TUNING.DRIVE.fuel_per_sec_throttle = 1.0

# Top-down рендер: окно видимости дороги (в road-space "метрах" по s).
# Если дорога “обрывается” сзади/спереди — увеличивай эти значения.
TUNING.DRIVE.render_back_s = 300.0
TUNING.DRIVE.render_forward_s = 350.0

# Позиция машины на экране в top-down: Y ниже центра = видно больше дороги впереди.
#
# Ограничиваем min/max, чтобы:
# - спрайт машины не обрезался снизу экрана;
# - камера не “уплывала” слишком высоко (иначе будет плохо видно, куда рулить).
# Эти значения обычно трогать не нужно, но они полезны при смене размера спрайта/якоря
# и при экспериментах с компоновкой HUD.
TUNING.DRIVE.view_center_y = 100.0
# Минимально допустимый Y для `view_center_y` (зажим в рендере).
TUNING.DRIVE.view_center_y_min = 40.0
# Максимально допустимый Y для `view_center_y` (зажим в рендере).
TUNING.DRIVE.view_center_y_max = 128.0

# Где у машины “опорная точка” физики на спрайте (top-down).
#
# Мы считаем физику в одной точке (x,y). В рендере мы можем совместить эту точку
# с “задней осью”, с “центром массы” или с “передней осью”.
#
# Сейчас: физическую точку совмещаем с задней осью:
# - X: центр спрайта,
# - Y: ближе к низу спрайта.
TUNING.DRIVE.car_sprite_anchor_x = 16.0
# TUNING.DRIVE.car_sprite_anchor_y = 24.0  # центр на задней оси
# TUNING.DRIVE.car_sprite_anchor_y = 8.0  # центр на передней оси
TUNING.DRIVE.car_sprite_anchor_y = 16.0  # центр в центре

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

# Визуализация активной зоны (контур) для проверки коллизии зон с хитбоксами.
TUNING.DRIVE.debug_zones_enabled = True

# Визуализация хитбоксов машины (для настройки коллизий).
#
# Мы используем 2 круга: задняя ось и передняя ось. Это компромисс между
# одним большим кругом (слишком грубо) и 4 колёсами (слишком сложно).
#
# Координаты задаются в пикселях спрайта (32x32), а затем автоматически
# переводятся в экранные координаты через `car_sprite_anchor_*`.
# Это важно: хитбокс “ездит” вместе со спрайтом и совпадает с тем, по чему
# ориентируется игрок.
#
# Задний круг обычно можно оставить в (0,0), потому что физическая точка сейчас
# привязана к задней оси (см. car_sprite_anchor_y).
TUNING.DRIVE.debug_hitboxes_enabled = False
TUNING.DRIVE.hitbox_rear_px = 16.0
TUNING.DRIVE.hitbox_rear_py = 22.0
TUNING.DRIVE.hitbox_rear_radius = 6.0
TUNING.DRIVE.hitbox_front_px = 16.0
TUNING.DRIVE.hitbox_front_py = 10.0
TUNING.DRIVE.hitbox_front_radius = 6.0

# Телеметрия DRIVE (для отладки управления).
#
# Идея: мы пишем сэмплы не каждый кадр (чтобы не спамить консоль), а раз в N кадров,
# плюс отмечаем “события” (например, выезд на оффроуд).
# Лог печатается в консоль (через `trace`) при выходе из DRIVE (finish/evac).
TUNING.DRIVE.telemetry_enabled = True
TUNING.DRIVE.telemetry_every_frames = 20
TUNING.DRIVE.telemetry_max_lines = 140

# Объекты на дороге (m1.5)
#
# Плотности задаются "на 100 метров": 1.0 означает "в среднем 1 объект на 100м".
# Количество на сегмент берём примерно как: (total_length / 100) * density.
#
# Важно: объекты сейчас спавнятся детерминированно по seed и учитывают safe start.

# Средняя плотность препятствий.
TUNING.DRIVE.obstacles_per_100m = 1.0

# Средняя плотность опасных зон.
TUNING.DRIVE.zones_per_100m = 0.2

# Минимальная дистанция между объектами (по s).
TUNING.DRIVE.spawn_min_distance_between = 50.0

# Отступ от краёв дороги, чтобы не спавнить объекты вплотную к обочине.
TUNING.DRIVE.spawn_min_distance_from_edges = 3.0

# Радиус препятствия (в road-space единицах).
TUNING.DRIVE.obstacle_radius = 2.0

# Дальность отрисовки препятствий вокруг текущего `road_s` (в единицах s).
# Если увеличить — препятствия будут появляться раньше, но кадр станет тяжелее.
TUNING.DRIVE.obstacle_render_range_s = 200.0

# Урон за столкновение с препятствием (единоразово, за каждое препятствие).
TUNING.DRIVE.obstacle_hit_damage = 8.0

# Радиус зоны (по d). Чем больше, тем шире полоса на дороге.
TUNING.DRIVE.zone_radius = 5.0

# Длина зоны по s.
TUNING.DRIVE.zone_length = 60.0

# Зоны на дороге (m1.5):
# Сейчас используем их как “ускорялки” (boost pads), потому что визуально они читаются
# как дорожная разметка/панели ускорения.
#
# Механика ускорялки:
# - пока машина внутри зоны (по s/d), добавляем ускорение ВДОЛЬ направления дороги
#   (`zone_boost_forward_accel`);
# - и (опционально) добавляем ускорение К ЦЕНТРУ дороги (`zone_boost_center_accel`).
#   Мы держим этот параметр, но по умолчанию он выключен: на резких поворотах
#   “магнит к центру” часто мешает больше, чем помогает.
# - вместо “магнита” делаем ускорялку “безопасной полосой”:
#   * повышаем сцепление (`zone_grip_mult`);
#   * и дополнительно гасим боковую скорость (занос) через `zone_antislip`.
#
# Пример “на пальцах”:
# - если `zone_boost_forward_accel = 80`, а машина проводит на панели 0.5 секунды,
#   то прибавка скорости будет примерно +40 units/sec (потому что dv = a * t).
#
# Примечание:
# Мы не используем “периодический урон/штраф по времени” на дороге: зоны — это ускорялки/безопасные полосы.
# Если когда-нибудь понадобится “опасная” зона, лучше добавить отдельный тип зоны, а не перегружать этот.
TUNING.DRIVE.zone_boost_forward_accel = 30.0
TUNING.DRIVE.zone_boost_center_accel = 0.0
# Сцепление внутри ускорялки: больше = легче стабилизировать машину на панели.
TUNING.DRIVE.zone_grip_mult = 2.2
# Минимальное effective_grip внутри ускорялки (grip-floor).
#
# Зачем: ручник снижает сцепление мультипликатором (`handbrake_grip_mult`), и на высокой
# скорости это может сделать бустер бесполезным. Grip-floor гарантирует, что на панели
# будет хотя бы некоторый “минимальный зацеп”, даже если ты в дрифте на ручнике.
#
# Пример:
#   base_grip=4.2, zone_grip_mult=2.2 => 9.24
#   handbrake_grip_mult=0.4 => 3.70
#   zone_grip_floor=6.0 => итоговый effective_grip = max(3.70, 6.0) = 6.0
TUNING.DRIVE.zone_grip_floor = 6.0
# Анти-занос внутри ускорялки (1/sec): дополнительно гасит v_side.
# Больше = сильнее “стабилизатор”, но слишком большое значение убьёт удовольствие от дрифта.
TUNING.DRIVE.zone_antislip = 0.01

TUNING.POI.timer_seconds = 10.0
TUNING.POI.scrap_per_loot = 5
