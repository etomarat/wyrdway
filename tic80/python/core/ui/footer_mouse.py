from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import mouse

    from .overlay_layout import OverlayLayout, ui_overlay_footer_slot_at
    from typing import Sequence
else:
    OverlayLayout = dict


class UiMouseState:
    def __init__(self) -> None:
        self.x = 0
        self.y = 0
        self.left_down = False
        self.left_pressed = False
        self.left_released = False
        self.right_down = False
        self.right_pressed = False
        self.right_released = False
        self.scroll_y = 0

    def poll(self) -> None:
        mx, my, left_btn, _mid_btn, right_btn, _scroll_x, scroll_y = mouse()
        left_now = bool(left_btn)
        self.left_pressed = left_now and (not self.left_down)
        self.left_released = (not left_now) and self.left_down
        self.left_down = left_now

        right_now = bool(right_btn)
        self.right_pressed = right_now and (not self.right_down)
        self.right_released = (not right_now) and self.right_down
        self.right_down = right_now

        self.x = int(mx)
        self.y = int(my)
        self.scroll_y = int(scroll_y)


class OverlayFooterMouseState:
    def __init__(self) -> None:
        self.hover_slot = -1
        self.down_slot = -1

    def reset(self) -> None:
        self.hover_slot = -1
        self.down_slot = -1

    def poll_release(
        self,
        layout: OverlayLayout,
        slots: list[str],
        mouse_state: UiMouseState,
        footer_line_y: int,
        footer_text_y: int
    ) -> int:
        self.hover_slot = ui_overlay_footer_slot_at(
            layout,
            slots,
            mouse_state.x,
            mouse_state.y,
            footer_line_y,
            footer_text_y
        )
        if mouse_state.left_pressed:
            self.down_slot = self.hover_slot
        if mouse_state.left_released:
            released_slot = -1
            if self.down_slot >= 0 and self.down_slot == self.hover_slot:
                released_slot = self.hover_slot
            self.down_slot = -1
            return released_slot
        if not mouse_state.left_down:
            self.down_slot = -1
        return -1

    def is_slot_active(self, slot_index: int, mouse_state: UiMouseState) -> bool:
        return (
            mouse_state.left_down
            and self.down_slot == int(slot_index)
            and self.hover_slot == int(slot_index)
        )


def ui_overlay_footer_slot_states(
    slot_count: int,
    keyboard_active: Sequence[bool],
    mouse_state: UiMouseState,
    footer_mouse: OverlayFooterMouseState
) -> tuple[list[bool], list[bool]]:
    active: list[bool] = []
    hover: list[bool] = []
    i = 0
    while i < int(slot_count):
        key_active = False
        if i < len(keyboard_active):
            key_active = bool(keyboard_active[i])
        is_active = key_active or footer_mouse.is_slot_active(i, mouse_state)
        active.append(is_active)
        hover.append((not is_active) and footer_mouse.hover_slot == i)
        i += 1
    return active, hover
