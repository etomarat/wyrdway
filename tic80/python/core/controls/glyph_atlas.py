from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .prompts import PromptGlyph


# Prompt glyph sprites live right of the car sprites in the second sprite bank.
#
# Car block (3x4) starts at `spr=256` (see `drive_topdown_renderer._CAR_SPRITE_BASE_ID`).
# Prompts start immediately to the right at `spr=259` and span 13 columns x 2 rows.
#
# Order in the editor (13x2, 8x8 each):
# Row 0 (spr 259..271):
# - face:   south, west, north, east
# - dpad:   center, up, right, left, down
# - pad:    RT, LT, RB, LB
# Row 1 (spr 275..287):
# - keys:   SPACE, ENTER, BACKSPACE, UP, RIGHT, DOWN, LEFT, Z, X, A, S, Y, B
#
# Extra:
# - `spr=291` (row below the atlas, first column) is a compact "ARROWS" icon.
# - `spr=292` (same row, next column) is an "F6" key icon.

PROMPT_GLYPH_SPR_BASE = 259
PROMPT_GLYPH_SPR_ROW_STRIDE = 16

_ROW0_GLYPH_OFFSET = {
    # Face buttons.
    0: 0,
    1: 1,
    2: 3,
    3: 2,
    # Shoulders.
    4: 9,
    5: 10,
    6: 11,
    7: 12,
    # D-pad.
    8: 5,
    9: 8,
    10: 7,
    11: 6,
    12: 4
}

_ROW1_GLYPH_OFFSET = {
    20: 3,   # KEY_UP
    21: 5,   # KEY_DOWN
    22: 6,   # KEY_LEFT
    23: 4,   # KEY_RIGHT
    24: 7,   # KEY_Z
    25: 8,   # KEY_X
    26: 9,   # KEY_A
    27: 10,  # KEY_S
    28: 1,   # KEY_ENTER
    29: 0,   # KEY_SPACE
    30: 2,   # KEY_BACKSPACE
    31: 11,  # KEY_Y
    32: 12   # KEY_B
}

_GLYPH_ARROWS = 33
_GLYPH_F6 = 34


def prompt_glyph_sprite_id(glyph: int) -> int:
    """Maps PromptGlyph id -> sprite id, or -1 if not available."""
    g = int(glyph)
    base = int(PROMPT_GLYPH_SPR_BASE)
    row1 = base + int(PROMPT_GLYPH_SPR_ROW_STRIDE)

    row0_offset = _ROW0_GLYPH_OFFSET.get(g)
    if row0_offset is not None:
        return base + int(row0_offset)

    row1_offset = _ROW1_GLYPH_OFFSET.get(g)
    if row1_offset is not None:
        return row1 + int(row1_offset)

    if g == _GLYPH_ARROWS:
        # Extra icon lives on the next row under the prompt atlas.
        return base + int(PROMPT_GLYPH_SPR_ROW_STRIDE) * 2
    if g == _GLYPH_F6:
        # F6 icon is placed right after ARROWS icon.
        return base + int(PROMPT_GLYPH_SPR_ROW_STRIDE) * 2 + 1

    return -1
