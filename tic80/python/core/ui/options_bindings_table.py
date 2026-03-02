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
    left_sections: list[tuple[str, list[tuple[str, str]]]],
    right_sections: list[tuple[str, list[tuple[str, str]]]],
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

    left_section_x0 = table_x0
    left_section_x1 = split_x - 2
    right_section_x0 = split_x + 3
    right_section_x1 = table_x1
    left_text_x = left_section_x0 + 2
    right_text_x = right_section_x0 + 2
    title_y = table_y0 + 2
    row_step = 8
    left_bind_dx = 64
    right_bind_dx = 58
    ui_options_bindings_sections_column_draw(
        left_section_x0,
        left_section_x1,
        left_text_x,
        title_y,
        table_y1,
        left_sections,
        left_bind_dx,
        row_step,
        title_color,
        row_color,
        line_color
    )
    ui_options_bindings_sections_column_draw(
        right_section_x0,
        right_section_x1,
        right_text_x,
        title_y,
        table_y1,
        right_sections,
        right_bind_dx,
        row_step,
        title_color,
        row_color,
        line_color
    )


def ui_options_bindings_sections_column_draw(
    section_x0: int,
    section_x1: int,
    text_x: int,
    title_y: int,
    table_y1: int,
    sections: list[tuple[str, list[tuple[str, str]]]],
    bind_dx: int,
    row_step: int,
    title_color: int,
    row_color: int,
    line_color: int
) -> None:
    if len(sections) <= 0:
        return
    section_gap = 4
    section_title_y = int(title_y)
    section_i = 0
    while section_i < len(sections):
        title, rows = sections[section_i]
        if section_title_y + 7 >= table_y1:
            return
        print(title, text_x, section_title_y, title_color)
        line(section_x0, section_title_y + 7,
             section_x1, section_title_y + 7, line_color)

        rows_top = section_title_y + 11
        max_rows = int((table_y1 - rows_top) / row_step) + 1
        if max_rows < 1:
            return
        draw_rows = rows
        if len(draw_rows) > max_rows:
            draw_rows = rows[:max_rows]
        ui_options_bindings_column_draw(
            text_x,
            rows_top,
            bind_dx,
            row_step,
            draw_rows,
            row_color
        )
        section_title_y = rows_top + len(draw_rows) * row_step + section_gap
        section_i += 1


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
