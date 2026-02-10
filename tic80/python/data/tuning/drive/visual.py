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

# cam-v2 spring: подавление рывков на низкой скорости.
#
# Гистерезис режима velocity:
# - enter: выше этого порога камера начинает ориентироваться по velocity;
# - exit: ниже этого порога камера возвращается к heading.
# В cam-v3 blend эти пороги не используются, оставлены для обратной совместимости.
TUNING.DRIVE.cam_vel_enter_speed = 7.0
TUNING.DRIVE.cam_vel_exit_speed = 4.0
#
# Пружинное сглаживание угла камеры:
# - freq_hz: частота реакции,
# - damping: демпфирование (около 1.0 = около критического).
# Пояснения:
# - cam_spring_freq_hz: больше = камера резче догоняет цель, меньше "ватности".
# - cam_spring_damping: больше = меньше перерегулирования, но больше "тупости".
TUNING.DRIVE.cam_spring_freq_hz = 4.8
TUNING.DRIVE.cam_spring_damping = 1.1

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
# Сейчас: физическую точку совмещаем с задней осью:
# - X: центр спрайта,
# - Y: ближе к низу спрайта.
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
# Задний круг обычно можно оставить в (0,0), потому что физическая точка сейчас
# привязана к задней оси (см. car_sprite_anchor_y).
TUNING.DRIVE.hitbox_rear_px = 16.0
TUNING.DRIVE.hitbox_rear_py = 22.0
TUNING.DRIVE.hitbox_rear_radius = 6.0
TUNING.DRIVE.hitbox_front_px = 16.0
TUNING.DRIVE.hitbox_front_py = 10.0
TUNING.DRIVE.hitbox_front_radius = 6.0
