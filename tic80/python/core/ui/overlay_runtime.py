from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Sequence

    from ..controls.actions import ActionId
    from ..controls.input import Controls
    from ..game_state import GameState
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
    GameState = object
    OverlayLayout = dict


class UiOverlayRuntime:
    _ACTION_CONFIRM = 0
    _ACTION_CANCEL = 1

    def __init__(self) -> None:
        self.release = UiReleaseLatch()
        self.mouse = UiMouseState()
        self.footer_mouse = OverlayFooterMouseState()

    def sync_actions(
        self,
        controls: Controls,
        actions: "Sequence[ActionId]",
        context_token: int = 0
    ) -> None:
        self.release.sync_actions_from_controls(controls, actions, context_token)

    def poll_mouse(self) -> None:
        self.mouse.poll()

    def poll_action(
        self,
        controls: Controls,
        action: ActionId,
        context_token: int = 0
    ) -> bool:
        return self.release.poll(controls, action, context_token)

    def poll_button_action(
        self,
        state: GameState,
        controls: Controls,
        action: ActionId,
        context_token: int = 0
    ) -> bool:
        released = self.release.poll(controls, action, context_token)
        if released:
            state.vibe_ui_button()
        return released

    def poll_confirm(
        self,
        state: GameState,
        controls: Controls,
        context_token: int = 0
    ) -> bool:
        return self.poll_button_action(
            state,
            controls,
            self._ACTION_CONFIRM,
            context_token
        )

    def poll_cancel(
        self,
        state: GameState,
        controls: Controls,
        context_token: int = 0
    ) -> bool:
        return self.poll_button_action(
            state,
            controls,
            self._ACTION_CANCEL,
            context_token
        )

    def poll_actions(
        self,
        controls: Controls,
        actions: "Sequence[ActionId]",
        context_token: int = 0
    ) -> list[bool]:
        out: list[bool] = []
        i = 0
        while i < len(actions):
            out.append(self.release.poll(controls, actions[i], context_token))
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

    def poll_footer_button_release(
        self,
        state: GameState,
        layout: OverlayLayout,
        slots: list[str]
    ) -> int:
        released_slot = self.poll_footer_release(layout, slots)
        if released_slot >= 0:
            state.vibe_ui_button()
        return released_slot

    def footer_button_released(
        self,
        state: GameState,
        released_slot: int,
        slot_index: int
    ) -> bool:
        if int(released_slot) != int(slot_index):
            return False
        state.vibe_ui_button()
        return True

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
