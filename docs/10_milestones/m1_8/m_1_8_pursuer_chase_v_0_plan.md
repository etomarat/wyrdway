# M1.8 — Pursuer Chase v0 (Return Pressure)

**Цель:** сделать возврат в гараж осмысленным и напряжённым: на return появляется преследователь (аномалия), который догоняет и периодически атакует, высасывая ресурсы.

## Метаданные
- **Файл плана:** `m_1_8_pursuer_chase_v0_plan.md`
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
- Визуал преследователя: **glitch-entity** (рваные полосы/split-каналы/фрагменты кода) + **cyan/blue lightning** в момент укуса.
- Дрен ресурсов на каждой атаке:
  - ресурсы рейда: `scrap` и `fuel` (fuel = бак машины)
  - атакующий эффект чередуется: `SCRAP/HP` ↔ `FUEL`
  - если scrap закончился → дреним **HP** тем же количеством
- Fail:
  - если `fuel <= 0` или `hp <= 0` **по пути к POI (travel)** → откат к последнему сейву
  - если `fuel <= 0` или `hp <= 0` **на return (погоня)** → fail, потеря добычи рейда (`run_scrap = 0`)

---

## Параметры тюнинга (v0 дефолты)
> Все числа — стартовые, для полировки через TUNING.

### Pursuer (distance model)
- `pursuer_grace_meters = 20`
- `pursuer_grace_seconds_cap = 4.0`
- `pursuer_start_gap_s = 150`  
  (после grace преследователь стартует на таком отставании)
- `follow_gap_s = 11`  
  (минимальная дистанция сзади; ближе преследователь не подъезжает)
- `contact_offset_s = 32`  
  (только визуальный сдвиг тела назад относительно логической контактной точки)

### Pursuer speed
- Базовая скорость преследователя (в road-space units/sec):
  - `pursuer_base_speed = 100`
- Догоняние зависит от скорости игрока относительно `TUNING.DRIVE.max_speed`:
  - `speed_factor = clamp(speed / max_speed, 0, 2)`
  - `slow_factor = clamp(1 - speed_factor, 0, 1)`
  - `catchup = slow_factor * pursuer_slow_catchup`
  - `pursuer_slow_catchup = 0`
- Доп. фактор (опционально): оффроад ускоряет догоняние:
  - `pursuer_offroad_catchup = 0`
  - `0` = фактор выключен

### Visibility / states
- `pursuer_show_dist_s = 240`  (начинаем рисовать/FX)
- `pursuer_near_dist_s = 16`   (режим NEAR и максимальная интенсивность давления)

### Strike rules
- `strike_cooldown_sec = 1.35`
- `strike_drain_amount = 2`
- `strike_begin_dist_s = 12` (кусает только когда действительно рядом)
- `strike_min_speed = 0` (`0` = укус возможен даже на очень низкой скорости)
- Триггер укуса (v0):
  - `distance <= max(strike_begin_dist_s, follow_gap_s)`
  - cooldown готов
  - выполнен speed gate (`speed >= strike_min_speed`, если порог > 0)

### Boost interaction
- На активации дорожного буста (ускорялки) отталкиваем преследователя назад:
  - `boost_pushback_s = 22`
  - `0` = отключено

### Screen / FX
- `strike_shake_intensity = 24.0` (impact в общий shake-hit канал)
- `near_vignette = 0.25` (интенсивность при NEAR)
- `near_noise = 0.5`     (интенсивность глича при NEAR)
- `contact_noise_mult = 10` (доп. множитель шума, когда преследователь уже догнал)
- `strike_noise_boost = 20` (доп. буст шума в момент укуса)
- `strike_meltdown_intensity = 1.0` (сила global-break эффекта в момент укуса)
- `strike_flash_seconds = 0.22` (длительность окна ударного визуала)

### Pursuer body (visual)
- `body_radius_chase = 9`
- `body_radius_near = 13`
- `debug_contact_marker = False` (временная дебаг-точка контакта, по умолчанию выключена)

---

## Данные / UI

### Run resources (рейд)
- `run_scrap` — добыча рейда (то, что монстр может «вернуть»)
- `car_fuel` — топливо бака (также дренится монстром)

### HUD
- Плашки:
  - `SCRAP: <run_scrap>`
  - `FUEL: <car_fuel>`
  - `PURSuer: <bar>` или `DIST: <d>` (бар предпочтительнее)
- Попапы возле машины при атаке:
  - `-2 SCRAP` или `-2 FUEL`
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
- [x] Укус по cooldown при `distance <= max(strike_begin_dist_s, follow_gap_s)`
- [x] Strike:
  - [x] триггер FX + shake
  - [x] дрен ресурсов (см. ниже)
  - [x] cooldown старт

### 3) Дрен ресурсов (чередование)
- [x] `strike_phase` переключатель: `SCRAP_HP` ↔ `FUEL`
- [x] На `SCRAP_HP`:
  - [x] `take = min(run_scrap, drain)` → `run_scrap -= take`
  - [x] `rem = drain - take` → если `rem > 0`: `car_hp -= rem`
  - [x] попапы: `-take SCRAP`, при `rem>0` попап `-rem HP`
- [x] На `FUEL`:
  - [x] `car_fuel -= drain`
  - [x] попап `-drain FUEL`
- [x] После удара: `strike_phase = other`

### 4) Визуал преследователя (v0)
- [x] World-object спрайт «glitch-entity»:
  - [x] рисовать в CHASE/NEAR позади машины по центру дорожной оси
  - [x] лёгкий lateral wobble (синус/шум) для ощущения «кружит»
  - [x] рваные сканлайны/цветовой split + фрагменты кода в NEAR
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
  - [ ] Зафиксировать финальные значения в `data/tuning/pursuer.py`

---

## DoD (готово, если)
- [x] На return появляется преследователь, который в среднем догоняет при медленной езде
- [x] Буст заметно отталкивает преследователя
- [x] При `distance <= max(strike_begin_dist_s, follow_gap_s)` укус срабатывает по кулдауну
- [x] Укус вызывает: shake + FX + popups `-SCRAP/-FUEL/-HP`
- [x] Дрен чередуется `SCRAP/HP` ↔ `FUEL`
- [x] При нуле hp/fuel происходит fail → гараж со штрафом (потеря добычи)

---

## Вне скоупа (явно)
- Реальный AI и коллизии преследователя
- Несколько типов преследователей/модификаторы узлов
- Лор и локализация терминов (пока EN)
- Продвинутые сценарии поражения (кроме fail→гараж)
