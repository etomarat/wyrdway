# Refactor Backlog

## Done (high priority)

- [x] Remove menu preview dependency on temporary global `TUNING.DRIVE` mutations.
- [x] Replace direct private `DriveLogic` field writes in menu preview with a public API.

## Pending (medium/low priority)

- [ ] Split `MainMenuScene` into focused components:
  - menu list/input
  - entity-watch overlay
  - modal overlays
- [ ] Move overlay static text arrays (`controls/credits/confirm`) to class-level constants to reduce per-frame allocations.
- [ ] Extract common panel frame drawing helper to avoid duplicated border/layout code.
- [ ] Unify local menu RNG helpers into one reusable utility.
