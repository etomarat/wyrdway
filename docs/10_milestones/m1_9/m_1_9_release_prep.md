# M1.9 release prep draft

Дата последнего обновления: 2026-03-15

Кандидат версии на сейчас: `0.0.2 alpha`

## Source range

- Base tag: `v0.0.1`
- Base commit: `3c35f7bcf785ea0b0f5a95b3c3c7e4474591e18e`
- Previous freeze head: `159886044061dc295f6579211e9c680d089b524f`
- Previous freeze subject: `fx: add post-finish slide and finish burst`
- Current draft range: `v0.0.1..6f1a911`
- Current head: `6f1a911fe1ad3c5859489086a6129bef695e7fb4`
- Current head subject: `ui: prototype turn shoulder line accents and keep road edge experiments`

Примечание: этот файл фиксирует исходную точку для релизных заметок. Если до тега появятся новые player-facing изменения, их нужно добавить и сюда, и в `CHANGELOG.md`.

## New commits since previous freeze

- `6f1a911` `ui: prototype turn shoulder line accents and keep road edge experiments`
- `57310ef` `ui: add garage back action on region map`
- `cccb802` `feat: add new game intro popup sequence`
- `7f41fb3` `fix: preserve vibration state across gamepad reconnects`
- `3990339` `fx: add and refine finish gate, sparks, and fading road tails`

## Draft release angle

Это промежуточный player-facing апдейт без нового gameplay milestone.
Основной фокус:

- UI/UX pass по меню и overlay-экранам
- campaign/setup/options polish
- gamepad, rumble, haptics, input prompts
- drive feedback и финишные FX

## Draft changelog

### Added

- New main menu scene with drive preview and entity watch polish.
- New campaign setup with seed editor and run-index saves.
- New game intro popup sequence.
- Global options persistence, difficulty setting, and saved input toggles.
- Rumble and haptics support, plus controller and mouse-aware options flow.
- Sprite-based control prompts, including an `F6` glyph for the CRT toggle.
- Region map now has a garage back action.

### Changed

- Unified overlay UI/runtime across the main menu, garage, result, POI, and region map screens.
- Reworked garage action rows, footer actions, modal layouts, and controls legends for more consistent navigation.
- Improved drive feedback with stronger haptics, burnout tuning, high-speed skid mark gating, and HUD/control hint polish.
- Added post-finish slide and finish burst FX to make run endings feel more readable and punchy.
- Added and refined finish gate FX, sparks, fading road tails, and shoulder line accents during turns.
- Refined setup/options labels and continue info, including campaign seed visibility in the main menu.

### Fixed

- Isolated layered UI input state across scenes so modal input no longer leaks between screens.
- Continue now resumes in the garage correctly and saves the profile on menu exit.
- Re-enabled the minified watch flow in dev mode.
- Vibration state now survives gamepad reconnects.

## Commit groups worth revisiting before publish

- `6f1a911` `ui: prototype turn shoulder line accents and keep road edge experiments`
- `57310ef` `ui: add garage back action on region map`
- `cccb802` `feat: add new game intro popup sequence`
- `7f41fb3` `fix: preserve vibration state across gamepad reconnects`
- `3990339` `fx: add and refine finish gate, sparks, and fading road tails`
- `1598860` `fx: add post-finish slide and finish burst`
- `9263333` `feat: improve drive feedback and unify ui haptics`
- `b713ff1` `feat: add drift rumble, extend burnout, and gate skid marks at high speed`
- `6baf405` `feat: add rumble+haptics, persist input toggles, and mouse controls in options/new game`
- `782aa39` `feat: add new campaign setup with seed editor and run-index saves`
- `434ab09` `feat: persist global options and add difficulty in options menu`
- `f7556dc` `feat: add main menu scene with drive preview and entity watch polish`
- `6b348ce` `fix: isolate layered ui input state across scenes`
- `cf8c822` `fix: continue resumes in garage and saves profile on menu exit`
