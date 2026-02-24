from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import print, rect, rectb

    from ..text_layout import text_width


def ui_panel_draw(
    x: int,
    y: int,
    w: int,
    h: int,
    border_color: int,
    outer_color: int = 0,
    inner_color: int = 15
) -> None:
    rect(x, y, w, h, outer_color)
    rect(x + 1, y + 1, w - 2, h - 2, inner_color)
    rectb(x, y, w, h, border_color)


def ui_panel_draw_split_actions(
    x: int,
    y: int,
    w: int,
    h: int,
    left_text: str,
    right_text: str,
    border_color: int,
    text_color: int,
    outer_color: int = 0,
    inner_color: int = 15,
    left_width: int = -1,
    left_text_color: int = -1,
    right_text_color: int = -1
) -> None:
    ui_panel_draw(x, y, w, h, border_color, outer_color, inner_color)
    left_w = int(left_width)
    if left_w <= 0 or left_w >= w:
        left_w = int(w * 0.5)
    right_w = w - left_w
    divider_x = x + left_w
    rect(divider_x, y + 1, 1, h - 2, border_color)

    text_y = y + int((h - 6) * 0.5) + 1
    left_x = x + int((left_w - text_width(left_text)) * 0.5)
    right_x = divider_x + int((right_w - text_width(right_text)) * 0.5)
    left_color = left_text_color
    if left_color < 0:
        left_color = text_color
    right_color = right_text_color
    if right_color < 0:
        right_color = text_color
    print(left_text, left_x, text_y, left_color, True)
    print(right_text, right_x, text_y, right_color, True)
