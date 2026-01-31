# Content Tables Spec (Wyrdway / TIC-80 Python)

## Цели
- Контент задаётся данными (таблицами), код читает таблицы и исполняет правила.
- Все записи имеют стабильные `id` и валидируются при загрузке (fail-fast).
- Таблицы расширяемы: добавление нового врага/POI/апгрейда не требует правок логики (кроме добавления новых обработчиков эффектов).

## Общие соглашения

### ID и нейминг
- `id`: строка в `snake_case`, уникальна внутри своей таблицы.
- Ключи полей: `snake_case`.
- `tags`: список строк, например: `["anomaly", "electrical"]`.

### Время
- Все значения времени в данных задаются в **секундах** (для читаемости и будущей переносимости).
- На загрузке/валидации они конвертируются в тики текущего рантайма (для TIC-80 это 60 FPS).
  - Пример: `timer_s = 15` → `timer_t = 900`.

### Регионы и биомы
- Любой `spawn` может включать `biomes: ["plains", "marsh"]` (строки).
- На M1 можно использовать строки без отдельной таблицы регионов.
- Когда появится генерация регионов — добавляется `REGIONS/BIOMES`, и валидатор начнёт проверять ссылки.

### Версионирование
- В `data/content.py` хранится `CONTENT_VERSION = 1`.
- Ломающие изменения схемы: увеличиваем `CONTENT_VERSION` и обновляем загрузчик/валидатор.

### Валидация
На старте (или при входе в гараж) выполняется:
- проверка обязательных полей,
- проверка типов/диапазонов,
- проверка ссылок (`loot_table_id`, `upgrade_id`, `enemy_id`, `hazard_id`),
- проверка уникальности `id`.

---

## Таблицы

### 1) ENEMIES
Враги:
- `drone` / `turret` (глушатся/иногда уничтожаются)
- `chaser` (погоня, ключевой pressure)

#### Схема
**Обязательные поля:**
- `id: str`
- `kind: str` — `"drone" | "turret" | "chaser"`
- `name: str` — отображаемое имя (или ключ локализации)
- `tags: list[str]`
- `tier: int` — `1..5`
- `spawn: dict` — правила появления

**Опциональные поля:**
- `stats: dict`
- `behavior: dict`
- `loot_table_id: str | None`
- `jam_rules: dict | None`
- `audio: dict | None`
- `fx: dict | None`

`spawn`:
- `contexts: list[str]` — `"drive" | "poi" | "extract"`
- `weight: int` — относительный вес
- `min_threat: int` — `0..100`
- `max_threat: int` — `0..100`
- `biomes: list[str] | None`

**Пример:**
```python
ENEMIES = [
  {
    "id": "spark_drone",
    "kind": "drone",
    "name": "Spark Drone",
    "tags": ["electrical", "scout"],
    "tier": 2,
    "spawn": {"contexts": ["poi"], "weight": 40, "min_threat": 10, "max_threat": 70},
    "stats": {"hp": 3, "speed": 0.9, "range": 5},
    "jam_rules": {"can_jam": True, "jam_time_s": 2.0, "jam_cooldown_s": 5.0},
    "loot_table_id": "lt_drone_basic"
  }
]
```

**Нормы (валидация по `kind`):**
- `turret`: требует `range` и `fire_rate`.
- `chaser`: требует `speed` и параметр давления (например `pressure` или `threat_push`).

---

### 2) HAZARDS
Hazards — это **системы** (туман, статические поля, магнитные зоны, глюки интерфейса, отказ электроники и т.п.).

#### Схема
**Обязательные:**
- `id: str`
- `name: str`
- `tags: list[str]`
- `tier: int` — `1..5`
- `effect_id: str` — идентификатор обработчика эффекта в коде
- `params: dict` — параметры эффекта
- `spawn: dict` — `contexts/weight/threat/biomes`

**Пример:**
```python
HAZARDS = [
  {
    "id": "fog_static",
    "name": "Static Fog",
    "tags": ["anomaly", "visibility"],
    "tier": 1,
    "effect_id": "effect_fog",
    "params": {"density": 0.6, "noise": 0.3},
    "spawn": {"contexts": ["drive"], "weight": 60, "min_threat": 0, "max_threat": 40}
  }
]
```

