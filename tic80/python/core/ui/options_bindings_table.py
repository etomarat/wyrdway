from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import line, print

    from .overlay_layout import OverlayLayout, ui_overlay_layout_int
    from .rich_text import ui_rich_print
else:
    OverlayLayout = dict


def ui_options_bindings_table_draw(
    layout: OverlayLayout,
    body_x: int,
    area_top: int,
    footer_line_y: int,
    left_rows: list[tuple[str, str]],
    right_rows: list[tuple[str, str]],
    title_color: int,
    row_color: int,
    line_color: int
) -> None:
    table_x0 = body_x
    table_x1 = ui_overlay_layout_int(layout, "box_x", 20) + ui_overlay_layout_int(layout, "box_w", 200) - 9
    table_y0 = area_top
    table_y1 = footer_line_y - 4
    if table_x1 <= table_x0 or table_y1 <= table_y0:
        return
    split_x = table_x0 + int((table_x1 - table_x0) * 0.5)
    line(split_x, table_y0 + 1, split_x, table_y1, line_color)

    left_title_x = table_x0 + 2
    right_title_x = split_x + 3
    right_text_x = right_title_x + 2
    title_y = table_y0 + 2
    print("MENU", left_title_x, title_y, title_color)
    print("DRIVING", right_text_x, title_y, title_color)
    line(left_title_x - 2, title_y + 7, split_x - 2, title_y + 7, line_color)
    line(right_title_x, title_y + 7, table_x1, title_y + 7, line_color)

    ui_options_bindings_column_draw(left_title_x, title_y + 11, 66, 8, left_rows, row_color)
    ui_options_bindings_column_draw(right_text_x, title_y + 11, 66, 8, right_rows, row_color)


def ui_options_bindings_column_draw(
    col_x: int,
    rows_top: int,
    bind_dx: int,
    row_step: int,
    rows: list[tuple[str, str]],
    row_color: int
) -> None:
    i = 0
    while i < len(rows):
        row_y = rows_top + i * row_step
        label, prompt = rows[i]
        print(label, col_x, row_y, row_color)
        ui_rich_print(prompt, col_x + bind_dx, row_y, row_color, fixed=True)
        i += 1
