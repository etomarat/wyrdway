from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import rect, rectb

    from .rich_text import ui_rich_has_glyph_tokens, ui_rich_print, ui_rich_text_center_x


def ui_modal_centered_box(
    box_w: int,
    box_h: int,
    screen_w: int = 240,
    screen_h: int = 136
) -> tuple[int, int]:
    x = int((int(screen_w) - int(box_w)) * 0.5)
    y = int((int(screen_h) - int(box_h)) * 0.5)
    return x, y


def ui_modal_draw_box(
    box_x: int,
    box_y: int,
    box_w: int,
    box_h: int,
    border_color: int,
    outer_color: int = 0,
    inner_color: int = 15
) -> None:
    rect(box_x, box_y, box_w, box_h, outer_color)
    rect(box_x + 1, box_y + 1, box_w - 2, box_h - 2, inner_color)
    rectb(box_x, box_y, box_w, box_h, border_color)


def ui_modal_draw_lines(
    lines: tuple[tuple[str, int], ...],
    box_x: int,
    box_y: int,
    box_w: int,
    top_pad: int = 10,
    line_step: int = 12
) -> None:
    y = box_y + int(top_pad)
    step = int(line_step)
    i = 0
    while i < len(lines):
        text, color = lines[i]
        x = box_x + ui_rich_text_center_x(text, screen_w=box_w, margin_x=0)
        ui_rich_print(text, x, y, color, not ui_rich_has_glyph_tokens(text))
        y += step
        i += 1
