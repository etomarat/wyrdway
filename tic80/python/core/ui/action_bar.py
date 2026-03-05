from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import TypeAlias, TypedDict

    from tic80 import rectb
    from .panel import ui_panel_draw
    from .footer_mouse import (
        OverlayFooterMouseState,
        UiMouseState,
        ui_overlay_footer_slot_states
    )
    from .overlay_footer import ui_overlay_footer_draw
    from .overlay_layout import OverlayLayout, ui_overlay_layout_int

    ActionBarRowSpec: TypeAlias = tuple[int, tuple[int, ...]]
    ActionBarRowSpecs: TypeAlias = list[ActionBarRowSpec] | tuple[ActionBarRowSpec, ...]

    class ActionBarStyle(TypedDict):
        line_offset_y: int
        text_offset_y: int
        button_bg_color: int
        divider_color: int
        footer_line_color: int
        slot_text_color: int
        slot_active_bg_color: int
        slot_hover_bg_color: int
        slot_active_text_color: int
        slot_hover_text_color: int
        panel_border_color: int
        panel_border_outset: int
        panel_x: int
        panel_y: int
        panel_w: int
        panel_h: int
        panel_outer_color: int
        panel_inner_color: int

    class ActionBarStylePatch(TypedDict, total=False):
        line_offset_y: int
        text_offset_y: int
        button_bg_color: int
        divider_color: int
        footer_line_color: int
        slot_text_color: int
        slot_active_bg_color: int
        slot_hover_bg_color: int
        slot_active_text_color: int
        slot_hover_text_color: int
        panel_border_color: int
        panel_border_outset: int
        panel_x: int
        panel_y: int
        panel_w: int
        panel_h: int
        panel_outer_color: int
        panel_inner_color: int
else:
    OverlayLayout = dict
    ActionBarRowSpecs = list
    ActionBarStyle = dict
    ActionBarStylePatch = dict


UI_ACTION_BAR_ROW_H = 11
UI_ACTION_BAR_LINE_OFFSET_Y = -1
UI_ACTION_BAR_TEXT_OFFSET_Y = 3
UI_ACTION_BAR_ROW_GAP_DEFAULT = 1
UI_ACTION_BAR_PANEL_PAD_Y_DEFAULT = 0
UI_ACTION_BAR_FOOTER_PAD_X_DEFAULT = 0

def ui_action_bar_make_row_layout(
    x: int,
    y: int,
    w: int,
    slot_count: int,
    slot_weights: tuple[int, ...]
) -> OverlayLayout:
    return {
        "box_x": int(x),
        "box_y": int(y),
        "box_w": int(w),
        "box_h": int(UI_ACTION_BAR_ROW_H),
        "footer_pad_x": int(UI_ACTION_BAR_FOOTER_PAD_X_DEFAULT),
        "slot_count": int(slot_count),
        "slot_weights": slot_weights
    }


def ui_action_bar_panel_height(
    row_count: int,
    row_h: int = 11,
    row_gap: int = 1,
    pad_y: int = 0
) -> int:
    n = int(row_count)
    if n < 1:
        n = 1
    h = int(row_h)
    if h < 8:
        h = 8
    gap = int(row_gap)
    if gap < 0:
        gap = 0
    py = int(pad_y)
    if py < 0:
        py = 0
    return n * h + (n - 1) * gap + py * 2


def ui_action_bar_build_standard(
    panel_x: int,
    panel_y: int,
    panel_w: int,
    row_specs: ActionBarRowSpecs,
    row_gap: int = 1,
    pad_y: int = 0,
    footer_pad_x: int = 0
) -> tuple[int, list[OverlayLayout]]:
    panel_h = ui_action_bar_panel_height(
        len(row_specs),
        UI_ACTION_BAR_ROW_H,
        row_gap,
        pad_y
    )
    layouts = ui_action_bar_build_row_layouts(
        panel_x,
        panel_y,
        panel_w,
        row_specs,
        UI_ACTION_BAR_ROW_H,
        row_gap,
        pad_y,
        footer_pad_x
    )
    return panel_h, layouts


