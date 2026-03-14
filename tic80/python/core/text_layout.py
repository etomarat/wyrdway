from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .rich_tokens import rich_token_match


def text_width(text: str, char_w: int = 6) -> int:
    cw = int(char_w)
    if cw < 1:
        cw = 1
    return len(text) * cw


def rich_text_width(
    text: str,
    char_w: int = 6,
    glyph_w: int = 8,
    gap_w: int = 3,
    sep_w: int = 3
) -> int:
    """Text width for strings that may contain prompt glyph tokens.

    Token format: `{g:<int>}`. It counts as a single glyph of `glyph_w` pixels.
    Everything else counts as regular characters of `char_w` pixels.
    """
    cw = int(char_w)
    if cw < 1:
        cw = 1
    gw = int(glyph_w)
    if gw < 1:
        gw = 1

    s = str(text)
    i = 0
    w = 0
    n = len(s)
    gap = int(gap_w)
    if gap < 1:
        gap = 1
    sep = int(sep_w)
    if sep < 1:
        sep = 1

    while i < n:
        kind, _, next_i = rich_token_match(s, i)
        if kind == 1:
            w += gw
            i = next_i
            continue
        if kind == 2:
            w += gap
            i = next_i
            continue
        if kind == 3:
            w += sep
            i = next_i
            continue
        w += cw
        i = next_i
    return w


def text_max_chars(screen_w: int = 240, char_w: int = 6, margin_x: int = 0) -> int:
    cw = int(char_w)
    if cw < 1:
        cw = 1
    inner_w = int(screen_w) - int(margin_x) * 2
    if inner_w < 0:
        inner_w = 0
    return int(inner_w / cw)


def text_trim(text: str, max_chars: int, ellipsis: bool = True) -> str:
    limit = int(max_chars)
    if limit < 0:
        limit = 0
    if len(text) <= limit:
        return text
    if not ellipsis:
        return text[:limit]
    if limit <= 3:
        return text[:limit]
    return text[:limit - 3] + "..."


def text_center_x(text: str, screen_w: int = 240, char_w: int = 6, margin_x: int = 0) -> int:
    x = int((int(screen_w) - text_width(text, char_w)) * 0.5)
    min_x = int(margin_x)
    if x < min_x:
        return min_x
    return x


def rich_text_center_x(
    text: str,
    screen_w: int = 240,
    char_w: int = 6,
    glyph_w: int = 8,
    margin_x: int = 0
) -> int:
    x = int((int(screen_w) - rich_text_width(text, char_w, glyph_w)) * 0.5)
    min_x = int(margin_x)
    if x < min_x:
        return min_x
    return x


def text_right_x(text: str, right_x: int = 239, char_w: int = 6, margin_x: int = 0) -> int:
    x = int(right_x) + 1 - text_width(text, char_w)
    min_x = int(margin_x)
    if x < min_x:
        return min_x
    return x


def rich_text_right_x(
    text: str,
    right_x: int = 239,
    char_w: int = 6,
    glyph_w: int = 8,
    margin_x: int = 0
) -> int:
    x = int(right_x) + 1 - rich_text_width(text, char_w, glyph_w)
    min_x = int(margin_x)
    if x < min_x:
        return min_x
    return x
