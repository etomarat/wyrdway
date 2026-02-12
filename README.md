![Wyrdway Logo](poster.png)

# Wyrdway
Wyrdway — a content-driven road-trip roguelite game for [TIC-80 fantasy computer](https://tic80.com/): drive between strange POIs, do quick loot raids, extract, and upgrade your car in the garage to survive escalating anomalies.

## Play (latest updatable WIP)
- [https://etomarat.github.io/wyrdway/](https://etomarat.github.io/wyrdway/)

## Gameplay record (early WIP)
![Wyrdway Logo](last_gameplay.gif)

## Game Design Document (lang: RU)
- [gdd_v0.md](docs/00_spec/0_gdd_v0.md) — early proto

## Repo layout
- `tic80/python/main.py` — game entry point (Python TIC-80).
- `tic80/python/game.py` — TIC-80 cart resources (sprites/sfx/etc); avoid editing directly.
- `tic80/python/build.py` — bundler output; do not edit.
- `tic80/python/build.min.py` — minified bundler output; do not edit.
- `scripts/minify_tic80_build.py` — bundle minifier (strips comments/TYPE_CHECKING, compresses indentation).
- `docs/` — design and architecture references.

## Third-party particles
Some particle FX were ported from TIC-80 community carts (Lua → Python/PocketPy). Thanks to the original authors:
- `vand` — “vand particles pack” (source: https://tic80.com/play?cart=1983)
- `Viza` — “pslib” (source: https://tic80.com/play?cart=85)

Attribution + file mapping lives in `docs/80_misc/third_party_particles.md`

## Run & build (Windows)
- `run_tic80_python.bat dev` — **development**: bundle and launch TIC-80 without minification (best for fast iteration / readable code / “live” tweaking).
- `run_tic80_python.bat` — bundle + **minify** + launch TIC-80 using `build.min.py`.
- `run_tic80_python.bat build` — bundle + minify only (no emulator).
- `run_tic80_python.bat dist` — bundle + minify + export to `dist/` (`wyrdway.tic`, `wyrdway.exe`, `wyrdway.zip`, `wyrdway-linux.zip`, `wyrdway-mac.zip`).

---

# Wyrdway

Wyrdway — контент‑ориентированный road‑trip roguelite для [фэнтези‑компьютера TIC‑80](https://tic80.com/): путешествуйте между странными точками интереса, делайте короткие вылазки за лутом, эвакуируйтесь и улучшайте машину в гараже, чтобы пережить нарастающие аномалии.

## Играть (последняя рабочая версия)
- [https://etomarat.github.io/wyrdway/](https://etomarat.github.io/wyrdway/)

## Дизайн-документ

* [gdd_v0.md](docs/00_spec/0_gdd_v0.md) — ранний прототип

## Частицы от сообщества TIC-80 (vendor)
Мы портировали часть эффектов частиц из картриджей сообщества TIC-80 (Lua → Python/PocketPy). Спасибо авторам:
- `vand` — “vand particles pack” (source: https://tic80.com/play?cart=1983)
- `Viza` — “pslib” (source: https://tic80.com/play?cart=85)

Атрибуция и соответствие файлов хранится в `docs/80_misc/third_party_particles.md` (в бандле/минификации исходные комментарии теряются).

## Сборка (Windows)
- `run_tic80_python.bat dev` — **разработка**: сборка и запуск TIC-80 без минификации (лучше для быстрой итерации / читаемого кода).
- `run_tic80_python.bat` — сборка + **минификация** + запуск TIC-80 через `build.min.py`.
- `run_tic80_python.bat build` — сборка + минификация (без эмулятора).
- `run_tic80_python.bat dist` — сборка + минификация + экспорт в `dist/` (`wyrdway.tic`, `wyrdway.exe`, `wyrdway.zip`, `wyrdway-linux.zip`, `wyrdway-mac.zip`).

## Заметки по тюнингу
- Тюнинг DRIVE FX — в `tic80/python/data/tuning/drive/fx.py`.
- Искры на границе оффроуда масштабируются по скорости параметрами:
  - `TUNING.DRIVE.fx_transition_sparks_min_speed`
  - `TUNING.DRIVE.fx_transition_sparks_ramp_speed`
