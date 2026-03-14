from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import print, rect

    from .overlay_layout import OverlayLayout, ui_overlay_layout_int
    from .rich_text import ui_rich_print, ui_rich_text_width
    from ..text_layout import text_width
else:
    OverlayLayout = dict


def ui_options_settings_draw(
    layout: OverlayLayout,
    body_x: int,
    body_top: int,
    line_step: int,
    body_x_pad: int,
    selected_row: int,
    labels: list[str],
    values: list[str],
    enabled_rows: list[bool],
    active_rows: list[bool],
    left_arrow: str,
    right_arrow: str,
    right_gap_comp: int,
    value_anchor_label: str,
    panel_bg_color: int,
    text_base_color: int,
    text_selected_color: int,
    text_active_color: int
) -> None:
    marker_x = body_x
    label_x = body_x + 10
    value_x = body_x + text_width(value_anchor_label, 6) + 14
    left_w = ui_rich_text_width(left_arrow)
    left_gap = ui_rich_text_width("{gap}")
    right_gap = ui_rich_text_width("{gap}")
    row_w = ui_overlay_layout_int(layout, "box_w", 200) - body_x_pad * 2 - 2

    row = 0
    while row < len(labels):
        row_y = body_top + row * line_step
        enabled = bool(enabled_rows[row]) if row < len(enabled_rows) else False
        selected = row == selected_row
        row_active = bool(active_rows[row]) if row < len(active_rows) else False

        if row_active:
            rect(body_x - 1, row_y - 1, row_w, 8, panel_bg_color)

        label_color = int(text_base_color)
        value_color = int(text_base_color)
        marker_color = int(panel_bg_color)
        if not enabled:
            label_color = int(panel_bg_color)
            value_color = int(panel_bg_color)
        if selected:
            marker_color = int(text_selected_color)
            if enabled:
                label_color = int(text_selected_color)
                value_color = int(text_selected_color)
        if row_active:
            marker_color = int(text_active_color)
            if enabled:
                label_color = int(text_active_color)
                value_color = int(text_active_color)
        if selected:
            print(">", marker_x, row_y, marker_color)

        label = labels[row]
        value = values[row] if row < len(values) else ""
        print(label, label_x, row_y, label_color)
        value_draw_x = value_x + left_w + left_gap
        print(value, value_draw_x, row_y, value_color, fixed=True)
        if selected and enabled and left_arrow != "" and right_arrow != "":
            arrow_color = value_color
            if row_active:
                arrow_color = int(text_active_color)
            left_arrow_x = value_draw_x - left_gap - left_w
            right_arrow_x = value_draw_x + text_width(value, 6) + right_gap + right_gap_comp
            ui_rich_print(left_arrow, left_arrow_x, row_y, arrow_color, fixed=True)
            ui_rich_print(right_arrow, right_arrow_x, row_y, arrow_color, fixed=True)
        row += 1


def ui_options_settings_row_at(
    layout: OverlayLayout,
    body_x_pad: int,
    line_step: int,
    row_count: int,
    mx: int,
    my: int
) -> int:
    body_top = ui_overlay_layout_int(layout, "body_top", 54)
    body_x = ui_overlay_layout_int(layout, "box_x", 20) + body_x_pad
    body_w = ui_overlay_layout_int(layout, "box_w", 200) - body_x_pad * 2
    if mx < body_x or mx >= body_x + body_w:
        return -1
    row = 0
    while row < int(row_count):
        row_y = body_top + row * line_step
        if my >= row_y - 1 and my < row_y + 7:
            return row
        row += 1
    return -1


def ui_options_settings_dir_at(
    layout: OverlayLayout,
    body_x_pad: int,
    line_step: int,
    row: int,
    row_enabled: bool,
    row_value: str,
    left_arrow: str,
    right_arrow: str,
    right_gap_comp: int,
    value_anchor_label: str,
    mx: int,
    my: int
) -> int:
    if int(row) < 0:
        return 0
    if not bool(row_enabled):
        return 0

    body_top = ui_overlay_layout_int(layout, "body_top", 54)
    row_y = body_top + int(row) * int(line_step)
    if my < row_y - 1 or my >= row_y + 7:
        return 0

    body_x = ui_overlay_layout_int(layout, "box_x", 20) + body_x_pad
    value_x = body_x + text_width(value_anchor_label, 6) + 14
    if left_arrow == "" or right_arrow == "":
        return 0

    left_w = ui_rich_text_width(left_arrow)
    left_gap = ui_rich_text_width("{gap}")
    right_w = ui_rich_text_width(right_arrow)
    right_gap = ui_rich_text_width("{gap}")
    value_w = text_width(row_value, 6)
    value_x0 = value_x + left_w + left_gap
    left_x0 = value_x0 - left_gap - left_w
    left_x1 = left_x0 + left_w
    right_x0 = value_x0 + value_w + right_gap + right_gap_comp
    right_x1 = right_x0 + right_w
    if mx >= left_x0 and mx < left_x1:
        return -1
    if mx >= right_x0 and mx < right_x1:
        return 1
    return 0