def ui_action_bar_build_row_layouts(
    panel_x: int,
    panel_y: int,
    panel_w: int,
    row_specs: ActionBarRowSpecs,
    row_h: int = 11,
    row_gap: int = 1,
    pad_y: int = 0,
    footer_pad_x: int = 0
) -> list[OverlayLayout]:
    layouts: list[OverlayLayout] = []
    y = int(panel_y) + int(pad_y)
    h = int(row_h)
    if h < 8:
        h = 8
    gap = int(row_gap)
    if gap < 0:
        gap = 0
    i = 0
    while i < len(row_specs):
        spec = row_specs[i]
        slot_count = int(spec[0])
        if slot_count < 1:
            slot_count = 1
        slot_weights = spec[1]
        layouts.append(
            {
                "box_x": int(panel_x),
                "box_y": y + i * (h + gap),
                "box_w": int(panel_w),
                "box_h": h,
                "footer_pad_x": int(footer_pad_x),
                "slot_count": slot_count,
                "slot_weights": slot_weights
            }
        )
        i += 1
    return layouts


def ui_action_bar_make_mouse_states(row_count: int) -> list[OverlayFooterMouseState]:
    states: list[OverlayFooterMouseState] = []
    n = int(row_count)
    if n < 1:
        n = 1
    i = 0
    while i < n:
        states.append(OverlayFooterMouseState())
        i += 1
    return states


def ui_action_bar_reset_mouse_states(states: list[OverlayFooterMouseState]) -> None:
    i = 0
    while i < len(states):
        states[i].reset()
        i += 1


def ui_action_bar_row_positions(
    layout: OverlayLayout,
    line_offset_y: int = -1,
    text_offset_y: int = 3
) -> tuple[int, int]:
    y = ui_overlay_layout_int(layout, "box_y", 0)
    h = ui_overlay_layout_int(layout, "box_h", UI_ACTION_BAR_ROW_H)

    line_y = y + int(line_offset_y)
    text_y = y + int(text_offset_y)

    if h < 8:
        h = 8
    if text_y > y + h - 6:
        text_y = y + h - 6
    if text_y < y + 1:
        text_y = y + 1
    if line_y >= text_y:
        line_y = text_y - 1
    if line_y < y - 1:
        line_y = y - 1
    return int(line_y), int(text_y)


def ui_action_bar_row_poll_release(
    layout: OverlayLayout,
    slots: list[str],
    mouse_state: UiMouseState,
    footer_mouse: OverlayFooterMouseState,
    line_offset_y: int = -1,
    text_offset_y: int = 3
) -> int:
    line_y, text_y = ui_action_bar_row_positions(
        layout, line_offset_y, text_offset_y)
    return footer_mouse.poll_release(
        layout,
        slots,
        mouse_state,
        line_y,
        text_y
    )


def ui_action_bar_rows_poll_release(
    layouts: list[OverlayLayout],
    slots_rows: list[list[str]],
    mouse_state: UiMouseState,
    footer_mice: list[OverlayFooterMouseState],
    line_offset_y: int = -1,
    text_offset_y: int = 3
) -> list[int]:
    released: list[int] = []
    i = 0
    while i < len(layouts):
        row_slots: list[str] = []
        if i < len(slots_rows):
            row_slots = slots_rows[i]
        row_release = -1
        if i < len(footer_mice):
            row_release = ui_action_bar_row_poll_release(
                layouts[i],
                row_slots,
                mouse_state,
                footer_mice[i],
                line_offset_y,
                text_offset_y
            )
        released.append(row_release)
        i += 1
    return released


def ui_action_bar_row_draw(
    layout: OverlayLayout,
    slots: list[str],
    keyboard_active: list[bool],
    mouse_state: UiMouseState,
    footer_mouse: OverlayFooterMouseState,
    line_offset_y: int = -1,
    text_offset_y: int = 3,
    button_bg_color: int = 0,
    divider_color: int = 12,
    footer_line_color: int | None = 12,
    slot_text_color: int = 13,
    slot_active_bg_color: int = 1,
    slot_hover_bg_color: int = 13,
    slot_active_text_color: int = 12,
    slot_hover_text_color: int = 12
) -> None:
    slot_active, slot_hover = ui_overlay_footer_slot_states(
        len(slots),
        keyboard_active,
        mouse_state,
        footer_mouse
    )
    line_y, text_y = ui_action_bar_row_positions(
        layout, line_offset_y, text_offset_y)
    ui_overlay_footer_draw(
        layout,
        slots,
        slot_active,
        slot_hover,
        line_y,
        text_y,
        button_bg_color,
        divider_color,
        footer_line_color,
        slot_text_color,
        slot_active_bg_color,
        slot_hover_bg_color,
        slot_active_text_color,
        slot_hover_text_color
    )


