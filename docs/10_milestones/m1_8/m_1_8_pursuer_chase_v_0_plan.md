# M1.8 — Pursuer Chase v0 (Return Pressure)

**Цель:** сделать возврат в гараж осмысленным и напряжённым: на return появляется преследователь (аномалия), который догоняет и периодически атакует, высасывая ресурсы.

## Метаданные
- **Файл плана:** `m_1_8_pursuer_chase_v_0_plan.md`
- **Ветка:** `m1.8-pursuer-chase-v0`
- **Предыдущая веха:** M1.7 ✅ (минимальная петля с return, ремонт в гараже, подписанный лут)

---

## Решения (зафиксировано) ✅
- Преследователь активен **только на return (дорога обратно в гараж)**.
- Есть **grace-период** (метры/секунды), чтобы игрок успел набрать скорость, но с верхним капом.
- HUD показывает **близость преследователя** (distance to car), + показываем ресурсы рейда.
- `run_scrap` для дрен/штрафов = **добыча текущего рейда**, которую везём в гараж.
- Преследователь — **объект в мире** (в topdown), плюс HUD/FX как «наступление».
- Атака — **рывками (strike) с кулдауном**:
  - когда преследователь близко, он едет по центру «в хвосте»
  - укус/выпад происходит по **cooldown**, если выполнен порог дистанции укуса
  - в момент атаки: **скриншейк + глич/FX + попапы -ресурсы**
- Визуал преследователя: вариантный (малый `The Entity` и большой `The Prime Entity`) + **cyan/blue lightning** в момент укуса.
- Дрен ресурсов на каждой атаке (as-is):
  - по умолчанию преследователь дренит `SCRAP`, затем остаток в `HP` (если scrap не хватило)
  - fuel-фаза есть как **опциональный режим** профиля (`strike_enable_fuel_phase`)
  - для текущих профилей (`The Entity`, `The Prime Entity`) fuel-фаза выключена
- Fail:
  - если `fuel <= 0` или `hp <= 0` **по пути к POI (travel)** → откат к последнему сейву
  - если `fuel <= 0` или `hp <= 0` **на return (погоня)** → fail, потеря добычи рейда (`run_scrap = 0`)

---

## Параметры тюнинга (as-is)
> Текущие значения вынесены в:
> `tic80/python/data/tuning/pursuer.py` и `tic80/python/data/tuning/pursuers/*.py`.

### Global pursuer tuning
- `enabled = True`
- `grace_meters = 20.0`
- `grace_seconds_cap = 4.0`
- `active_variant = entity` (по умолчанию)

### Shared chase model (в обоих профилях сейчас)
- `start_gap_s = 150`
- `base_speed = 100`
- `slow_catchup = 0`
- `offroad_catchup = 0`
- `show_dist_s = 240`
- `near_dist_s = 24`
- `boost_pushback_s = 22`

### Strike rules (as-is)
- `strike_cooldown_sec = 1.35`
- `strike_min_speed = 0`
- Триггер укуса:
  - `distance <= strike_begin_dist_s`
  - cooldown готов
  - speed gate выполнен (`speed >= strike_min_speed`, если порог > 0)
- `follow_gap_s` используется как ограничение максимального приближения преследователя к машине, но не как отдельный `max(...)` в strike-предикате.

### Variant: The Entity (small)
- `name = "The Entity"`
- `contact_offset_s = 0`
- `intro_entry_screen_y = 146`
- `intro_entry_seconds = 0.45`
- `strike_drain_amount = 2`
- `strike_enable_fuel_phase = False`
- `strike_drain_hp_after_scrap = True`
- `strike_begin_dist_s = 11`
- `follow_gap_s = 10`
- `body_radius_chase = 6`
- `body_radius_near = 8`
- `strike_shake_intensity = 12.0`
- `near_vignette = 0.12`
- `near_noise = 0.25`
- `contact_noise_mult = 5.0`
- `strike_noise_boost = 10.0`
- `strike_meltdown_intensity = 0.5`
- `strike_flash_seconds = 0.22`
- `debug_contact_marker = False`

### Variant: The Prime Entity (boss)
- `name = "The Prime Entity"`
- `contact_offset_s = 32`
- `intro_entry_screen_y = 164`
- `intro_entry_seconds = 0.75`
- `strike_drain_amount = 4`
- `strike_enable_fuel_phase = False`
- `strike_drain_hp_after_scrap = True`
- `strike_begin_dist_s = 12`
- `follow_gap_s = 11`
- `body_radius_chase = 9`
- `body_radius_near = 13`
- `code_shard_radius_inner = 24`
- `code_shard_radius_outer = 50`
- `code_shard_up_bias = 0`
- `code_shard_count_chase = 4`
- `code_shard_count_near = 8`
- `strike_shake_intensity = 24.0`
- `near_vignette = 0.25`
- `near_noise = 0.5`
- `contact_noise_mult = 10.0`
- `strike_noise_boost = 20.0`
- `strike_meltdown_intensity = 1.0`
- `strike_flash_seconds = 0.22`
- `debug_contact_marker = False`

---

## Данные / UI

### Run resources (рейд)
- `run_scrap` — добыча рейда (то, что монстр может «вернуть»)
- `car_fuel` — топливо бака (может дрениться монстром, если включить fuel-фазу профиля)

### HUD
- Плашки:
  - `ENTITY THREAT` бар (сверху по центру), под ним имя активного варианта
  - `SCRAP` бар под `HP` слева, плюс цифра текущего значения
  - базовые `HP/FUEL` остаются в общем DRIVE HUD
