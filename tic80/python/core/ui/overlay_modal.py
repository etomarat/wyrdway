from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Sequence

    from tic80 import line, print, rect

    from .rich_text import ui_rich_has_glyph_tokens, ui_rich_print, ui_rich_text_center_x
    from .overlay_layout import OverlayLayout, ui_overlay_layout_int
    from ..text_layout import text_center_x


def ui_overlay_modal_draw_chrome(
    layout: OverlayLayout,
    title: str,
    title_color: int,
    frame_color: int,
    panel_color: int,
    header_fill_color: int,
    header_line_color: int
) -> tuple[int, int, int, int, int, int, int]:
    x = ui_overlay_layout_int(layout, "box_x", 20)
    y = ui_overlay_layout_int(layout, "box_y", 28)
    w = ui_overlay_layout_int(layout, "box_w", 200)
    h = ui_overlay_layout_int(layout, "box_h", 90)
    header_text_y = ui_overlay_layout_int(layout, "header_text_y", 37)
    body_top = ui_overlay_layout_int(layout, "body_top", 54)
    footer_line_y = ui_overlay_layout_int(layout, "footer_line_y", 104)
    footer_text_y = ui_overlay_layout_int(layout, "footer_text_y", 108)

    rect(x, y, w, h, frame_color)
    rect(x + 1, y + 1, w - 2, h - 2, panel_color)
    rect(x + 4, y + 4, w - 8, 14, header_fill_color)
    line(x + 4, y + 18, x + w - 5, y + 18, header_line_color)
    print(title, text_center_x(title, margin_x=x + 4), header_text_y, title_color)
    return x, y, w, h, body_top, footer_line_y, footer_text_y


def ui_overlay_modal_draw_centered_lines(
    lines: Sequence[tuple[str, int]],
    box_x: int,
    box_w: int,
    top_y: int,
    line_step: int
) -> None:
    y = int(top_y)
    step = int(line_step)
    i = 0
    while i < len(lines):
        text, color = lines[i]
        x = box_x + ui_rich_text_center_x(text, screen_w=box_w, margin_x=0)
        ui_rich_print(text, x, y, color, not ui_rich_has_glyph_tokens(text))
        y += step
        i += 1