def ui_action_bar_layout_bounds(layouts: list[OverlayLayout]) -> tuple[int, int, int, int]:
    if len(layouts) <= 0:
        return 0, 0, 0, 0
    x0 = ui_overlay_layout_int(layouts[0], "box_x", 0)
    y0 = ui_overlay_layout_int(layouts[0], "box_y", 0)
    x1 = x0 + ui_overlay_layout_int(layouts[0], "box_w", 0)
    y1 = y0 + ui_overlay_layout_int(layouts[0], "box_h", 0)
    i = 1
    while i < len(layouts):
        x = ui_overlay_layout_int(layouts[i], "box_x", 0)
        y = ui_overlay_layout_int(layouts[i], "box_y", 0)
        w = ui_overlay_layout_int(layouts[i], "box_w", 0)
        h = ui_overlay_layout_int(layouts[i], "box_h", 0)
        if x < x0:
            x0 = x
        if y < y0:
            y0 = y
        if x + w > x1:
            x1 = x + w
        if y + h > y1:
            y1 = y + h
        i += 1
    return x0, y0, x1 - x0, y1 - y0


def ui_action_bar_style_default() -> ActionBarStyle:
    return {
        "line_offset_y": int(UI_ACTION_BAR_LINE_OFFSET_Y),
        "text_offset_y": int(UI_ACTION_BAR_TEXT_OFFSET_Y),
        "button_bg_color": 0,
        "divider_color": 12,
        "footer_line_color": 12,
        "slot_text_color": 13,
        "slot_active_bg_color": 1,
        "slot_hover_bg_color": 13,
        "slot_active_text_color": 12,
        "slot_hover_text_color": 12,
        "panel_border_color": -1,
        "panel_border_outset": 1,
        "panel_x": -1,
        "panel_y": -1,
        "panel_w": -1,
        "panel_h": -1,
        "panel_outer_color": 0,
        "panel_inner_color": 0
    }


def ui_action_bar_style_merge(
    style_overrides: ActionBarStyle | ActionBarStylePatch | None = None
) -> ActionBarStyle:
    style = ui_action_bar_style_default()
    if style_overrides is None:
        return style
    style.update(style_overrides)
    return style


def ui_action_bar_style_with_border(
    base_style: ActionBarStyle | ActionBarStylePatch,
    panel_border_color: int
) -> ActionBarStyle:
    style = ui_action_bar_style_merge(base_style)
    style["panel_border_color"] = int(panel_border_color)
    return style


def ui_action_bar_style_with_panel(
    base_style: ActionBarStyle | ActionBarStylePatch,
    panel_x: int,
    panel_y: int,
    panel_w: int,
    panel_h: int,
    panel_outer_color: int = 0,
    panel_inner_color: int = 0,
    panel_border_outset: int = 0
) -> ActionBarStyle:
    style = ui_action_bar_style_merge(base_style)
    style["panel_x"] = int(panel_x)
    style["panel_y"] = int(panel_y)
    style["panel_w"] = int(panel_w)
    style["panel_h"] = int(panel_h)
    style["panel_outer_color"] = int(panel_outer_color)
    style["panel_inner_color"] = int(panel_inner_color)
    style["panel_border_outset"] = int(panel_border_outset)
    return style


def ui_action_bar_rows_poll_release_with_style(
    layouts: list[OverlayLayout],
    slots_rows: list[list[str]],
    mouse_state: UiMouseState,
    footer_mice: list[OverlayFooterMouseState],
    style: ActionBarStyle | ActionBarStylePatch | None = None
) -> list[int]:
    merged = ui_action_bar_style_merge(style)
    return ui_action_bar_rows_poll_release(
        layouts,
        slots_rows,
        mouse_state,
        footer_mice,
        int(merged.get("line_offset_y", UI_ACTION_BAR_LINE_OFFSET_Y)),
        int(merged.get("text_offset_y", UI_ACTION_BAR_TEXT_OFFSET_Y))
    )


