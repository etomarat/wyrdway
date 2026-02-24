from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import print, rect, rectb


def ui_meter_clamp01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


def ui_meter_fill_ratio(value: float, cap: float) -> float:
    if cap <= 0.0:
        return 0.0
    return ui_meter_clamp01(value / cap)


def ui_meter_draw_bar(
    x: int,
    y: int,
    w: int,
    h: int,
    ratio: float,
    fill_color: int,
    border_color: int,
    outer_color: int,
    inner_color: int
) -> None:
    height = int(h)
    if height < 4:
        height = 4
    inner_w = int(w) - 2
    if inner_w < 1:
        inner_w = 1
    fill_w = int(inner_w * ui_meter_clamp01(float(ratio)))
    rect(int(x), int(y), int(w), height, int(outer_color))
    rect(int(x) + 1, int(y) + 1, inner_w, height - 2, int(inner_color))
    if fill_w > 0:
        rect(int(x) + 1, int(y) + 1, fill_w, height - 2, int(fill_color))
    rectb(int(x), int(y), int(w), height, int(border_color))


def ui_meter_draw_labeled(
    label: str,
    value: float,
    cap: float,
    x: int,
    y: int,
    w: int,
    bar_h: int,
    fill_color: int,
    label_color: int,
    border_color: int,
    outer_color: int,
    inner_color: int
) -> None:
    ratio = ui_meter_fill_ratio(float(value), float(cap))
    ui_meter_draw_bar(
        x,
        y,
        w,
        bar_h,
        ratio,
        fill_color,
        border_color,
        outer_color,
        inner_color
    )
    text = (
        str(label)
        + " "
        + f"{float(value):.2f}"
        + "/"
        + f"{float(cap):.2f}"
    )
    print(text, int(x), int(y) - 7, int(label_color))
