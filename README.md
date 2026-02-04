![Wyrdway Logo](poster.png)

# Wyrdway
Wyrdway — a content-driven road-trip roguelite game for [TIC-80 fantasy computer](https://tic80.com/): drive between strange POIs, do quick loot raids, extract, and upgrade your car in the garage to survive escalating anomalies.

## Gameplay record (early WIP)
![Wyrdway Logo](last_gameplay.gif)

## Game Design Document (lang: RU)
- [gdd_v0.md](docs/00_spec/0_gdd_v0.md) — early proto

## Repo layout
- `tic80/python/main.py` — game entry point (Python TIC-80).
- `tic80/python/game.py` — TIC-80 cart resources (sprites/sfx/etc); avoid editing directly.
- `tic80/python/build.py` — bundler output; do not edit.
- `docs/` — design and architecture references.

## Run & build (Windows)
- `run_tic80_python.bat` — bundle `game.py` + `main.py` and launch TIC-80.
- `run_tic80_python.bat build` — bundle only (no emulator).
- `run_tic80_python.bat dist` — bundle + make a “safe” export build and write outputs into `tic80/python/dist/`:
  - Note: `dist/` is cleared on each run to avoid stale export artifacts.
  - `tic80/python/dist/build.py` — postprocessed code (no typing / TYPE_CHECKING / annotations).
  - `tic80/python/dist/wyrdway.tic` — full cart (resources from `game.py` + safe code).
  - `tic80/python/dist/wyrdway_html*` — HTML export (TIC-80 generates a set of files with this base name).
  - `tic80/python/dist/wyrdway_win*` — Windows export (TIC-80 generates platform artifacts with this base name).

---

# Wyrdway

Wyrdway — контент‑ориентированный road‑trip roguelite для [фэнтези‑компьютера TIC‑80](https://tic80.com/): путешествуйте между странными точками интереса, делайте короткие вылазки за лутом, эвакуируйтесь и улучшайте машину в гараже, чтобы пережить нарастающие аномалии.

## Дизайн-документ

* [gdd_v0.md](docs/00_spec/0_gdd_v0.md) — ранний прототип

## Запуск и сборка (Windows)

* `run_tic80_python.bat` — собрать `game.py` + `main.py` и запустить TIC‑80.
* `run_tic80_python.bat build` — только сборка (без запуска).
* `run_tic80_python.bat dist` — сборка + “безопасный” билд для экспорта; все выходные файлы попадают в `tic80/python/dist/`:
  * Примечание: папка `dist/` очищается при каждом запуске, чтобы не было старых артефактов экспорта.
  * `tic80/python/dist/build.py` — постпроцессированный код (без typing/TYPE_CHECKING/аннотаций).
  * `tic80/python/dist/wyrdway.tic` — полный картридж (ресурсы из `game.py` + safe‑код).
  * `tic80/python/dist/wyrdway_html*` — HTML экспорт (TIC‑80 создаёт набор файлов с этим базовым именем).
  * `tic80/python/dist/wyrdway_win*` — Windows экспорт (TIC‑80 создаёт артефакт(ы) с этим базовым именем).
