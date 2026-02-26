from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .actions import Action
    from .modes import (
        InputDeviceMode,
        InputDeviceModeId,
        PromptGlyphDetail,
        PromptGlyphDetailId
    )


class PromptGlyph:
    # Gamepad positions (preferred for icons because letters vary by controller)
    PAD_SOUTH = 0
    PAD_WEST = 1
    PAD_EAST = 2
    PAD_NORTH = 3

    # Optional synonyms (custom TIC-80 build maps these to the same btn ids)
    PAD_RT = 4
    PAD_LT = 5
    PAD_RB = 6
    PAD_LB = 7

    # Keyboard labels (text fallback)
    KEY_UP = 20
    KEY_DOWN = 21
    KEY_LEFT = 22
    KEY_RIGHT = 23
    KEY_Z = 24
    KEY_X = 25
    KEY_A = 26
    KEY_S = 27
    KEY_ENTER = 28
    KEY_SPACE = 29


def glyph_label(glyph: int) -> str:
    # Keyboard labels.
    if glyph == PromptGlyph.KEY_UP:
        return "UP"
    if glyph == PromptGlyph.KEY_DOWN:
        return "DOWN"
    if glyph == PromptGlyph.KEY_LEFT:
        return "LEFT"
    if glyph == PromptGlyph.KEY_RIGHT:
        return "RIGHT"
    if glyph == PromptGlyph.KEY_Z:
        return "Z"
    if glyph == PromptGlyph.KEY_X:
        return "X"
    if glyph == PromptGlyph.KEY_A:
        return "A"
    if glyph == PromptGlyph.KEY_S:
        return "S"
    if glyph == PromptGlyph.KEY_ENTER:
        return "ENTER"
    if glyph == PromptGlyph.KEY_SPACE:
        return "SPACE"

    # Gamepad positions / shoulders.
    if glyph == PromptGlyph.PAD_SOUTH:
        return "SOUTH"
    if glyph == PromptGlyph.PAD_WEST:
        return "WEST"
    if glyph == PromptGlyph.PAD_EAST:
        return "EAST"
    if glyph == PromptGlyph.PAD_NORTH:
        return "NORTH"
    if glyph == PromptGlyph.PAD_RT:
        return "RT"
    if glyph == PromptGlyph.PAD_LT:
        return "LT"
    if glyph == PromptGlyph.PAD_RB:
        return "RB"
    if glyph == PromptGlyph.PAD_LB:
        return "LB"

    return "?"


def format_prompt(glyphs: list[int], detail: PromptGlyphDetailId) -> str:
    """Formats like '[SOUTH]/[RT]/[Z]'. Uses text fallback only."""
    if not glyphs:
        return ""
    show_all = detail != PromptGlyphDetail.PRIMARY_ONLY
    if not show_all:
        glyphs = glyphs[:1]
    parts: list[str] = []
    for g in glyphs:
        parts.append("[" + glyph_label(g) + "]")
    return "/".join(parts)


def prompt_glyphs_for_action(action: int, device: InputDeviceModeId) -> list[int]:
    """Returns ordered glyphs for UI hints.

    - Order: face -> shoulders (if any) -> keyboard (if device=BOTH)
    - A single action can advertise multiple glyphs for the same underlying btn.
      Example: South and RT can be synonyms in a custom TIC-80 build.
    """
    if action == Action.CONFIRM:
        pad = [PromptGlyph.PAD_SOUTH, PromptGlyph.PAD_RT]
        key = [PromptGlyph.KEY_Z]
        return _select_device(device, pad, key)

    if action == Action.CANCEL:
        pad = [PromptGlyph.PAD_EAST, PromptGlyph.PAD_LT]
        key = [PromptGlyph.KEY_X]
        return _select_device(device, pad, key)

    if action == Action.NAV_UP:
        return [PromptGlyph.KEY_UP]
    if action == Action.NAV_DOWN:
        return [PromptGlyph.KEY_DOWN]
    if action == Action.NAV_LEFT:
        return [PromptGlyph.KEY_LEFT]
    if action == Action.NAV_RIGHT:
        return [PromptGlyph.KEY_RIGHT]

    if action == Action.THROTTLE:
        pad = [PromptGlyph.PAD_SOUTH, PromptGlyph.PAD_RT]
        key = [PromptGlyph.KEY_UP]
        return _select_device(device, pad, key)

    if action == Action.BRAKE:
        pad = [PromptGlyph.PAD_EAST, PromptGlyph.PAD_LT]
        key = [PromptGlyph.KEY_DOWN]
        return _select_device(device, pad, key)

    if action == Action.HANDBRAKE:
        pad = [PromptGlyph.PAD_WEST, PromptGlyph.PAD_LB]
        key = [PromptGlyph.KEY_X]
        return _select_device(device, pad, key)

    if action == Action.SKILL:
        pad = [PromptGlyph.PAD_NORTH, PromptGlyph.PAD_RB]
        key = [PromptGlyph.KEY_Z]
        return _select_device(device, pad, key)

    return []


def _select_device(device: InputDeviceModeId, pad: list[int], key: list[int]) -> list[int]:
    if device == InputDeviceMode.GAMEPAD:
        return list(pad)
    if device == InputDeviceMode.KEYBOARD:
        return list(key)
    if device == InputDeviceMode.BOTH:
        return list(pad) + list(key)
    return list(pad)
