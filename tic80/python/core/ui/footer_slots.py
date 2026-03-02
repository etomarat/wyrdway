from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..controls.actions import ActionId
    from .overlay_layout import (
        OverlayLayout,
        ui_overlay_layout_slot_index
    )
    from .prompts import (
        PromptState,
        ui_prompt_for_action,
        ui_prompt_for_nav_hint,
        ui_prompt_with_text
    )
else:
    OverlayLayout = dict
    ActionId = int


def ui_footer_slot_indices(
    layout: OverlayLayout,
    slot_count: int
) -> tuple[int, int, int]:
    slot_nav = ui_overlay_layout_slot_index(layout, "slot_nav", 0, slot_count)
    slot_confirm = ui_overlay_layout_slot_index(layout, "slot_confirm", 2, slot_count)
    slot_cancel = ui_overlay_layout_slot_index(
        layout,
        "slot_cancel",
        slot_count - 1,
        slot_count
    )
    return slot_nav, slot_confirm, slot_cancel


def ui_footer_empty_slots(slot_count: int) -> list[str]:
    slots: list[str] = []
    i = 0
    while i < int(slot_count):
        slots.append("")
        i += 1
    return slots


def ui_footer_slots_standard(
    layout: OverlayLayout,
    slot_count: int,
    state: PromptState,
    confirm_action: ActionId,
    cancel_action: ActionId,
    nav_enabled: bool,
    nav_label: str,
    confirm_label: str,
    cancel_label: str
) -> list[str]:
    slots = ui_footer_empty_slots(slot_count)
    slot_nav, slot_confirm, slot_cancel = ui_footer_slot_indices(layout, slot_count)
    if confirm_label != "":
        confirm_prompt = ui_prompt_for_action(state, confirm_action)
        slots[slot_confirm] = ui_prompt_with_text(confirm_prompt, confirm_label)
    if cancel_label != "":
        cancel_prompt = ui_prompt_for_action(state, cancel_action)
        slots[slot_cancel] = ui_prompt_with_text(cancel_prompt, cancel_label)
    if nav_enabled:
        nav_prompt = ui_prompt_for_nav_hint(state)
        slots[slot_nav] = ui_prompt_with_text(nav_prompt, nav_label)
    return slots


def ui_footer_slots_single_action(
    layout: OverlayLayout,
    state: PromptState,
    action: ActionId,
    label: str
) -> tuple[list[str], int]:
    slot_count = 1
    slots = ui_footer_slots_standard(
        layout,
        slot_count,
        state,
        action,
        action,
        False,
        "",
        label,
        ""
    )
    _slot_nav, slot_confirm, _slot_cancel = ui_footer_slot_indices(layout, slot_count)
    return slots, slot_confirm


def ui_footer_slots_confirm_cancel(
    layout: OverlayLayout,
    state: PromptState,
    confirm_action: ActionId,
    cancel_action: ActionId,
    confirm_label: str,
    cancel_label: str
) -> tuple[list[str], int, int]:
    slot_count = 2
    slots = ui_footer_slots_standard(
        layout,
        slot_count,
        state,
        confirm_action,
        cancel_action,
        False,
        "",
        confirm_label,
        cancel_label
    )
    _slot_nav, slot_confirm, slot_cancel = ui_footer_slot_indices(layout, slot_count)
    return slots, slot_confirm, slot_cancel
