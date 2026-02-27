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

PROMPT_GLYPH_SPR_BASE = 259
PROMPT_GLYPH_SPR_ROW_STRIDE = 16


def prompt_glyph_sprite_id(glyph: int) -> int:
    """Maps PromptGlyph id -> sprite id, or -1 if not available."""
    g = int(glyph)
    base = int(PROMPT_GLYPH_SPR_BASE)
    row1 = base + int(PROMPT_GLYPH_SPR_ROW_STRIDE)

    # Gamepad: face positions.
    if g == 0:  # PromptGlyph.PAD_SOUTH
        return base + 0
    if g == 1:  # PromptGlyph.PAD_WEST
        return base + 1
    if g == 2:  # PromptGlyph.PAD_EAST
        return base + 3
    if g == 3:  # PromptGlyph.PAD_NORTH
        return base + 2

    # Gamepad: shoulders.
    if g == 4:  # PromptGlyph.PAD_RT
        return base + 9
    if g == 5:  # PromptGlyph.PAD_LT
        return base + 10
    if g == 6:  # PromptGlyph.PAD_RB
        return base + 11
    if g == 7:  # PromptGlyph.PAD_LB
        return base + 12

    # Gamepad: D-pad directions.
    if g == 8:  # PromptGlyph.PAD_UP
        return base + 5
    if g == 9:  # PromptGlyph.PAD_DOWN
        return base + 8
    if g == 10:  # PromptGlyph.PAD_LEFT
        return base + 7
    if g == 11:  # PromptGlyph.PAD_RIGHT
        return base + 6
    if g == 12:  # PromptGlyph.PAD_DPAD
        return base + 4

    # Keyboard (optional; currently we render keyboard as text by default).
    if g == 20:  # PromptGlyph.KEY_UP
        return row1 + 3
    if g == 21:  # PromptGlyph.KEY_DOWN
        return row1 + 5
    if g == 22:  # PromptGlyph.KEY_LEFT
        return row1 + 6
    if g == 23:  # PromptGlyph.KEY_RIGHT
        return row1 + 4
    if g == 24:  # PromptGlyph.KEY_Z
        return row1 + 7
    if g == 25:  # PromptGlyph.KEY_X
        return row1 + 8
    if g == 26:  # PromptGlyph.KEY_A
        return row1 + 9
    if g == 27:  # PromptGlyph.KEY_S
        return row1 + 10
    if g == 28:  # PromptGlyph.KEY_ENTER
        return row1 + 1
    if g == 29:  # PromptGlyph.KEY_SPACE
        return row1 + 0
    if g == 30:  # PromptGlyph.KEY_BACKSPACE
        return row1 + 2
    if g == 31:  # PromptGlyph.KEY_Y
        return row1 + 11
    if g == 32:  # PromptGlyph.KEY_B
        return row1 + 12
    if g == 33:  # PromptGlyph.KEY_ARROWS
        # Extra icon lives on the next row under the prompt atlas.
        return base + int(PROMPT_GLYPH_SPR_ROW_STRIDE) * 2

    return -1
