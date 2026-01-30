# Wyrdway — RunState v0 (Contract)

Этот документ фиксирует **контракт данных** между сценами (GARAGE/REGION_MAP/DRIVE/POI/RESULT) и правила их изменения.

Цель: чтобы сцены не обменивались «случайными глобалками», а работали через один источник истины.

---

## 0) Термины

- **MetaState** — долгоживущие данные (между забегами, сохраняются в сейв).
- **RunState** — данные текущего забега (сбрасываются при старте нового рана).
- **Segment** — один «шаг» по региону: выбор узла → DRIVE(travel) → (POI → DRIVE(extract)) → RESULT.
- **Secure / Loose** — «закреплённое» (в гараже) vs «незакреплённое» (в поездке) имущество.

---

## 1) Время жизни и ответственность

### Кто создаёт и сбрасывает RunState
- **GARAGE** создаёт новый RunState при `Start Run`.
- **RESULT** завершает сегмент; при финале поездки/провале выполняет «возврат в гараж» и (при необходимости) сбрасывает RunState.

### Источник истины
- **RunState = истина** для забега.
- `params` при переходе сцен — только контекст входа (например `mode="extract"`), не место хранения прогресса.

---

## 2) Схема MetaState (v0)

MetaState — то, что живёт в гараже и переживает провал.

Минимальный набор на v0:
- `meta.version` — версия формата (инкремент при изменениях)
- `meta.profile_id` — идентификатор профиля
- `meta.unlocked_upgrades` — set/list id чертежей/апгрейдов
- `meta.resources_secure` — ресурсы в гараже (scrap/electronics/chem/fuel)
- `meta.inventory_secure` — закреплённые предметы/детали (опционально v0)
- `meta.car_garage` — состояние машины в гараже (что установлено / базовые статы)

Примечание:
- В v0 можно держать `inventory_secure` пустым, а сохранять только `resources_secure`.

---

## 3) Схема RunState (v0)

### 3.1 Общие поля забега
- `run.version` — версия схемы RunState
- `run.seed` — seed рана (для воспроизводимости и RNG)
- `run.region_id` — текущий регион
- `run.region_seed` — seed региона/графа узлов (можно = seed)
- `run.node_id` — текущий выбранный узел (на который едем)
- `run.threat_level` — уровень угрозы/напряжения (число)
- `run.active_upgrade_id` — активка на кнопке B (или `None`)

### 3.2 Route / граф узлов (минимум)
- `run.route` — описание графа узлов (минимально: список узлов + связи)
- `run.route_progress` — какие узлы уже пройдены/текущая позиция

v0 допускает «плоский маршрут»:
- `route.nodes = [{id,type,poi_id,risk,reward,next_ids...}, ...]`
- `route.current_id`

### 3.3 CarState (v0)
Машина = персонаж, поэтому состояние хранится детально, но компактно.

- `run.car.fuel` — топливо
- `run.car.battery` — батарея/электрика
- `run.car.heat` — перегрев
- `run.car.parts` — HP по деталям (минимум 6):
  - `body`, `engine`, `tires`, `battery`, `fuel_tank`, `suspension`
- `run.car.statuses` — список статусов (v0 может быть пустым): `leak`, `short`, `wobble`, `overheat`...

Примечание:
- Панели/слоты/модули можно добавить позже (M2 CarState v1), но v0 уже держит структуру `parts`.

### 3.4 Inventory (v0)
В GDD целевой вариант — тетрис-инвентарь. На v0 фиксируем **универсальную модель предмета**, чтобы перейти к тетрису без ломки данных.

- `run.inventory` — список предметов в поездке (пока простой список/стэки)

Формат предмета (универсальный):
- `id` — id предмета
- `qty` — количество
- `tags` — теги (опционально)
- `size` — `{w,h}` (для будущего тетриса; на v0 можно держать `1x1`)
- `meta` — произвольные данные (например прочность)

### 3.5 Secure / Loose / Insured
Чтобы поддержать модель провала из GDD:

- `run.loot_loose` — «незакреплённое», рискует потеряться при провале
- `run.loot_secure` — то, что уже «закреплено» (обычно только после возврата в гараж)
- `run.insured_slot` — один «застрахованный» слот (предмет/пакет ресурсов), не теряется при провале
- `run.recovery_beacon_used` — флаг/кол-во, влияющее на сохранение части добычи при провале

