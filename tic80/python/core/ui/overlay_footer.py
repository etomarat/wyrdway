from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import line, print, rect

    from ..palette import Color
    from .overlay_layout import OverlayLayout
    from .rich_text import ui_rich_print, ui_rich_text_width
    from .overlay_layout import (
        ui_overlay_footer_slot_geometry,
        ui_overlay_layout_int
    )


def ui_overlay_footer_draw(
    layout: OverlayLayout,
    slots: list[str],
    slot_active: list[bool],
    slot_hover: list[bool],
    footer_line_y: int,
    footer_text_y: int,
    button_bg_color: int,
    divider_color: int = -1,
    debug_slots: bool = False,
    footer_line_color: int = -1,
    slot_text_color: int = -1,
    slot_active_bg_color: int = -1,
    slot_hover_bg_color: int = -1,
    slot_active_text_color: int = -1,
    slot_hover_text_color: int = -1
) -> None:
    if divider_color < 0:
        divider_color = Color.GREY
    if footer_line_color < 0:
        footer_line_color = Color.GREY
    if slot_text_color < 0:
        slot_text_color = Color.LIGHT_GREY
    if slot_active_bg_color < 0:
        slot_active_bg_color = Color.DARK_BLUE
    if slot_hover_bg_color < 0:
        slot_hover_bg_color = Color.DARK_GREY
    if slot_active_text_color < 0:
        slot_active_text_color = Color.WHITE
    if slot_hover_text_color < 0:
        slot_hover_text_color = Color.WHITE

    x = ui_overlay_layout_int(layout, "box_x", 20)
    w = ui_overlay_layout_int(layout, "box_w", 200)
    line(x + 4, footer_line_y, x + w - 5, footer_line_y, footer_line_color)
    slot_count = len(slots)
    slot_starts, slot_ends, button_bg_y, button_bg_h = ui_overlay_footer_slot_geometry(
        layout,
        slot_count,
        footer_line_y,
        footer_text_y
    )
    slot_text_colors: list[int] = []
    i = 0
    while i < slot_count:
        slot_text_colors.append(slot_text_color)
        i += 1

    i = 0
    while i < slot_count:
        text = str(slots[i])
        if text != "":
            slot_x0 = slot_starts[i]
            slot_x1 = slot_ends[i]
            slot_w = slot_x1 - slot_x0
            if slot_w > 0:
                bg = button_bg_color
                if i < len(slot_active) and slot_active[i]:
                    bg = slot_active_bg_color
                    slot_text_colors[i] = slot_active_text_color
                elif i < len(slot_hover) and slot_hover[i]:
                    bg = slot_hover_bg_color
                    slot_text_colors[i] = slot_hover_text_color
                rect(slot_x0, button_bg_y, slot_w, button_bg_h, bg)
        i += 1

    if debug_slots:
        debug_y = footer_line_y + 1
        debug_h = 11
        debug_colors = [
            Color.DARK_BLUE,
            Color.BLUE,
            Color.DARK_GREEN,
            Color.PURPLE
        ]
        j = 0
        while j < slot_count:
            slot_x0 = slot_starts[j]
            slot_x1 = slot_ends[j]
            slot_w = slot_x1 - slot_x0
            rect(slot_x0, debug_y, slot_w, debug_h, debug_colors[j % len(debug_colors)])
            print(str(j + 1), slot_x0 + 1, debug_y + 1, Color.YELLOW, fixed=True)
            j += 1

    j = 1
    while j < slot_count:
        split_x = slot_starts[j]
        line(split_x, footer_line_y + 1, split_x, footer_text_y + 7, divider_color)
        j += 1

    i = 0
    while i < slot_count:
        text = str(slots[i])
        if text != "":
            slot_x0 = slot_starts[i]
            slot_x1 = slot_ends[i]
            slot_w = slot_x1 - slot_x0
            text_w = ui_rich_text_width(text)
            draw_x = slot_x0 + int((slot_w - text_w) * 0.5)
            ui_rich_print(text, draw_x, footer_text_y, slot_text_colors[i], fixed=True)
        i += 1
