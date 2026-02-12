# SAVE/LOAD (as-is): профиль на `pmem`

Этот документ фиксирует текущее состояние системы сохранений в коде.

Текущее решение (M1): **сохраняем только профиль**. Состояние рана не сохраняется.

---

## 1) Где реализовано

- `tic80/python/core/save_system.py` — чтение/запись профиля в `pmem`.
- `tic80/python/core/game_state.py` — когда загрузить/сохранить и как применить.

---

## 2) Что сохраняем (Profile)

Сохраняемые поля профиля:
- `scrap: int`
- `garage_hp: float`
- `garage_fuel: float`
- `tuning_version: int` (для диагностики несовпадений тюнинга)

Поля хранятся в `pmem`, который принимает только int, поэтому float сохраняем как int с масштабом.

---

## 3) Формат и слоты `pmem`

Файл: `tic80/python/core/save_system.py`

Константы:
- `SAVE_MAGIC = 0x57595244` (строка `"WYRD"` как int)
- `SAVE_SCHEMA_VERSION = 3`
- `FLOAT_SCALE = 100.0`

Слоты:
- `pmem[0]` — magic
- `pmem[1]` — schema_version
- `pmem[2]` — tuning_version (из `TUNING.tuning_version`)
- `pmem[10]` — scrap
- `pmem[11]` — garage_hp * 100 (int)
- `pmem[12]` — garage_fuel * 100 (int)

---

## 4) Правила загрузки (load)

Поведение `SaveSystem.load_profile()`:
- Если magic не совпал: считаем, что сейва нет (новая игра).
- Если schema_version не совпал: считаем, что сейв несовместим (новая игра).
- Иначе читаем поля и возвращаем `SaveProfileData`.

Поведение `GameState.load_profile()`:
- Если данных нет: `profile_loaded = False`.
- Если данные есть: применяем к профилю и ставим флаги:
  - `profile_loaded = True`
  - `profile_tuning_mismatch = (save.tuning_version != TUNING.tuning_version)`

Диагностика:
- в консоль идут `trace(...)` строки при загрузке и при несовпадении тюнинга.

---

## 5) Правила сохранения (save)

`SaveSystem.save_profile()` всегда перезаписывает заголовок (magic/schema/tuning_version) и поля профиля.

Клэмпы и нормализация:
- `scrap` хранится как `max(0, int(scrap))`
- `garage_hp/garage_fuel` хранятся как `max(0, int(round(value * FLOAT_SCALE)))`

---

## 6) Точки сохранения (as-is)

В обычном режиме игры профиль сохраняется:
- перед стартом рана (GARAGE → REGION_MAP)
- после ремонта в гараже
- после применения результатов в RESULT (`GameState.apply_run_results()`)
- после reset профиля (NEW GAME)

---

## 7) Совместимость версий (as-is)

Сейчас стратегия минимальная:
- несовместимые изменения → увеличить `SAVE_SCHEMA_VERSION`
- при несовпадении версии → трактовать сейв как отсутствующий

Миграции и `last_good` пока не реализованы.

---

## 8) Что НЕ сохраняем (важно)

- `RunState` и его `delta`, инвентарь рана, позиция/сегмент DRIVE.
- плейтест‑статистика DRIVE.

Если понадобится “continue run” позже, это будет отдельное расширение схемы.
