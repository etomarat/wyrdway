# SAVE/LOAD (as-is): профиль + runtime-флаги на `pmem`

Этот документ фиксирует текущее состояние сохранений в коде.

Текущее решение: сохраняем профиль и отдельные runtime-флаги сессии. Полный `RunState` не сериализуется.

---

## 1) Где реализовано

- `tic80/python/core/save_system.py` — чтение/запись профиля и runtime-флагов в `pmem`.
- `tic80/python/core/game_state.py` — применение загрузки, rollback и recovery после прерванной сессии.

---

## 2) Что сохраняем

### 2.1 Профиль

- `scrap: int`
- `garage_hp: float`
- `garage_fuel: float`
- `theseus: int`
- `seed_counter: int`
- `tuning_version: int`

### 2.2 Runtime-флаги

- `run_active: bool` — ран был в процессе (для детекта перезапуска/обрыва).
- `chase_active: bool` — ран был в погоне/контакте с сущностью.

---

## 3) Формат и слоты `pmem`

Файл: `tic80/python/core/save_system.py`

Константы:
- `SAVE_MAGIC = 0x57595244` (`"WYRD"` как int)
- `SAVE_SCHEMA_VERSION = 6`
- `FLOAT_SCALE = 100.0`

Слоты:
- `pmem[0]` — magic
- `pmem[1]` — schema_version
- `pmem[2]` — tuning_version
- `pmem[3]` — profile seed_counter
- `pmem[10]` — profile scrap
- `pmem[11]` — profile garage_hp * 100
- `pmem[12]` — profile garage_fuel * 100
- `pmem[13]` — profile theseus
- `pmem[20]` — runtime run_active (0/1)
- `pmem[21]` — runtime chase_active (0/1)

---

## 4) Правила загрузки и rollback

`SaveSystem.load_profile()`:
- если `magic`/`schema` не совпали, профиль считается отсутствующим.
- иначе возвращается `SaveProfileData`.

`GameState.load_profile()`:
- загружает профиль и `seed_counter`;
- выставляет `profile_loaded` и `profile_tuning_mismatch`.

`GameState.rollback_to_last_save(reason, chase_contact)`:
- откатывает профиль к последнему сейву;
- добавляет штраф `Theseus` (`rollback_theseus_gain` + бонус `rollback_theseus_chase_bonus` при `chase_contact=True`);
- сохраняет результат отката;
- завершает ран и сбрасывает runtime-флаги.

`GameState.recover_interrupted_session()`:
- читает runtime-флаги на `BOOT()`;
- если сессия была прервана, выполняет rollback с начислением `Theseus`.

---

## 5) Правила сохранения (save)

`SaveSystem.save_profile(...)` всегда перезаписывает заголовок и поля профиля.

Нормализация:
- `scrap`, `theseus`, `seed_counter` клэмпятся к `>= 0`;
- `garage_hp` и `garage_fuel` сохраняются как `int(round(value * FLOAT_SCALE))`.

---

## 6) Точки сохранения

- после успешного применения результатов в `RESULT` (`GameState.apply_run_results()`);
- после rollback (`GameState.rollback_to_last_save(...)`);
- после `NEW GAME` (`GameState.start_new_game()`);
- после ремонта в гараже (через `GameState.save_profile()`).

Runtime-флаги пишутся отдельно:
- `run_active=True` при входе в `DRIVE`;
- `chase_active=True` при входе в `DRIVE(extract)`;
- оба флага сбрасываются при завершении/rollback/new game.

---

## 7) Что не сохраняем

- полный `RunState` (`delta`, инвентарь рана, позиция/сегмент DRIVE);
- временные данные сцены и эффекты кадра.
