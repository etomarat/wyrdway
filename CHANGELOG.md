# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]

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

## [0.0.1] - 2026-02-26

### Added
- First public pre-alpha build.
- Public itch.io page and first devlog post.
- Core playable loop with garage, route selection, drive, POI and result flow.
