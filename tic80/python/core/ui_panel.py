from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import print, rect, rectb

    from .text_layout import text_width


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
    inner_color: int = 15
) -> None:
    ui_panel_draw(x, y, w, h, border_color, outer_color, inner_color)
    half_w = int(w * 0.5)
    divider_x = x + half_w
    rect(divider_x, y + 1, 1, h - 2, border_color)

    text_y = y + int((h - 6) * 0.5) + 1
    left_x = x + int((half_w - text_width(left_text)) * 0.5)
    right_x = divider_x + int((half_w - text_width(right_text)) * 0.5)
    print(left_text, left_x, text_y, text_color, True)
    print(right_text, right_x, text_y, text_color, True)
