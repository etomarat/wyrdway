from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import print

    from .rich_text import ui_rich_has_glyph_tokens, ui_rich_print, ui_rich_text_center_x


def ui_text_center(
    text: str,
    y: int,
    color: int,
    screen_w: int = 240,
    margin_x: int = 4,
    fixed: bool | None = None
) -> None:
    fixed_font = True
    if fixed is None:
        fixed_font = not ui_rich_has_glyph_tokens(text)
    else:
        fixed_font = bool(fixed)
    ui_rich_print(
        text,
        ui_rich_text_center_x(text, screen_w=screen_w, margin_x=margin_x),
        y,
        color,
        fixed_font
    )
