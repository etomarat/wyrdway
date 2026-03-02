from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Sequence

    from ..palette import Color
    from .overlay_layout import OverlayLayout
    from .overlay_theme import OverlayTheme
    from .overlay_runtime import UiOverlayRuntime
    from .overlay_modal import (
        ui_overlay_modal_draw_centered_lines,
        ui_overlay_modal_draw_chrome
    )
    from .overlay_footer import ui_overlay_footer_draw


def ui_overlay_screen_draw(
    runtime: UiOverlayRuntime,
    layout: OverlayLayout,
    title: str,
    body_lines: Sequence[tuple[str, int]],
    slots: list[str],
    keyboard_active: Sequence[bool],
    theme: OverlayTheme | None = None,
    title_color: int = -1,
    body_line_step: int = 8,
    frame_color: int = -1,
    panel_color: int = -1,
    header_fill_color: int = -1,
    header_line_color: int = -1,
    button_bg_color: int = -1,
    divider_color: int = -1,
    footer_line_color: int = -1,
    slot_text_color: int = -1,
    slot_active_bg_color: int = -1,
    slot_hover_bg_color: int = -1,
    slot_active_text_color: int = -1,
    slot_hover_text_color: int = -1
) -> tuple[int, int, int, int, int, int, int]:
    if theme is None:
        theme = {}
    if title_color < 0:
        title_color = int(theme.get("title_color", Color.WHITE))
    if frame_color < 0:
        frame_color = int(theme.get("frame_color", Color.BLACK))
    if panel_color < 0:
        panel_color = int(theme.get("panel_color", Color.DARK_GREY))
    if header_fill_color < 0:
        header_fill_color = int(theme.get("header_fill_color", Color.BLACK))
    if header_line_color < 0:
        header_line_color = int(theme.get("header_line_color", Color.GREY))
    if button_bg_color < 0:
        button_bg_color = int(theme.get("button_bg_color", Color.BLACK))
    if divider_color < 0:
        divider_color = int(theme.get("divider_color", Color.GREY))
    if footer_line_color < 0:
        footer_line_color = int(theme.get("footer_line_color", Color.GREY))
    if slot_text_color < 0:
        slot_text_color = int(theme.get("slot_text_color", Color.LIGHT_GREY))
    if slot_active_bg_color < 0:
        slot_active_bg_color = int(theme.get("slot_active_bg_color", Color.DARK_BLUE))
    if slot_hover_bg_color < 0:
        slot_hover_bg_color = int(theme.get("slot_hover_bg_color", Color.DARK_GREY))
    if slot_active_text_color < 0:
        slot_active_text_color = int(theme.get("slot_active_text_color", Color.WHITE))
    if slot_hover_text_color < 0:
        slot_hover_text_color = int(theme.get("slot_hover_text_color", Color.WHITE))
    box_x, box_y, box_w, box_h, body_top, footer_line_y, footer_text_y = ui_overlay_modal_draw_chrome(
        layout,
        title,
        title_color,
        frame_color,
        panel_color,
        header_fill_color,
        header_line_color
    )
    ui_overlay_modal_draw_centered_lines(
        body_lines,
        box_x,
        box_w,
        body_top,
        body_line_step
    )
    slot_active, slot_hover = runtime.slot_states(
        len(slots),
        keyboard_active
    )
    ui_overlay_footer_draw(
        layout,
        slots,
        slot_active,
        slot_hover,
        footer_line_y,
        footer_text_y,
        button_bg_color,
        divider_color,
        footer_line_color,
        slot_text_color,
        slot_active_bg_color,
        slot_hover_bg_color,
        slot_active_text_color,
        slot_hover_text_color
    )
    return box_x, box_y, box_w, box_h, body_top, footer_line_y, footer_text_y
