# Wyrdway — GameState / Profile / RunState (as-is)

Этот документ фиксирует текущий “контракт данных” между сценами и правила мутаций.
Цель: чтобы сцены общались через один источник истины, а не через случайные глобалки.

---

## 1) Источник истины (что где живёт)

### 1.1 GameState
Файл: `tic80/python/core/game_state.py`

`GameState` — это корневой контейнер состояния:
- `profile: Profile` — долгоживущие данные между “ранами” (то, что мы сохраняем).
- `run: RunState | None` — текущий ран (живёт только в памяти, сбрасывается при завершении).
- отладочные линии кадра (для DebugOverlay).
- режим DRIVE‑плейтеста (для тюнинга управления).

### 1.2 Profile
Файл: `tic80/python/core/profile.py`

`Profile` — текущий минимальный “мета‑прогресс”:
- `scrap: int`
- `garage_hp: float`
- `garage_fuel: float`
- `upgrades: list[str]` (пока не используется геймплейно, но поле уже есть)

### 1.3 RunState
Файл: `tic80/python/core/run_state.py`

`RunState` — минимальные данные забега (M1):
- `seed: int`
- `node_id: int | None`
- `car_hp: float`
- `car_fuel: float`
- `inventory: list[RunItem]` (сейчас это только `"scrap"`, см. `RunItemId`)
- `delta: SegmentDelta | None`

### 1.4 SegmentDelta
Файл: `tic80/python/core/run_state.py`

`SegmentDelta` — итоговые данные сегмента, которые RESULT показывает и по которым
`GameState.apply_run_results()` решает “успех/провал”:
- `node_id: int | None` (для какого узла формировалась дельта)
- `poi_action: "loot" | "leave" | "timeout" | None`
- `escape_outcome: "ok" | "fail" | None`
- `items_gained: list[RunItem]` (сейчас используется только счётчик)

---

## 2) Жизненный цикл (as-is)

Точка входа: `BOOT()` в `tic80/python/main.py`.

### 2.1 Обычная игра (вертикальная петля M1)
Включается при `IS_DRIVE_PLAYTEST = False`:
- `BOOT()` вызывает `GameState.load_profile()`.
- `GarageScene` по `A` делает `save_profile()` и `start_run()`.
- `RegionMapScene` выбирает `node_id` и вызывает `run.ensure_delta(node_id)`.
- `DriveScene` обновляет вождение и меняет `run.car_hp/run.car_fuel`.
- `PoiScene` выставляет `delta.poi_action`, добавляет лут в ран, при тайм‑ауте ставит `escape_outcome="fail"`.
- `ResultScene` по `A` вызывает `GameState.apply_run_results()` и возвращает в `GarageScene`.

### 2.2 DRIVE плейтест
Включается при `IS_DRIVE_PLAYTEST = True`:
- `BOOT()` не грузит сейв, сбрасывает профиль и включает плейтест‑статистику.
- `DRIVE_PRESET` выбирает пресет.
- `DriveScene` при завершении сегмента ведёт в `ResultScene`.
- `ResultScene` по `A` запускает следующий сегмент (цикл DRIVE↔RESULT).

---

## 3) Правила мутаций (кто что имеет право менять)

### 3.1 GarageScene
Файл: `tic80/python/scenes/garage_scene.py`
- `GameState.start_run()` создаёт новый `RunState` с `car_hp/car_fuel` из профиля.
- Ремонт меняет только профиль (через `Profile.repair()`).
- Профиль сохраняется в ключевых местах (до старта, после ремонта, после reset).

### 3.2 RegionMapScene
Файл: `tic80/python/scenes/region_map_scene.py`
- Меняет только `run.node_id`.
- Создаёт/активирует “дельту сегмента” через `run.ensure_delta(run.node_id)`.

### 3.3 DriveScene
Файл: `tic80/python/scenes/drive_scene.py`
- Меняет только `run.car_hp` и `run.car_fuel` (через `RunState.apply_damage()` и `RunState.consume_fuel()` внутри drive‑логики).
- По эвакуации выставляет `delta.escape_outcome="fail"` и уходит в RESULT.
- По успешному extract выставляет `delta.escape_outcome="ok"` и уходит в RESULT.

### 3.4 PoiScene
Файл: `tic80/python/scenes/poi_scene.py`
- Выставляет `delta.poi_action`.
- При `loot` добавляет предмет(ы) в `run.inventory` и отмечает это в `delta`.
- При тайм‑ауте выставляет `delta.escape_outcome="fail"` и уходит напрямую в RESULT (упрощение M1).

### 3.5 ResultScene
Файл: `tic80/python/scenes/result_scene.py`
- В обычной игре единственное место, где результат применяется к профилю: `GameState.apply_run_results()`.
- После применения результата `GameState` завершает ран (`end_run` внутри `apply_run_results()`).

---

## 4) Границы сохранений (as-is)

Сейчас сохраняется только профиль. Ран не сериализуется.
Детали: `docs/00_spec/6_save_load.md`.

---

## 5) Инварианты (минимум)

- `Profile` никогда не содержит “живой ран”.
- `RunState.seed` задаётся при создании и не меняется в течение рана.
- `RunState.inventory_items()` возвращает копию списка (чтобы не было внешней мутации).

---

## 6) Планируемое (ещё не реализовано)

В ранних спеках встречаются поля “CarState parts/statuses”, “MetaState”, “secure/loose”.
Сейчас этого в коде нет: `Profile` и `RunState` минимальны под M1.