В v0 можно упростить:
- держать всё в `run.inventory`, а `loot_loose/secure` использовать только на уровне RESULT (как расчёт)

### 3.6 Контекст текущего сегмента
Чтобы RESULT мог честно показать итоги, не вытаскивая их из «внутренностей сцены»:

- `run.segment.index` — номер сегмента
- `run.segment.kind` — `"travel" | "poi" | "extract" | "hazard" | "exit"`
- `run.segment.node_id` — к какому узлу относится
- `run.segment.poi_id` — если это POI

- `run.segment.delta` — структура итогов (см. ниже)

---

## 4) SegmentDelta (итоги сегмента)

`run.segment.delta` — это данные, которые RESULT показывает и применяет.

Минимальный формат:
- `delta.resources_gained` — `{scrap: +2, fuel: +10, ...}`
- `delta.resources_spent` — `{fuel: -5, ...}`
- `delta.items_gained` — список предметов
- `delta.items_lost` — список предметов (если было)
- `delta.damage` — какие детали/поля пострадали (для UI)
- `delta.flags` — `success`, `evac`, `fail`, `extracted`

Правило:
- **Сцены (DRIVE/POI)** собирают «дельту», но RESULT — место, где она финализируется, отображается и (при необходимости) переносится в MetaState.

---

## 5) Правила мутаций (кто что имеет право менять)

### GARAGE
- создаёт новый `RunState` (seed, region, базовая машина)
- применяет апгрейды/ремонт к `MetaState` и/или `meta.car_garage`

### REGION_MAP
- выбирает следующий `run.node_id`
- может повышать/понижать `run.threat_level` по правилам региона
- не трогает инвентарь и HP напрямую

### DRIVE (mode="travel" / "extract")
- меняет `run.car.*` (fuel/battery/heat/parts/statuses)
- меняет `run.threat_level` (рост напряжения)
- заполняет `run.segment.delta.damage/resources_spent` и флаги success/fail
- в конце:
  - travel: либо отправляет в POI, либо формирует дельту и идёт в RESULT
  - extract: всегда формирует дельту (успех/провал) и идёт в RESULT

### POI_V0
- меняет `run.inventory` и/или `run.segment.delta.items_gained/resources_gained`
- может тратить ресурсы/расходники (через delta.spent)
- по выходу **всегда** готовит `run.segment.delta` и отправляет в DRIVE(mode="extract")

### RESULT
- показывает `run.segment.delta`
- применяет последствия сегмента к RunState (если сцены копили дельту, но не меняли run напрямую)
- при провале/эвакуации:
  - применяет правила потери/сохранения `loose` и insured
  - добавляет штрафы (fuel/scrap) и «поломки после эвакуации» (в терминах delta + car.parts)
- при возврате в гараж:
  - переносит «secure» в `meta.resources_secure` / `meta.inventory_secure`
  - очищает `run.segment.delta`

---

## 6) Контракт переходов DRIVE ↔ POI

Минимальный набор данных, который должен сохраняться между режимами (лежит в RunState):
- `run.seed`, `run.node_id`, `run.threat_level`
- `run.inventory`
- `run.car` (fuel/battery/heat + parts/statuses)
- `run.active_upgrade_id`

Переходы (из архитектуры):
- `DRIVE(travel) → POI_V0 → DRIVE(extract) → RESULT`

---

## 7) Инварианты (чтобы ловить баги рано)

- `run.car.parts` содержит все 6 ключевых деталей.
- `run.seed` не меняется в течение рана.
- `run.segment.delta` либо `None`, либо соответствует текущему сегменту и очищается после RESULT.
- Ни одна сцена не хранит «важный прогресс» только внутри себя: всё важное либо в RunState, либо в SegmentDelta.

---

## 8) Debug overlay (минимум для M1)

Для отладки удобно показывать:
- `seed`, `region_id`, `node_id`, `threat_level`
- `car.fuel`, `car.battery`, `car.heat`
- `parts (body/engine/tires/battery/fuel_tank/suspension)`
- текущая сцена и `DRIVE.mode`

