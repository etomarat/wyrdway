from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import print, rect, spr

    from ..controls.glyph_atlas import prompt_glyph_sprite_id
    from ..controls.prompts import glyph_label
    from ..rich_tokens import rich_token_match


_PROMPT_GLYPH_COLORKEY = 0
# Fine-tuning for vertical alignment of 8x8 glyph sprites relative to 6px text.
# If prompts feel too low/high, tweak this value (in screen pixels).
_PROMPT_GLYPH_Y_NUDGE_PX = -1

# Horizontal spacing (in pixels, before scaling).
#
# Use `{gap}` between prompt glyphs and text so spacing is consistent everywhere.
# If you ever need text before glyphs, also use `{gap}` at that boundary.
_PROMPT_TEXT_GAP_PX = 3

# `{sep}` is drawn as a thin vertical line between glyphs, with configurable padding.
_PROMPT_SEP_PAD_BEFORE_PX = 2
_PROMPT_SEP_PAD_AFTER_PX = 2
_PROMPT_SEP_LINE_W_PX = 1
_PROMPT_SEP_LINE_H_PX = 7


def ui_rich_text_width(text: str, scale: int = 1) -> int:
    """Width of a rich string in pixels (matches ui_rich_print)."""
    s = str(text)
    n = len(s)
    i = 0
    sc = int(scale)
    if sc < 1:
        sc = 1
    w = 0
    while i < n:
        kind, _, next_i = rich_token_match(s, i)
        if kind == 1:
            w += 8 * sc
            i = next_i
            continue
        if kind == 2:
            w += _PROMPT_TEXT_GAP_PX * sc
            i = next_i
            continue
        if kind == 3:
            w += (_PROMPT_SEP_PAD_BEFORE_PX +
                  _PROMPT_SEP_LINE_W_PX + _PROMPT_SEP_PAD_AFTER_PX) * sc
            i = next_i
            continue
        w += 6 * sc
        i = next_i
    return int(w)


def ui_rich_text_center_x(
    text: str,
    screen_w: int = 240,
    margin_x: int = 0,
    scale: int = 1
) -> int:
    x = int((int(screen_w) - ui_rich_text_width(text, scale)) * 0.5)
    min_x = int(margin_x)
    if x < min_x:
        return min_x
    return x


def ui_rich_print(
    text: str,
    x: int,
    y: int,
    color: int,
    fixed: bool = False,
    scale: int = 1,
    glyph_dy: int | None = None
) -> int:
    """Prints text with inline glyph tokens.

    Supported token format: `{g:<int>}` where `<int>` is a PromptGlyph id.
    The token is rendered as a sprite when available, otherwise falls back to
    text: `(SOUTH)` / `[ENTER]` depending on the glyph range.
    """
    s = str(text)
    n = len(s)
    i = 0
    cx = int(x)
    cy = int(y)
    buf = ""
    sc = int(scale)
    if sc < 1:
        sc = 1
    # We always print in fixed-width mode so spacing matches our width advances.
    fx = True
    # PocketPy is picky about non-literal defaults in function signatures,
    # so we apply the tweak here instead of `glyph_dy=_PROMPT_GLYPH_Y_NUDGE_PX`.
    dy = _PROMPT_GLYPH_Y_NUDGE_PX if glyph_dy is None else int(glyph_dy)
    base_y = cy - sc + dy

    while i < n:
        kind, glyph, next_i = rich_token_match(s, i)
        if kind == 2:
            cx += _PROMPT_TEXT_GAP_PX * sc
            i = next_i
            continue
        if kind == 3:
            cx += _PROMPT_SEP_PAD_BEFORE_PX * sc
            # Draw line centered within 8px glyph height.
            rect(
                cx,
                base_y + sc,
                _PROMPT_SEP_LINE_W_PX * sc,
                _PROMPT_SEP_LINE_H_PX * sc,
                color
            )
            cx += _PROMPT_SEP_LINE_W_PX * sc
            cx += _PROMPT_SEP_PAD_AFTER_PX * sc
            i = next_i
            continue
        if kind == 1:
            if buf != "":
                print(buf, cx, cy, color, fx, sc)
                cx += len(buf) * 6 * sc
                buf = ""
            spr_id = int(prompt_glyph_sprite_id(glyph))
            if spr_id >= 0:
                # Align 8px sprite with 6px text cell.
                spr(spr_id, cx, base_y, _PROMPT_GLYPH_COLORKEY, sc)
                cx += 8 * sc
            else:
                label = str(glyph_label(glyph))
                if glyph >= 20:
                    fallback = "[" + label + "]"
                else:
                    fallback = "(" + label + ")"
                print(fallback, cx, cy, color, fx, sc)
                cx += len(fallback) * 6 * sc
            i = next_i
            continue

        buf += s[i]
        i = next_i

    if buf != "":
        print(buf, cx, cy, color, fx, sc)
        cx += len(buf) * 6 * sc

    return int(cx - int(x))
