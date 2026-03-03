from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Literal, TypeAlias

    FooterPadProfileId: TypeAlias = Literal[0, 1]
    OverlayCenteredSpec: TypeAlias = tuple[int, int, int, int]
    OverlayLayoutValue: TypeAlias = int | tuple[int, ...]
    OverlayLayout: TypeAlias = dict[str, OverlayLayoutValue]
else:
    FooterPadProfileId = int
    OverlayCenteredSpec = tuple
    OverlayLayoutValue = int
    OverlayLayout = dict


FOOTER_PAD_PROFILE_DEFAULT: FooterPadProfileId = 0
FOOTER_PAD_PROFILE_INVERTED: FooterPadProfileId = 1


def ui_overlay_layout_int(layout: OverlayLayout, key: str, fallback: int) -> int:
    value = layout.get(key)
    if value is None:
        return int(fallback)
    if isinstance(value, tuple):
        return int(fallback)
    return int(value)


def ui_overlay_layout_slot_index(
    layout: OverlayLayout,
    key: str,
    fallback: int,
    slot_count: int
) -> int:
    idx = int(fallback)
    value = layout.get(key)
    if value is not None and not isinstance(value, tuple):
        idx = int(value)
    if idx < 0:
        return 0
    if idx >= slot_count:
        return slot_count - 1
    return idx


def ui_overlay_layout_slot_weights(layout: OverlayLayout, slot_count: int) -> list[int]:
    raw = layout.get("slot_weights")
    weights: list[int] = []
    i = 0
    while i < slot_count:
        w = 1
        if isinstance(raw, tuple) and i < len(raw):
            w = int(raw[i])
            if w < 1:
                w = 1
        weights.append(w)
        i += 1
    return weights


def ui_overlay_layout_slot_count(layout: OverlayLayout, fallback: int = 4) -> int:
    slot_count = ui_overlay_layout_int(layout, "slot_count", fallback)
    if slot_count < 1:
        return 1
    return slot_count


def ui_overlay_footer_positions(
    layout: OverlayLayout,
    fallback_line_y: int = 104,
    fallback_text_y: int = 108
) -> tuple[int, int]:
    y = ui_overlay_layout_int(layout, "box_y", 28)
    h = ui_overlay_layout_int(layout, "box_h", 90)

    # Keep footer anchored to the modal bottom across all overlays.
    footer_bottom_pad = ui_overlay_layout_int(layout, "footer_bottom_pad", -1)
    if footer_bottom_pad < 0:
        # Footer pad profile:
        # - default/black-frame: 2px from bottom
        # - inverted/non-black-frame: 1px from bottom
        footer_pad_profile = ui_overlay_layout_int(
            layout,
            "footer_pad_profile",
            FOOTER_PAD_PROFILE_DEFAULT
        )
        if footer_pad_profile == FOOTER_PAD_PROFILE_INVERTED:
            footer_bottom_pad = 1
        else:
            footer_bottom_pad = 2
    footer_line_gap = ui_overlay_layout_int(layout, "footer_line_gap", 4)
    if footer_bottom_pad < 0:
        footer_bottom_pad = 0
    if footer_line_gap < 1:
        footer_line_gap = 1

    footer_text_y = y + h - 8 - footer_bottom_pad
    min_text_y = y + 20
    if footer_text_y < min_text_y:
        footer_text_y = min_text_y

    footer_line_y = footer_text_y - footer_line_gap
    if footer_line_y < y + 19:
        footer_line_y = y + 19
    if footer_line_y >= footer_text_y:
        footer_line_y = footer_text_y - 1
    if footer_line_y < y:
        return int(fallback_line_y), int(fallback_text_y)

    return int(footer_line_y), int(footer_text_y)


