from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..controls.actions import ActionId
    from .footer_slots import (
        ui_footer_slots_confirm_cancel,
        ui_footer_slots_single_action
    )
    from .overlay_layout import (
        OverlayCenteredSpec,
        OverlayLayout,
        ui_overlay_layout_centered_by_spec
    )
    from .prompts import PromptState
else:
    ActionId = int
    OverlayLayout = dict
    OverlayCenteredSpec = tuple


def ui_overlay_flow_single_action(
    layout_spec: OverlayCenteredSpec,
    state: PromptState,
    action: ActionId,
    label: str
) -> tuple[OverlayLayout, list[str], int]:
    layout = ui_overlay_layout_centered_by_spec(
        layout_spec,
        1,
        (1,),
        0,
        0,
        0
    )
    slots, slot_confirm = ui_footer_slots_single_action(
        layout,
        state,
        action,
        label
    )
    return layout, slots, slot_confirm


def ui_overlay_flow_confirm_cancel(
    layout_spec: OverlayCenteredSpec,
    state: PromptState,
    confirm_action: ActionId,
    cancel_action: ActionId,
    confirm_label: str,
    cancel_label: str
) -> tuple[OverlayLayout, list[str], int, int]:
    layout = ui_overlay_layout_centered_by_spec(
        layout_spec,
        2,
        (1, 1),
        0,
        0,
        1
    )
    slots, slot_confirm, slot_cancel = ui_footer_slots_confirm_cancel(
        layout,
        state,
        confirm_action,
        cancel_action,
        confirm_label,
        cancel_label
    )
    return layout, slots, slot_confirm, slot_cancel
