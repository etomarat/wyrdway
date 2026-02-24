def text_width(text: str, char_w: int = 6) -> int:
    cw = int(char_w)
    if cw < 1:
        cw = 1
    return len(text) * cw


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


def text_right_x(text: str, right_x: int = 239, char_w: int = 6, margin_x: int = 0) -> int:
    x = int(right_x) + 1 - text_width(text, char_w)
    min_x = int(margin_x)
    if x < min_x:
        return min_x
    return x
