from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Sequence

    from ..controls.actions import ActionId
    from ..controls.input import Controls
    from .overlay_layout import (
        OverlayLayout,
        ui_overlay_footer_positions
    )
    from .footer_mouse import (
        OverlayFooterMouseState,
        UiMouseState,
        ui_overlay_footer_slot_states
    )
    from .release_latch import UiReleaseLatch
else:
    ActionId = int
    Controls = object
    OverlayLayout = dict


class UiOverlayRuntime:
    def __init__(self) -> None:
        self.release = UiReleaseLatch()
        self.mouse = UiMouseState()
        self.footer_mouse = OverlayFooterMouseState()

    def sync_actions(self, controls: Controls, actions: list[ActionId]) -> None:
        self.release.sync_actions_from_controls(controls, actions)

    def poll_mouse(self) -> None:
        self.mouse.poll()

    def poll_action(self, controls: Controls, action: ActionId) -> bool:
        return self.release.poll(controls, action)

    def poll_actions(self, controls: Controls, actions: list[ActionId]) -> list[bool]:
        out: list[bool] = []
        i = 0
        while i < len(actions):
            out.append(self.release.poll(controls, actions[i]))
            i += 1
        return out

    def reset_footer(self) -> None:
        self.footer_mouse.reset()

    def poll_footer_release(self, layout: OverlayLayout, slots: list[str]) -> int:
        footer_line_y, footer_text_y = ui_overlay_footer_positions(
            layout,
            104,
            108
        )
        return self.footer_mouse.poll_release(
            layout,
            slots,
            self.mouse,
            footer_line_y,
            footer_text_y
        )

    def slot_states(
        self,
        slot_count: int,
        keyboard_active: Sequence[bool]
    ) -> tuple[list[bool], list[bool]]:
        return ui_overlay_footer_slot_states(
            slot_count,
            keyboard_active,
            self.mouse,
            self.footer_mouse
        )
