from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...tuning import TUNING


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

# camera-by-velocity: базовые параметры направления.
#
# При низкой скорости доверяем heading машины, чтобы избежать дрожи.
# Между min..full делаем плавный blend heading -> velocity direction.
# Пояснения:
# - cam_vel_min_speed: ниже этого порога velocity почти не влияет на направление камеры.
# - cam_vel_full_speed: выше этого порога направление камеры почти полностью от velocity.
# - cam_vel_dir_lerp: сглаживание направления velocity (меньше = стабильнее, но "тяжелее").
TUNING.DRIVE.cam_vel_min_speed = 3.0
TUNING.DRIVE.cam_vel_full_speed = 11.0
# Низкочастотное сглаживание velocity-направления (0..1 за кадр).
# Используется как предфильтр цели камеры перед blend/spring.
TUNING.DRIVE.cam_vel_dir_lerp = 0.16

# Пружинное сглаживание угла камеры (cam-v3 baseline):
# - freq_hz: частота реакции,
# - damping: демпфирование (около 1.0 = около критического).
# Пояснения:
# - cam_spring_freq_hz: больше = камера резче догоняет цель, меньше "ватности".
# - cam_spring_damping: больше = меньше перерегулирования, но больше "тупости".
TUNING.DRIVE.cam_spring_freq_hz = 4.8
TUNING.DRIVE.cam_spring_damping = 1.1

# Low-speed anti-jerk yaw cap (cam-v3.1).
# - cam_low_speed_cap_blend_max: до какого speed_blend действует ограничение (0..1).
# - cam_low_speed_yaw_rate_min_deg: минимальная скорость поворота цели камеры при почти нулевой скорости.
# - cam_low_speed_yaw_rate_max_deg: ограничение near-перехода к средней скорости.
TUNING.DRIVE.cam_low_speed_cap_blend_max = 0.45
TUNING.DRIVE.cam_low_speed_yaw_rate_min_deg = 260.0
TUNING.DRIVE.cam_low_speed_yaw_rate_max_deg = 720.0

# Screen shake (top-down).
# Общий лимит амплитуды, px (ограничивает сумму всех источников).
TUNING.DRIVE.shake_max_px = 4.0

# Оффроуд: сила, скорость набора/спада и частота "кочек".
# - strength: амплитуда тряски (px) при уровне offroad=1.0
# - ramp_up: скорость нарастания эффекта (1/sec)
# - ramp_down: скорость затухания эффекта (1/sec)
# - freq_hz: частота смены "кочек" (Гц)
TUNING.DRIVE.shake_offroad_strength = 2
TUNING.DRIVE.shake_offroad_ramp_up = 10.0
TUNING.DRIVE.shake_offroad_ramp_down = 6.0
TUNING.DRIVE.shake_offroad_freq_hz = 14.0

# Удар об препятствие: сила, "впрыск" травмы от impact и её спад.
# - hit_strength: амплитуда (px) при trauma=1.0
# - hit_impact_mult: сколько trauma добавлять на единицу impact
# - hit_trauma_max: максимум trauma (0..1)
# - hit_decay_per_sec: спад trauma (1/sec)
# - hit_freq_hz: частота "толчков" от удара (Гц)
# - hit_smooth_rate: сглаживание рывков (1/sec)
TUNING.DRIVE.shake_hit_strength = 3.0
TUNING.DRIVE.shake_hit_impact_mult = 0.06
TUNING.DRIVE.shake_hit_trauma_max = 1.0
TUNING.DRIVE.shake_hit_decay_per_sec = 1.6
TUNING.DRIVE.shake_hit_freq_hz = 24.0
TUNING.DRIVE.shake_hit_smooth_rate = 24.0

# Выхлоп/высокая скорость: не тряска, а плавный "дрейф" камеры + редкие толчки.
# - exhaust_strength: амплитуда (px) дрейфа при strength=1.0
# - exhaust_ramp_up/down: скорость нарастания/спада уровня (1/sec)
# - exhaust_freq_hz: частота смены направления дрейфа (Гц)
# - exhaust_smooth_rate: сглаживание дрейфа (1/sec)
# - exhaust_pulse_*: редкие короткие толчки, вероятность завязана на strength
# TUNING.DRIVE.shake_exhaust_strength = 1.2
TUNING.DRIVE.shake_exhaust_strength = 0  # Disabled. Candidate for removal.
TUNING.DRIVE.shake_exhaust_ramp_up = 3.0
TUNING.DRIVE.shake_exhaust_ramp_down = 4.0
TUNING.DRIVE.shake_exhaust_freq_hz = 2.2
TUNING.DRIVE.shake_exhaust_smooth_rate = 6.0
# TUNING.DRIVE.shake_exhaust_pulse_strength = 1.5
# Disabled. Candidate for removal.
TUNING.DRIVE.shake_exhaust_pulse_strength = 0
TUNING.DRIVE.shake_exhaust_pulse_chance_per_sec = 0.30
TUNING.DRIVE.shake_exhaust_pulse_decay_per_sec = 2.4
TUNING.DRIVE.shake_exhaust_pulse_freq_hz = 18.0
TUNING.DRIVE.shake_exhaust_pulse_smooth_rate = 28.0

# PRESET A (закомментированный): меньше jerk на выходе из дрифта, но без лишней ватности.
# Включать целиком (заменить активные значения выше).
#
# TUNING.DRIVE.cam_vel_min_speed = 3.5
# TUNING.DRIVE.cam_vel_full_speed = 11.0
# TUNING.DRIVE.cam_vel_dir_lerp = 0.16
# TUNING.DRIVE.cam_spring_freq_hz = 5.2
# TUNING.DRIVE.cam_spring_damping = 1.1
#
# PRESET B (закомментированный): максимум отзывчивости, меньше "ватности",
# но может вернуть немного резкости на выходе из дрифта.
# TUNING.DRIVE.cam_vel_min_speed = 3.0
# TUNING.DRIVE.cam_vel_full_speed = 10.0
# TUNING.DRIVE.cam_vel_dir_lerp = 0.18
# TUNING.DRIVE.cam_spring_freq_hz = 5.6
# TUNING.DRIVE.cam_spring_damping = 1.0

# Где у машины “опорная точка” физики на спрайте (top-down).
#
# Мы считаем физику в одной точке (x,y). В рендере мы можем совместить эту точку
# с “задней осью”, с “центром массы” или с “передней осью”.
#
# Сейчас: физическую точку совмещаем с центром спрайта:
# - X: центр спрайта,
# - Y: центр спрайта.
TUNING.DRIVE.car_sprite_anchor_x = 16.0
# TUNING.DRIVE.car_sprite_anchor_y = 24.0  # центр на задней оси
# TUNING.DRIVE.car_sprite_anchor_y = 8.0  # центр на передней оси
TUNING.DRIVE.car_sprite_anchor_y = 16.0  # центр в центре

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
# Круги задаются в координатах 32x32 и автоматически пересчитываются
# относительно текущего `car_sprite_anchor_*`.
TUNING.DRIVE.hitbox_rear_px = 16.0
TUNING.DRIVE.hitbox_rear_py = 22.0
TUNING.DRIVE.hitbox_rear_radius = 6.0
TUNING.DRIVE.hitbox_front_px = 16.0
TUNING.DRIVE.hitbox_front_py = 10.0
TUNING.DRIVE.hitbox_front_radius = 6.0
