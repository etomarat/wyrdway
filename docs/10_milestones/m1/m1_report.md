# M1 — отчёт по выполнению

Источник правды: текущий код в `tic80/python/` и чеклист `docs/m1_plan.md`.

Цель M1 (по плану): замкнутая петля **GARAGE → REGION_MAP → DRIVE → POI → RESULT → GARAGE**.

## 1) Итог: петля M1 работает

Петля реализована и проходима:
- `GarageScene` → старт рана → `RegionMapScene` → `DriveScene` (travel) → `PoiScene` → `DriveScene` (extract) → `ResultScene` → обратно в `GarageScene`.
- По итогам `ResultScene` результат применяется к профилю один раз, ран очищается.

Основные точки входа:
- Точка загрузки профиля: `BOOT()` вызывает `SCENE_MANAGER.state.load_profile()`. (`tic80/python/main.py`)
- Сохранения профиля: `GameState.save_profile()` вызывается в ключевых переходах. (`tic80/python/core/game_state.py`)

## 2) Сцены и управление

### GARAGE
Файл: `tic80/python/scenes/garage_scene.py`
- Экран показывает `scrap`, `hp`, `fuel`.
- `A` — старт рана (создаёт `RunState`, сохраняет профиль, переходит на карту).
- `B` — ремонт (тратит scrap, увеличивает HP, сохраняет профиль при успехе).
- Если `hp <= 0` или `fuel <= 0`, появляется `X = NEW GAME (RESET)` и по `X` профиль сбрасывается к стартовым значениям (`Profile.reset()`), затем сохраняется.

### REGION_MAP
Файл: `tic80/python/scenes/region_map_scene.py`
- Статический список узлов (сейчас 5).
- `UP/DOWN` — выбор узла, `A` — записывает `node_id` в ран и переходит в `DRIVE(travel)`.

### DRIVE
Файл: `tic80/python/scenes/drive_scene.py`
- Минимальное движение: удержание `LEFT/RIGHT` двигает позицию по оси X до `TUNING.DRIVE.segment_length`.
- Финиш: когда X достиг финиша, `A`:
  - в `travel` → `POI`
  - в `extract` → `RESULT ("EXTRACT OK")`
- Расход топлива: только когда есть движение (`move != 0.0`), расход `TUNING.DRIVE.fuel_per_sec`.
- Урон по времени: `TUNING.DRIVE.damage_per_sec` (сейчас всегда, независимо от движения).
- Провал/эвакуация: если `fuel <= 0` или `hp <= 0` → выставляется `escape_outcome="fail"` и переход в `RESULT` с причиной (`OUT OF FUEL` / `CAR DESTROYED`).

### POI
Файл: `tic80/python/scenes/poi_scene.py`
- Таймер вниз от `TUNING.POI.timer_seconds`.
- `A = LOOT`: добавляет предмет `"scrap"` в инвентарь рана (`TUNING.POI.scrap_per_loot`) и переходит в `DRIVE(extract)`.
- `B = LEAVE`: переход в `DRIVE(extract)` без лута.
- Тайм‑аут: прямой переход в `RESULT ("POI TIMEOUT")` с `escape_outcome="fail"`.
  - Примечание: это сознательное упрощение относительно “POI → DRIVE(extract) → RESULT” (решение принято в M1).

### RESULT
Файл: `tic80/python/scenes/result_scene.py`
- Показывает краткий отчёт (seed, node, fuel, inv и данные дельты, если есть).
- `A` — применяет результат к профилю через `GameState.apply_run_results()` и возвращает в `GARAGE`.

## 3) Данные: Profile / RunState и “методный стиль”

### Profile
Файл: `tic80/python/core/profile.py`
- Поля профиля: `scrap`, `garage_hp` (float), `garage_fuel` (float), `upgrades` (список строк).
- Состояние изменяется через методы: `add_scrap`, `spend_scrap`, `set_garage_stats`, `repair`, `apply_save`, `reset`.
- `reset()` не принимает параметров: сбрасывает к стартовым значениям, сохранённым при создании профиля.

### RunState
Файл: `tic80/python/core/run_state.py`
- Хранит `seed`, `node_id`, состояние машины в ранe (`car_hp`, `car_fuel`), `inventory`, `delta`.
- Инвентарь наружу отдаётся копией (`inventory_items()` возвращает `list(self._inventory)`), чтобы избежать внешней мутации.

## 4) Экономика M1 (scrap и штрафы эвакуации)

### Награда за POI
Файл: `tic80/python/scenes/poi_scene.py`
- Лут даёт `scrap` в ран (инвентарь рана).
- Перенос лута в профиль происходит только при успешном исходе в `GameState.apply_run_results()`.

### Штрафы при провале (эвакуация)
Файл: `tic80/python/core/game_state.py`
- Если `escape_outcome == "fail"`:
  - теряем fuel: `max(TUNING.PROFILE.evac_fuel_min, fuel * TUNING.PROFILE.evac_fuel_pct)`
  - теряем scrap: `TUNING.PROFILE.evac_scrap_loss`
  - лут рана не переносится в профиль

Все числа вынесены в `TUNING`:
- `tic80/python/contracts.py` (структуры тюнинга)
- `tic80/python/data/tuning.py` (конкретные значения)

## 5) SAVE/LOAD (только профиль)

Файлы:
- `tic80/python/core/save_system.py`
- `tic80/python/core/game_state.py`

Решение M1: сохраняем **только профиль**, ран не сохраняем.

### Формат
- `pmem` слоты + `SAVE_MAGIC` + `SAVE_SCHEMA_VERSION`.
- `SaveProfileData` как объект результата загрузки (удобно расширять полями).
- float‑поля (`garage_hp`, `garage_fuel`) сохраняются как `*100` (`FLOAT_SCALE = 100.0`).
- В сейв пишется `tuning_version` (из `TUNING.tuning_version`), при несовпадении с текущим:
  - в консоль идёт `trace`‑предупреждение,
  - на экране показывается строка `tuning mismatch: ...` (через debug overlay).

### Точки сохранения (M1)
Реализовано:
- Перед стартом рана (в гараже).
- После ремонта (в гараже).
- После применения результата (в `apply_run_results()`).
- После reset “новой игры”.

### Диагностика загрузки
- Если сейва нет или схема не совпадает — в консоль печатаются `trace` сообщения (`save: no magic...`, `save: schema mismatch...`).

## 6) Debug overlay / диагностика

Файлы:
- `tic80/python/core/debug.py`
- `tic80/python/main.py`

- `Y` — toggle оверлея.
- Оверлей сейчас показывает: текущую сцену, `dt`, статус профиля `loaded/new`, и предупреждение `tuning mismatch`, если есть.
- Остальные показатели (HP/fuel/timer/inv/etc.) уже отображаются на экранах сцен.

## 7) Проверки

По договорённости: все проверки из `docs/m1_plan.md` выполнены успешно (10 циклов, провалы, отсутствие двойных применений, влияние TUNING).

## 8) Известные упрощения/договорённости M1

- Провал по таймеру в POI ведёт напрямую в RESULT (без промежуточного `DRIVE(extract)`).
- Сохранения не атомарные/без `last_good` (в M1 минимальная реализация на `pmem`).
- `hp` и `fuel` — float; `scrap` — int; инвентарь рана — список предметов `"scrap"`.

