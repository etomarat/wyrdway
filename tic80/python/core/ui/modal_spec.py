from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..controls.actions import ActionId
    from ..controls.input import Controls
    from .footer_slots import ui_footer_slot_indices, ui_footer_slots_standard
    from .overlay_layout import OverlayLayout
    from .prompts import PromptState
else:
    ActionId = int
    OverlayLayout = dict


class UiModalNavMode:
    NEVER = 0
    ALWAYS = 1
    SCROLL = 2


class UiModalFooterSpec:
    __slots__ = (
        "confirm_action",
        "cancel_action",
        "nav_mode",
        "nav_label",
        "confirm_label",
        "cancel_label"
    )

    def __init__(
        self,
        confirm_action: ActionId,
        cancel_action: ActionId,
        nav_mode: int,
        nav_label: str,
        confirm_label: str,
        cancel_label: str
    ) -> None:
        self.confirm_action: ActionId = confirm_action
        self.cancel_action: ActionId = cancel_action
        self.nav_mode = int(nav_mode)
        self.nav_label = str(nav_label)
        self.confirm_label = str(confirm_label)
        self.cancel_label = str(cancel_label)


class UiModalSpec:
    __slots__ = (
        "title",
        "layout",
        "footer"
    )

    def __init__(
        self,
        title: str,
        layout: OverlayLayout,
        footer: UiModalFooterSpec
    ) -> None:
        self.title = str(title)
        self.layout = layout
        self.footer = footer


def ui_modal_nav_enabled(nav_mode: int, has_scroll: bool) -> bool:
    mode = int(nav_mode)
    if mode == int(UiModalNavMode.ALWAYS):
        return True
    if mode == int(UiModalNavMode.NEVER):
        return False
    return has_scroll


def ui_modal_footer_slots(
    layout: OverlayLayout,
    slot_count: int,
    state: PromptState,
    footer: UiModalFooterSpec,
    nav_enabled: bool
) -> list[str]:
    return ui_footer_slots_standard(
        layout,
        slot_count,
        state,
        footer.confirm_action,
        footer.cancel_action,
        bool(nav_enabled),
        footer.nav_label,
        footer.confirm_label,
        footer.cancel_label
    )


def ui_modal_keyboard_active(
    layout: OverlayLayout,
    slot_count: int,
    controls: Controls,
    footer: UiModalFooterSpec,
    nav_enabled: bool,
    nav_down: bool,
    context_token: int = 0
) -> list[bool]:
    slot_nav, slot_confirm, slot_cancel = ui_footer_slot_indices(
        layout,
        slot_count
    )
    active: list[bool] = []
    i = 0
    while i < slot_count:
        active.append(False)
        i += 1
    if nav_enabled:
        active[slot_nav] = bool(nav_down)
    if int(context_token) != 0:
        active[slot_confirm] = controls.down_for(
            footer.confirm_action,
            context_token
        )
        active[slot_cancel] = controls.down_for(
            footer.cancel_action,
            context_token
        )
    else:
        active[slot_confirm] = controls.down(footer.confirm_action)
        active[slot_cancel] = controls.down(footer.cancel_action)
    return active
