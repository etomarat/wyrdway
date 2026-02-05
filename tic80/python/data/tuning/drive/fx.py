from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....core.palette import Color
    from ...tuning import TUNING


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