---

### 3) POIS
POI — «короткая вылазка» с лутом, риском и таймером.

#### Схема
**Обязательные:**
- `id: str`
- `name: str`
- `tags: list[str]`
- `tier: int` — `1..5`
- `layout_id: str` — какой шаблон/генератор использовать
- `encounters: list[dict]`
- `rewards: list[dict]`
- `rules: dict`

`encounters[]`:
- `type: str` — `"enemy" | "hazard" | "event"`
- `ref_id: str` — `enemy_id / hazard_id / event_id`
- `weight: int`
- `count: int | (min,max)`

`rewards[]`:
- `type: str` — `"loot_table" | "item" | "upgrade"`
- `ref_id: str`
- `rolls: int` — только для `loot_table`

`rules` (минимум):
- `timer_s: number`
- `extract_after_s: number`
- `threat_gain: int`

**Пример:**
```python
POIS = [
  {
    "id": "poi_abandoned_gas",
    "name": "Abandoned Gas Station",
    "tags": ["industrial", "fuel"],
    "tier": 1,
    "layout_id": "layout_small_rect",
    "encounters": [
      {"type": "enemy", "ref_id": "spark_drone", "weight": 60, "count": (0, 2)},
      {"type": "hazard", "ref_id": "fog_static", "weight": 40, "count": 1}
    ],
    "rewards": [
      {"type": "loot_table", "ref_id": "lt_poi_gas_small", "rolls": 2}
    ],
    "rules": {"timer_s": 15.0, "extract_after_s": 5.0, "threat_gain": 10}
  }
]
```

---

### 4) UPGRADES
Апгрейды машины/гаража. Эффекты задаются данными и исполняются обработчиками.

#### Схема
**Обязательные:**
- `id: str`
- `name: str`
- `slot: str` — `"engine" | "tires" | "battery" | "scanner" | "cargo" | "garage"`
- `rarity: str` — `"common" | "uncommon" | "rare" | "epic"`
- `cost: dict` — например `{ "scrap": 20 }`
- `effects: list[dict]`
- `tags: list[str]`

`effects[]`:
- `effect_id: str` — например `"+cargo_slots"`, `"resist:electrical"`
- `value: number | dict`

**Пример:**
```python
UPGRADES = [
  {
    "id": "upg_cargo_rack_1",
    "name": "Cargo Rack I",
    "slot": "cargo",
    "rarity": "common",
    "cost": {"scrap": 25},
    "tags": ["cargo"],
    "effects": [
      {"effect_id": "+cargo_slots", "value": 2}
    ]
  }
]
```

---

### 5) LOOT_TABLES
Используется для POI rewards, drops, наград гаража.

#### Схема
**Обязательные:**
- `id: str`
- `rolls: int`
- `entries: list[dict]`

`entries[]`:
- `type: str` — `"item" | "upgrade" | "currency" | "table"`
- `ref_id: str`
- `weight: int`
- `qty: int | (min,max)`
- `chance: float | None` — `0..1`
- `conditions: dict | None`

**Пример:**
```python
LOOT_TABLES = [
  {
    "id": "lt_poi_gas_small",
    "rolls": 1,
    "entries": [
      {"type": "currency", "ref_id": "scrap", "weight": 80, "qty": (5, 15)},
      {"type": "item", "ref_id": "fuel_can_small", "weight": 50, "qty": 1},
      {"type": "upgrade", "ref_id": "upg_cargo_rack_1", "weight": 10, "qty": 1},
      {"type": "table", "ref_id": "lt_misc_junk", "weight": 60, "qty": 1}
    ]
  }
]
```

---

## Рекомендуемая структура файлов
- `data/content.py`
  - `CONTENT_VERSION`
  - `ENEMIES, HAZARDS, POIS, UPGRADES, LOOT_TABLES`
- `data/loader.py`
  - `load_content() -> ContentDB`
  - `validate_content(db)`
  - `compile_time_fields(db)` (конверсия `*_s → *_t`)
- `systems/loot.py`
  - `roll_loot(table_id, ctx) -> list[Reward]`