def ui_overlay_layout_centered(
    box_w: int,
    box_h: int,
    header_text_offset_y: int,
    body_top_offset_y: int,
    slot_count: int,
    slot_weights: tuple[int, ...],
    slot_nav: int,
    slot_confirm: int,
    slot_cancel: int,
    footer_pad_profile: FooterPadProfileId = 0,
    footer_line_gap: int = 4,
    screen_w: int = 240,
    screen_h: int = 136
) -> OverlayLayout:
    x = int((int(screen_w) - int(box_w)) * 0.5)
    y = int((int(screen_h) - int(box_h)) * 0.5)
    return {
        "box_x": x,
        "box_y": y,
        "box_w": int(box_w),
        "box_h": int(box_h),
        "header_text_y": y + int(header_text_offset_y),
        "body_top": y + int(body_top_offset_y),
        "footer_pad_profile": int(footer_pad_profile),
        "footer_line_gap": int(footer_line_gap),
        "slot_count": int(slot_count),
        "slot_weights": slot_weights,
        "slot_nav": int(slot_nav),
        "slot_confirm": int(slot_confirm),
        "slot_cancel": int(slot_cancel)
    }


def ui_overlay_layout_centered_by_spec(
    layout_spec: OverlayCenteredSpec,
    slot_count: int,
    slot_weights: tuple[int, ...],
    slot_nav: int,
    slot_confirm: int,
    slot_cancel: int,
    footer_pad_profile: FooterPadProfileId = 0,
    footer_line_gap: int = 4,
    screen_w: int = 240,
    screen_h: int = 136
) -> OverlayLayout:
    return ui_overlay_layout_centered(
        int(layout_spec[0]),
        int(layout_spec[1]),
        int(layout_spec[2]),
        int(layout_spec[3]),
        slot_count,
        slot_weights,
        slot_nav,
        slot_confirm,
        slot_cancel,
        footer_pad_profile,
        footer_line_gap,
        screen_w,
        screen_h
    )


def ui_overlay_footer_slot_geometry(
    layout: OverlayLayout,
    slot_count: int,
    footer_line_y: int,
    footer_text_y: int
) -> tuple[list[int], list[int], int, int]:
    inner_x = ui_overlay_layout_int(layout, "box_x", 20) + 4
    inner_w = ui_overlay_layout_int(layout, "box_w", 200) - 8
    weights = ui_overlay_layout_slot_weights(layout, slot_count)
    total_weight = 0
    i = 0
    while i < len(weights):
        total_weight += int(weights[i])
        i += 1
    if total_weight < 1:
        total_weight = slot_count

    slot_starts: list[int] = []
    slot_ends: list[int] = []
    acc = 0
    i = 0
    while i < slot_count:
        slot_x0 = inner_x + int(inner_w * acc / total_weight)
        acc += int(weights[i])
        slot_x1 = inner_x + int(inner_w * acc / total_weight)
        slot_starts.append(slot_x0)
        slot_ends.append(slot_x1)
        i += 1

    # Keep a visual gap before footer content via `footer_text_y`, but
    # hover/active fill should start right under the separator line.
    button_bg_y = footer_line_y + 1
    button_bg_h = footer_text_y + 8 - button_bg_y
    if button_bg_h < 1:
        button_bg_h = 1
    return slot_starts, slot_ends, button_bg_y, button_bg_h


def ui_overlay_footer_slot_at(
    layout: OverlayLayout,
    slots: list[str],
    mx: int,
    my: int,
    footer_line_y: int,
    footer_text_y: int
) -> int:
    slot_count = ui_overlay_layout_slot_count(layout)
    slot_starts, slot_ends, button_bg_y, button_bg_h = ui_overlay_footer_slot_geometry(
        layout,
        slot_count,
        footer_line_y,
        footer_text_y
    )
    i = 0
    while i < slot_count:
        if i >= len(slots):
            return -1
        if slots[i] == "":
            i += 1
            continue
        x0 = slot_starts[i]
        x1 = slot_ends[i]
        if mx >= x0 and mx < x1 and my >= button_bg_y and my < button_bg_y + button_bg_h:
            return i
        i += 1
    return -1
