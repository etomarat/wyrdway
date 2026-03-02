from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import TypeAlias

    from ..palette import Color
    OverlayTheme: TypeAlias = dict[str, int]
else:
    OverlayTheme = dict


def ui_overlay_theme_default() -> OverlayTheme:
    return {
        "title_color": Color.WHITE,
        "frame_color": Color.BLACK,
        "panel_color": Color.DARK_GREY,
        "header_fill_color": Color.BLACK,
        "header_line_color": Color.GREY,
        "button_bg_color": Color.BLACK,
        "divider_color": Color.GREY,
        "footer_line_color": Color.GREY,
        "slot_text_color": Color.LIGHT_GREY,
        "slot_active_bg_color": Color.DARK_BLUE,
        "slot_hover_bg_color": Color.DARK_GREY,
        "slot_active_text_color": Color.WHITE,
        "slot_hover_text_color": Color.WHITE
    }


def ui_overlay_theme_warning() -> OverlayTheme:
    theme = ui_overlay_theme_default()
    theme["title_color"] = Color.ORANGE
    theme["frame_color"] = Color.ORANGE
    return theme


def ui_overlay_theme_good() -> OverlayTheme:
    theme = ui_overlay_theme_default()
    theme["title_color"] = Color.LIGHT_GREEN
    theme["frame_color"] = Color.LIGHT_GREEN
    return theme


def ui_overlay_theme_fail() -> OverlayTheme:
    theme = ui_overlay_theme_default()
    theme["title_color"] = Color.RED
    theme["frame_color"] = Color.RED
    return theme


def ui_overlay_theme_inverted() -> OverlayTheme:
    theme = ui_overlay_theme_default()
    theme["frame_color"] = Color.DARK_GREY
    theme["panel_color"] = Color.BLACK
    return theme
