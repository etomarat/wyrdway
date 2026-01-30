# Wyrdway
Wyrdway — a content-driven road-trip roguelite game for TIC-80: drive between strange POIs, do quick loot raids, extract, and upgrade your car in the garage to survive escalating anomalies.

## Repo layout
- `tic80/python/main.py` — game entry point (Python TIC-80).
- `tic80/python/game.py` — TIC-80 cart resources (sprites/sfx/etc); avoid editing directly.
- `tic80/python/build.py` — bundler output; do not edit.
- `docs/` — design and architecture references.

## Run & build (Windows)
- `run_tic80_python.bat` — bundle `game.py` + `main.py` and launch TIC-80.
- `run_tic80_python.bat build` — bundle only (no emulator).
