# DRIVE (m1.6): плейтест, камера и читаемость заноса (as-is)

Этот документ фиксирует текущие решения m1.6 вокруг читаемости заноса в DRIVE:
- как запускать плейтест без петли M1,
- как работает “камера по скорости” (heading↔velocity),
- какие ручки тюнинга крутить и где они живут.

---

## 1) Быстрый плейтест DRIVE (без GARAGE/POI)

Точка входа: `tic80/python/main.py`.

Режим управляется флагом:
- по умолчанию: `IS_DRIVE_PLAYTEST = False`
- для плейтеста: `IS_DRIVE_PLAYTEST = True`

Поведение:
- сейв профиля не грузится,
- профиль сбрасывается на стартовые значения,
- запускается цикл: `DRIVE_PRESET → DRIVE(travel) → RESULT → DRIVE(travel) → ...`

Сцена выбора пресета:
- `tic80/python/scenes/drive_preset_scene.py`
- на `A (Z)` выбранный пресет применяет оверрайды к `TUNING.DRIVE.*` и запускает `DRIVE`.

Важно: пресеты меняют **только значения тюнинга** (без изменения логики).

---

## 2) Контрольные кнопки плейтеста (as-is)

Файлы:
- `tic80/python/main.py` — общий хук debug-переключателя.
- `tic80/python/scenes/drive_scene.py` — рестарт сегмента и накопление статистики.
- `tic80/python/scenes/result_scene.py` — переход к следующему сегменту.

Сейчас есть 3 “быстрых” механизма:
- В `TIC()` по `keyp(4)` включается/выключается `TUNING.DRIVE.debug_vectors_enabled` и `TUNING.DRIVE.debug_hitboxes_enabled`.
- В `DriveScene.update()` при `state.playtest_enabled` и `keyp(18)` выполняется рестарт текущего сегмента (через повторный `enter(...)`).
- В `ResultScene.update()` при `state.playtest_enabled` по `A (Z)` стартует следующий сегмент, сохраняя текущие `hp/fuel` как “гаражные”.

---

## 3) Направление камеры: heading ↔ velocity (m1.6)

В top-down DRIVE мир рисуется в системе координат камеры:
- вверх экрана = “вперёд по направлению камеры”,
- вправо экрана = “вправо от направления камеры”.

Ключевая идея m1.6:
- на низкой скорости направление камеры следует **heading** (куда смотрит машина), чтобы избежать дрожи,
- на высокой скорости направление камеры следует **velocity** (куда реально движется машина), чтобы занос читался.

Реализация:
- `tic80/python/scenes/drive/drive_topdown_renderer.py` (`_camera_forward(...)`)

Тюнинг-ручки (файл `tic80/python/data/tuning/drive/visual.py`):
- `cam_vel_min_speed` — ниже порога velocity почти не влияет на камеру.
- `cam_vel_full_speed` — выше порога камера почти полностью от velocity.
- `cam_vel_dir_lerp` — сглаживание направления velocity (предфильтр цели).

---

## 4) Пружинное сглаживание угла (cam-v3 baseline)

После вычисления “цели” (blended heading/velocity) камера сглаживает угол через пружину:
- меньше рывков,
- лучше читается траектория на скорости.

Реализация:
- `tic80/python/scenes/drive/drive_topdown_renderer.py` (`_step_camera_spring(...)`)

Тюнинг-ручки (файл `tic80/python/data/tuning/drive/visual.py`):
- `cam_spring_freq_hz` — частота реакции (больше = резче).
- `cam_spring_damping` — демпфирование (больше = меньше перерегулирования, но больше “ватности”).

---

## 5) Low-speed anti-jerk yaw cap (cam-v3.1)

Проблема: на почти нулевой скорости velocity-направление становится нестабильным, и цель камеры может “дёргаться”.

Решение: ограничить скорость поворота **цели** камеры, пока speed_blend маленький.

Реализация:
- `tic80/python/scenes/drive/drive_topdown_renderer.py` (`_cap_low_speed_target_angle(...)`)

Тюнинг-ручки (файл `tic80/python/data/tuning/drive/visual.py`):
- `cam_low_speed_cap_blend_max` — до какого `speed_blend` действует ограничение.
- `cam_low_speed_yaw_rate_min_deg` — минимум (почти ноль скорости).
- `cam_low_speed_yaw_rate_max_deg` — потолок ближе к средней скорости.

---

## 6) Где смотреть “почему так”

Планы и лог экспериментов:
- `docs/10_milestones/m1_6/m_1_6_drift_readability_plan.md`
- `docs/10_milestones/m1_6/m_1_6_drift_readability_log.md`
