from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import print

    from ..text_layout import text_center_x


def ui_text_center(
    text: str,
    y: int,
    color: int,
    screen_w: int = 240,
    margin_x: int = 4,
    fixed: bool = True
) -> None:
    print(
        text,
        text_center_x(text, screen_w=screen_w, margin_x=margin_x),
        y,
        color,
        fixed
    )
