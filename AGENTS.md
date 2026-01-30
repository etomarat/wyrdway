# Repository Guidelines

## Project Structure & Module Organization
- `tic80/python/` holds the active Python cartridge sources (`main.py`, `game.py`) plus `stubs/` for TIC-80 typing support.
- `tic80/lua/` contains a Lua cartridge prototype (`main.lua`) for reference only unless explicitly requested.
- `pyxel/` is a placeholder sandbox and should not be used unless explicitly requested.
- `docs/` captures design and architecture references (expect this area to grow over time).
- `run_tic80_python.bat` is the primary local run/build helper on Windows.

## Build, Test, and Development Commands
- `run_tic80_python.bat` bundles `tic80/python/game.py` into `tic80/python/main.py` and launches TIC-80.
- `run_tic80_python.bat build` bundles only (no emulator launch).
- `pyright` (if installed) runs static type checks based on `pyrightconfig.json`.

## Coding Style & Naming Conventions
- Default language is Python for TIC-80. Do not switch languages or runtimes unless explicitly directed.
- Python files use 4-space indentation; Lua prototype uses tabs in `tic80/lua/main.lua` if touched.
- Keep TIC-80 entry points named `TIC()` (Python) or `TIC` (Lua).
- No formatter or linter is configured yet; keep diffs tidy and consistent with surrounding code.

## TIC-80 Python Import/Bundling Rules
- TIC-80 Python does not support normal imports; we bundle everything into `main.py`.
- Use `tq-bundler` via `run_tic80_python.bat` to resolve imports and emit a single cart.
- In code, do imports in two layers (see `tic80/python/main.py`):
  - Real runtime dependencies are pulled with `include("module")` for the bundler/TIC-80.
  - Editor-only imports go under `if TYPE_CHECKING:` so Pyright/IDE can resolve types without breaking runtime.
```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import *
    from .test import *

include("test")
```

## Testing Guidelines
- There is no automated test suite yet. Validate changes by running the cart in TIC-80 and exercising the affected scene or mechanic.
- If you introduce tests, document the framework and commands here and keep tests near the code they cover (e.g., `tic80/python/*_test.py`).

## Commit & Pull Request Guidelines
- Recent commits use short, lower-case summaries (e.g., “add tic80 bundler support and stubs”). Keep messages concise and action-oriented.
- PRs should include: a short description of gameplay or tooling changes, how you tested (command + outcome), and screenshots or GIFs for visual changes.

## Architecture Notes
- Scene flow and ownership rules live in `docs/2_architecture.md`. Follow the “Replace SceneManager” rule: only one scene updates/draws at a time.
