def text_width(text: str, char_w: int = 6) -> int:
    cw = int(char_w)
    if cw < 1:
        cw = 1
    return len(text) * cw


def rich_text_width(text: str, char_w: int = 6, glyph_w: int = 8) -> int:
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

    i = 0
    w = 0
    s = str(text)
    n = len(s)
    while i < n:
        if i + 3 < n and s[i] == "{" and s[i + 1] == "g" and s[i + 2] == ":":
            j = i + 3
            # Parse digits.
            if j < n and s[j] >= "0" and s[j] <= "9":
                while j < n and s[j] >= "0" and s[j] <= "9":
                    j += 1
                if j < n and s[j] == "}":
                    w += gw
                    i = j + 1
                    continue
        w += cw
        i += 1
    return int(w)


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