- Попапы возле машины при атаке:
  - `-N SCRAP`
  - если включить fuel-фазу в профиле: `-N FUEL`
  - если scrap < drain → показываем ещё попап `-X HP`

---

## План работ

### 0) Подготовка
- [x] Добавить новую веху M1.8 в документацию/роадмап (минимально)
- [x] Добавить тюнинг-параметры в `TUNING` (раздел `DRIVE` или новый `PURSUER`)

### 1) Pursuer model (без визуала)
- [x] На старте return инициализировать pursuer state:
  - [x] grace meters + time cap
  - [x] `pursuer_s = car_s - pursuer_start_gap_s`
- [x] Каждый тик обновлять pursuer:
  - [x] вычислить `slow_factor` от `speed / max_speed`
  - [x] добавить offroad catchup если игрок в оффроуде (`logic.offroad`)
  - [x] интегрировать `pursuer_s += (base + catchup) * dt`
- [x] На boost событии: `pursuer_s -= boost_pushback_s`
- [x] Вычислять `d = car_s - pursuer_s` и публиковать в HUD

### 2) Состояния и правила атаки
- [x] State machine:
  - [x] FAR (d > show)
  - [x] CHASE (show >= d > near)
  - [x] NEAR (d <= near)
- [x] Укус по cooldown при `distance <= strike_begin_dist_s`
- [x] Strike:
  - [x] триггер FX + shake
  - [x] дрен ресурсов (см. ниже)
  - [x] cooldown старт

### 3) Дрен ресурсов (текущий режим + опциональная fuel-фаза)
- [x] `strike_phase` переключатель: `SCRAP_HP` ↔ `FUEL` (включается профилем)
- [x] На `SCRAP_HP`:
  - [x] `take = min(run_scrap, drain)` → `run_scrap -= take`
  - [x] `rem = drain - take` → если `rem > 0`: `car_hp -= rem`
  - [x] попапы: `-take SCRAP`, при `rem>0` попап `-rem HP`
- [x] На `FUEL` (опционально, если `strike_enable_fuel_phase=True`):
  - [x] `car_fuel -= drain`
  - [x] попап `-drain FUEL`
- [x] После удара: `strike_phase = other`

### 4) Визуал преследователя (v0)
- [x] World-object преследователь:
  - [x] рисовать в CHASE/NEAR позади машины по центру дорожной оси
  - [x] лёгкий lateral wobble (синус/шум) для ощущения «кружит»
  - [x] вариантный визуал (`The Entity` компактный, `The Prime Entity` крупный glitch-тело)
- [x] Strike FX:
  - [x] cyan/blue lightning к машине на 8–12 кадров
  - [x] усиление глича/вспышка
  - [x] скриншейк

### 5) HUD/FX «наступление»
- [x] Бар дистанции (чем ближе — тем опаснее)
- [x] Лёгкая виньетка/шум, усиливающиеся в NEAR

### 6) Fail outcome (v0)
- [x] При `hp<=0` или `fuel<=0` по пути к POI (travel):
  - [x] откат к последнему сейву (без применения результата текущего рейда)
- [x] При `hp<=0` или `fuel<=0` на return:
  - [x] fail → переход в гараж
  - [x] штраф v0: `run_scrap = 0` (потеря добычи рейда)

### 7) Debug/тест
- [x] Debug overlay: `d`, `pursuer_speed`, state, cooldown, phase
- [ ] Хоткеи: toggle pursuer, force NEAR, force STRIKE

### 8) Visual Polish (pending approval)
- [x] Увеличить визуальный размер преследователя (быстрый шаг):
  - [x] Поднять базовый радиус в CHASE
  - [x] Поднять радиус в NEAR (вплоть до визуально "почти ширины дороги")
  - [ ] Проверить читаемость машины под оверлеем преследователя
- [x] Разделить шум по состояниям:
  - [x] До догона (`FAR/CHASE`) шум делать монохромным (white/light_grey/dark_grey), как статика
  - [x] После входа в контактную дистанцию переключать шум в цветной "digital glitch" (cyan/blue/purple)
  - [x] Сохранить текущие множители интенсивности (`near_noise`, `contact_noise_mult`, `strike_noise_boost`)
- [x] Добавить экранный "meltdown" в момент укуса:
  - [x] Кратковременный global-break эффект на время `strike_flash`
  - [x] Бюджетные эффекты: scanline shear + line dropouts + channel split
  - [x] Эффект должен быстро затухать и не ломать читаемость HUD
- [ ] Прогон плейтеста и тюнинг:
  - [ ] Проверить FPS/читаемость на длинной сессии
  - [ ] Подкрутить интенсивность для CHASE/NEAR/STRIKE отдельно
  - [ ] Зафиксировать финальные значения в `data/tuning/pursuer.py` и `data/tuning/pursuers/*.py`

---

## DoD (готово, если)
- [x] На return появляется преследователь, который в среднем догоняет при медленной езде
- [x] Буст заметно отталкивает преследователя
- [x] При `distance <= strike_begin_dist_s` укус срабатывает по кулдауну
- [x] Укус вызывает: shake + FX + popups `-SCRAP/-HP` (и `-FUEL`, если fuel-фаза включена в профиле)
- [x] Базовый режим дренит `SCRAP` и затем `HP`; fuel-фаза поддерживается как опциональная
- [x] При нуле hp/fuel происходит fail → гараж со штрафом (потеря добычи)

---

## Вне скоупа (явно)
- Реальный AI и коллизии преследователя
- Радикально разные типы поведения (сейчас различается в основном визуал и профиль тюнинга)
- Лор и локализация терминов (пока EN)
- Продвинутые сценарии поражения (кроме fail→гараж)
