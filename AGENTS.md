# Repository Guidelines

## Project Structure & Module Organization
- `tic80/python/` holds the active Python cartridge sources (`main.py`, `game.py`) plus `stubs/` for TIC-80 typing support.
- `tic80/lua/` contains a Lua cartridge prototype (`main.lua`) for reference only unless explicitly requested.
- `pyxel/` is a placeholder sandbox and should not be used unless explicitly requested.
- `docs/` captures design and architecture references (expect this area to grow over time).
- `run_tic80_python.bat` is the primary local run/build helper on Windows.
  - `tic80/python/main.py` is the game entry point.
  - `tic80/python/game.py` is the TIC-80 cart resource file (sprites/sfx/etc). Avoid editing directly unless explicitly requested.
  - `tic80/python/build.py` is the bundler output (main + game); do not edit.

## Build, Test, and Development Commands
- `run_tic80_python.bat` bundles `tic80/python/game.py` into `tic80/python/main.py` and launches TIC-80.
- `run_tic80_python.bat build` bundles only (no emulator launch).
- `pyright` (if installed) runs static type checks based on `pyrightconfig.json`.

## Coding Style & Naming Conventions
- Default language is Python for TIC-80. Do not switch languages or runtimes unless explicitly directed.
- Python files use 4-space indentation; Lua prototype uses tabs in `tic80/lua/main.lua` if touched.
- Keep TIC-80 entry points named `TIC()` (Python) or `TIC` (Lua).
- No formatter or linter is configured yet; keep diffs tidy and consistent with surrounding code.
- Prefer **classes over ad-hoc globals** for game state and behavior. Use small, focused classes (e.g. scenes, data carriers) instead of spreading logic across module-level functions and global variables.
- Avoid introducing new mutable module-level state where possible. Prefer passing state explicitly or encapsulating it in objects owned by a clear root (e.g. `SceneManager`, `RunState`).
- Aim for typed code in editor: define shared contracts and shared types in `tic80/python/contracts.py` and import them under `if TYPE_CHECKING:`.
- Do not use string annotations or `from __future__ import annotations`. Type-only imports (e.g., protocol or TypedDict definitions) go under `if TYPE_CHECKING:` for editor/pyright support.

## TIC-80 Python Import/Bundling Rules
- TIC-80 Python does not support normal imports; we bundle everything into `main.py`.
- Use `tq-bundler` via `run_tic80_python.bat` to resolve imports and emit a single cart.
- In code, do imports in two layers (see `tic80/python/main.py`):
  - Real runtime dependencies are pulled with `include("module")` for the bundler/TIC-80. Use dot paths (e.g. `include("data.tuning")`), not slashes.
  - Editor-only imports go under `if TYPE_CHECKING:` so Pyright/IDE can resolve types without breaking runtime.
- Shared **types that are only used for static typing** (e.g. `TypedDict`, `Protocol`, aliases) live in `tic80/python/contracts.py` and are imported under `if TYPE_CHECKING:`. They do **not** require `include("contracts")` at runtime.
- Small **runtime data/contract classes** that must exist as values (for example, scene parameter objects like `DriveEnterParams` or `ResultEnterParams`) may also live in `tic80/python/contracts.py`, but in that case `tic80/python/main.py` must call `include("contracts")` so these classes are available in the bundled cart.
- TIC-80 Python ships with a restricted `typing` module. Do not rely on `typing.NamedTuple` at runtime; when you need simple data carriers, prefer regular classes with annotated fields (optionally with `__slots__`) instead.
- Python files that touch the TIC-80 API should start with a TIC-80 typing shim; using `from tic80 import *` under `if TYPE_CHECKING` is allowed, and Pyright will load TIC-80 stubs from `tic80.pyi`.
```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import *
```
```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import *
    from .test import msg

include("test")
```

## Testing Guidelines
- There is no automated test suite yet. Validate changes by running the cart in TIC-80 and exercising the affected scene or mechanic.
- If you introduce tests, document the framework and commands here and keep tests near the code they cover (e.g., `tic80/python/*_test.py`).

## Commit & Pull Request Guidelines
- Recent commits use short, lower-case summaries (e.g., “add tic80 bundler support and stubs”). Keep messages concise and action-oriented.
- After each successful iteration, provide a suggested commit message.
- PRs should include: a short description of gameplay or tooling changes, how you tested (command + outcome), and screenshots or GIFs for visual changes.

## Architecture Notes
- Scene flow and ownership rules live in `docs/2_architecture.md`. Follow the “Replace SceneManager” rule: only one scene updates/draws at a time.
- TIC-80 API docs live in `docs/tic80_api_reference.md` (short reference) and `docs/TIC-80.wiki` (full wiki clone). Use them to clarify API details when needed.
