from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Sequence

    from ..controls.actions import ActionId
    from ..controls.input import Controls
    from ..game_state import GameState
    from .footer_mouse import UiMouseState
    from .overlay_layout import OverlayLayout
    from .overlay_runtime import UiOverlayRuntime
else:
    ActionId = int
    Controls = object
    GameState = object


class UiInputLayer:
    def __init__(self) -> None:
        self.runtime = UiOverlayRuntime()
        self._context_token = 0

    @property
    def context_token(self) -> int:
        return int(self._context_token)

    @property
    def mouse(self) -> UiMouseState:
        return self.runtime.mouse

    def activate(
        self,
        controls: Controls,
        actions: "Sequence[ActionId]",
        swallow_held: bool = True,
        reset_footer: bool = True
    ) -> int:
        self._context_token = controls.enter_context(actions, swallow_held)
        self.runtime.sync_actions(
            controls,
            actions,
            self._context_token
        )
        if reset_footer:
            self.runtime.reset_footer()
        return int(self._context_token)

    def poll_mouse(self) -> None:
        self.runtime.poll_mouse()

    def reset_footer(self) -> None:
        self.runtime.reset_footer()

    def poll_footer_release(self, layout: OverlayLayout, slots: list[str]) -> int:
        return self.runtime.poll_footer_release(layout, slots)

    def poll_footer_button_release(
        self,
        state: GameState,
        layout: OverlayLayout,
        slots: list[str]
    ) -> int:
        return self.runtime.poll_footer_button_release(state, layout, slots)

    def footer_button_released(
        self,
        state: GameState,
        released_slot: int,
        slot_index: int
    ) -> bool:
        return self.runtime.footer_button_released(
            state,
            released_slot,
            slot_index
        )

    def down(self, controls: Controls, action: ActionId) -> bool:
        return bool(controls.down_for(action, self._context_token))

    def pressed(
        self,
        controls: Controls,
        action: ActionId,
        hold: int = -1,
        period: int = -1
    ) -> bool:
        return bool(
            controls.pressed_for(
                action,
                self._context_token,
                hold,
                period
            )
        )

    def poll_action(self, controls: Controls, action: ActionId) -> bool:
        return self.runtime.poll_action(
            controls,
            action,
            self._context_token
        )

    def poll_actions(
        self,
        controls: Controls,
        actions: "Sequence[ActionId]"
    ) -> list[bool]:
        return self.runtime.poll_actions(
            controls,
            actions,
            self._context_token
        )

    def poll_confirm(self, state: GameState, controls: Controls) -> bool:
        return self.runtime.poll_confirm(
            state,
            controls,
            self._context_token
        )

    def poll_cancel(self, state: GameState, controls: Controls) -> bool:
        return self.runtime.poll_cancel(
            state,
            controls,
            self._context_token
        )

    def sync_actions(
        self,
        controls: Controls,
        actions: "Sequence[ActionId]"
    ) -> None:
        self.runtime.sync_actions(
            controls,
            actions,
            self._context_token
        )
