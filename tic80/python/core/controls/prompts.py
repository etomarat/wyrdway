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
    PAD_UP = 8
    PAD_DOWN = 9
    PAD_LEFT = 10
    PAD_RIGHT = 11
    PAD_DPAD = 12

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
    KEY_BACKSPACE = 30
    KEY_Y = 31
    KEY_B = 32
    KEY_ARROWS = 33
    KEY_F6 = 34

_GLYPH_LABELS = {
    # Keyboard labels.
    PromptGlyph.KEY_UP: "UP",
    PromptGlyph.KEY_DOWN: "DOWN",
    PromptGlyph.KEY_LEFT: "LEFT",
    PromptGlyph.KEY_RIGHT: "RIGHT",
    PromptGlyph.KEY_Z: "Z",
    PromptGlyph.KEY_X: "X",
    PromptGlyph.KEY_A: "A",
    PromptGlyph.KEY_S: "S",
    PromptGlyph.KEY_ENTER: "ENTER",
    PromptGlyph.KEY_SPACE: "SPACE",
    PromptGlyph.KEY_BACKSPACE: "BACKSPACE",
    PromptGlyph.KEY_Y: "Y",
    PromptGlyph.KEY_B: "B",
    PromptGlyph.KEY_ARROWS: "ARROWS",
    PromptGlyph.KEY_F6: "F6",
    # Gamepad positions / shoulders.
    PromptGlyph.PAD_SOUTH: "SOUTH",
    PromptGlyph.PAD_WEST: "WEST",
    PromptGlyph.PAD_EAST: "EAST",
    PromptGlyph.PAD_NORTH: "NORTH",
    PromptGlyph.PAD_RT: "RT",
    PromptGlyph.PAD_LT: "LT",
    PromptGlyph.PAD_RB: "RB",
    PromptGlyph.PAD_LB: "LB",
    PromptGlyph.PAD_UP: "UP",
    PromptGlyph.PAD_DOWN: "DOWN",
    PromptGlyph.PAD_LEFT: "LEFT",
    PromptGlyph.PAD_RIGHT: "RIGHT",
    PromptGlyph.PAD_DPAD: "DPAD"
}

_PAD_SHOULDER_GLYPHS = {
    PromptGlyph.PAD_RT,
    PromptGlyph.PAD_LT,
    PromptGlyph.PAD_RB,
    PromptGlyph.PAD_LB
}


def glyph_label(glyph: int) -> str:
    label = _GLYPH_LABELS.get(int(glyph))
    if label is None:
        return "?"
    return str(label)


def format_prompt(glyphs: list[int], detail: PromptGlyphDetailId) -> str:
    """Formats like '{g:0}/{g:4}/[ENTER]'.

    - Glyphs are emitted as rich tokens for the UI renderer: `{g:<id>}`.
      UI should render those as sprites when available, and fall back to text when not.
    """
    if not glyphs:
        return ""
    show_all = detail != PromptGlyphDetail.PRIMARY_ONLY
    if not show_all:
        glyphs = glyphs[:1]
    parts: list[str] = []
    for g in glyphs:
        parts.append("{g:" + str(int(g)) + "}")
    return "{sep}".join(parts)


def prompt_glyphs_for_action(action: int, device: InputDeviceModeId) -> list[int]:
    """Returns ordered glyphs for UI hints.

    - Order: face -> shoulders (if any) -> keyboard (if device=BOTH)
    - A single action can advertise multiple glyphs for the same underlying btn.
      Example: South and RT can be synonyms in a custom TIC-80 build.
    """
    if action == Action.CONFIRM:
        pad = [PromptGlyph.PAD_SOUTH, PromptGlyph.PAD_RT]
        key = [PromptGlyph.KEY_ENTER, PromptGlyph.KEY_Z]
        return _select_device(device, pad, key)

    if action == Action.CANCEL:
        pad = [PromptGlyph.PAD_EAST, PromptGlyph.PAD_LT]
        key = [PromptGlyph.KEY_BACKSPACE, PromptGlyph.KEY_X]
        return _select_device(device, pad, key)

    if action == Action.SECONDARY:
        pad = [PromptGlyph.PAD_WEST, PromptGlyph.PAD_LB]
        key = [PromptGlyph.KEY_A]
        return _select_device(device, pad, key)

    if action == Action.HELP:
        pad = [PromptGlyph.PAD_NORTH, PromptGlyph.PAD_RB]
        key = [PromptGlyph.KEY_S]
        return _select_device(device, pad, key)

    if action == Action.NAV_UP:
        return _select_device(device, [PromptGlyph.PAD_UP], [PromptGlyph.KEY_UP])
    if action == Action.NAV_DOWN:
        return _select_device(device, [PromptGlyph.PAD_DOWN], [PromptGlyph.KEY_DOWN])
    if action == Action.NAV_LEFT:
        return _select_device(device, [PromptGlyph.PAD_LEFT], [PromptGlyph.KEY_LEFT])
    if action == Action.NAV_RIGHT:
        return _select_device(device, [PromptGlyph.PAD_RIGHT], [PromptGlyph.KEY_RIGHT])

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
        key = [PromptGlyph.KEY_SPACE, PromptGlyph.KEY_X]
        return _select_device(device, pad, key)

    if action == Action.SKILL:
        pad = [PromptGlyph.PAD_NORTH, PromptGlyph.PAD_RB]
        key = [PromptGlyph.KEY_Z]
        return _select_device(device, pad, key)

    return []


def prompt_glyphs_for_nav_hint(device: InputDeviceModeId) -> list[int]:
    """Compact movement hint: dpad icon and arrow-cluster icon."""
    return _select_device(device, [PromptGlyph.PAD_DPAD], [PromptGlyph.KEY_ARROWS])


def _select_device(device: InputDeviceModeId, pad: list[int], key: list[int]) -> list[int]:
    if device == InputDeviceMode.GAMEPAD:
        return list(pad)
    if device == InputDeviceMode.KEYBOARD:
        return list(key)
    if device == InputDeviceMode.BOTH:
        # In BOTH mode we only show primary controls for each device.
        out: list[int] = []
        # Keyboard first so "both" reads naturally on PC.
        if len(key) > 0:
            out.append(key[0])
        if len(pad) > 0:
            out.append(pad[0])
        return out
    return list(pad)


def _glyph_is_keyboard(glyph: int) -> bool:
    return glyph >= PromptGlyph.KEY_UP


def filter_prompt_glyphs(glyphs: list[int], show_shoulders: bool) -> list[int]:
    if show_shoulders:
        return list(glyphs)
    out: list[int] = []
    for g in glyphs:
        if _glyph_is_pad_shoulder(g):
            continue
        out.append(g)
    return out


def _glyph_is_pad_shoulder(glyph: int) -> bool:
    return int(glyph) in _PAD_SHOULDER_GLYPHS