def ui_action_bar_rows_draw_with_style(
    layouts: list[OverlayLayout],
    slots_rows: list[list[str]],
    keyboard_rows: list[list[bool]],
    mouse_state: UiMouseState,
    footer_mice: list[OverlayFooterMouseState],
    style: ActionBarStyle | ActionBarStylePatch | None = None,
    footer_line_colors: tuple[int | None, ...] | None = None
) -> None:
    merged = ui_action_bar_style_merge(style)
    ui_action_bar_rows_draw(
        layouts,
        slots_rows,
        keyboard_rows,
        mouse_state,
        footer_mice,
        int(merged.get("line_offset_y", UI_ACTION_BAR_LINE_OFFSET_Y)),
        int(merged.get("text_offset_y", UI_ACTION_BAR_TEXT_OFFSET_Y)),
        int(merged.get("button_bg_color", 0)),
        int(merged.get("divider_color", 12)),
        int(merged.get("footer_line_color", 12)),
        footer_line_colors,
        int(merged.get("panel_border_color", -1)),
        int(merged.get("panel_border_outset", 1)),
        int(merged.get("panel_x", -1)),
        int(merged.get("panel_y", -1)),
        int(merged.get("panel_w", -1)),
        int(merged.get("panel_h", -1)),
        int(merged.get("panel_outer_color", 0)),
        int(merged.get("panel_inner_color", 0)),
        int(merged.get("slot_text_color", 13)),
        int(merged.get("slot_active_bg_color", 1)),
        int(merged.get("slot_hover_bg_color", 13)),
        int(merged.get("slot_active_text_color", 12)),
        int(merged.get("slot_hover_text_color", 12))
    )


def ui_action_bar_rows_draw(
    layouts: list[OverlayLayout],
    slots_rows: list[list[str]],
    keyboard_rows: list[list[bool]],
    mouse_state: UiMouseState,
    footer_mice: list[OverlayFooterMouseState],
    line_offset_y: int = -1,
    text_offset_y: int = 3,
    button_bg_color: int = 0,
    divider_color: int = 12,
    footer_line_color: int = 12,
    footer_line_colors: tuple[int | None, ...] | None = None,
    panel_border_color: int = -1,
    panel_border_outset: int = 1,
    panel_x: int = -1,
    panel_y: int = -1,
    panel_w: int = -1,
    panel_h: int = -1,
    panel_outer_color: int = 0,
    panel_inner_color: int = 0,
    slot_text_color: int = 13,
    slot_active_bg_color: int = 1,
    slot_hover_bg_color: int = 13,
    slot_active_text_color: int = 12,
    slot_hover_text_color: int = 12
) -> None:
    border_x = 0
    border_y = 0
    border_w = 0
    border_h = 0
    if panel_border_color >= 0:
        box_x = int(panel_x)
        box_y = int(panel_y)
        box_w = int(panel_w)
        box_h = int(panel_h)
        if box_w > 0 and box_h > 0:
            border_x = box_x
            border_y = box_y
            border_w = box_w
            border_h = box_h
        else:
            auto_x, auto_y, auto_w, auto_h = ui_action_bar_layout_bounds(layouts)
            border_outset = int(panel_border_outset)
            if border_outset < 0:
                border_outset = 0
            border_x = auto_x - border_outset
            border_y = auto_y - border_outset
            border_w = auto_w + border_outset * 2
            border_h = auto_h + border_outset * 2
        if border_w > 0 and border_h > 0:
            ui_panel_draw(
                border_x,
                border_y,
                border_w,
                border_h,
                panel_border_color,
                panel_outer_color,
                panel_inner_color
            )
    i = 0
    while i < len(layouts):
        row_slots: list[str] = []
        row_keys: list[bool] = []
        if i < len(slots_rows):
            row_slots = slots_rows[i]
        if i < len(keyboard_rows):
            row_keys = keyboard_rows[i]
        if i >= len(footer_mice):
            i += 1
            continue
        row_footer_line_color: int | None = footer_line_color
        if i == 0:
            row_footer_line_color = None
        if footer_line_colors is not None and i < len(footer_line_colors):
            row_footer_line_color = footer_line_colors[i]
        ui_action_bar_row_draw(
            layouts[i],
            row_slots,
            row_keys,
            mouse_state,
            footer_mice[i],
            line_offset_y,
            text_offset_y,
            button_bg_color,
            divider_color,
            row_footer_line_color,
            slot_text_color,
            slot_active_bg_color,
            slot_hover_bg_color,
            slot_active_text_color,
            slot_hover_text_color
        )
        i += 1
    if panel_border_color >= 0 and border_w > 0 and border_h > 0:
        rectb(border_x, border_y, border_w, border_h, panel_border_color)
