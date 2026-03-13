from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Sequence

    from ..controls.actions import ActionId
    from ..controls.input import Controls
else:
    ActionId = int
    Controls = object


class UiReleaseLatch:
    def __init__(self) -> None:
        self._was_down: dict[int, bool] = {}
        self._armed: dict[int, bool] = {}

    def reset(self) -> None:
        self._was_down = {}
        self._armed = {}

    def sync_action(self, action: ActionId, is_down: bool) -> None:
        action_id = int(action)
        down = bool(is_down)
        self._was_down[action_id] = down
        self._armed[action_id] = not down

    def sync_actions_from_controls(
        self,
        controls: Controls,
        actions: "Sequence[ActionId]",
        context_token: int = 0
    ) -> None:
        i = 0
        while i < len(actions):
            action = actions[i]
            self.sync_action(
                action,
                self._controls_down(controls, action, context_token)
            )
            i += 1

    def released(self, action: ActionId, is_down: bool) -> bool:
        action_id = int(action)
        down = bool(is_down)
        was_down = bool(self._was_down.get(action_id, False))
        armed = bool(self._armed.get(action_id, True))
        released = False
        if not armed:
            if not down:
                armed = True
        elif was_down and not down:
            released = True
        self._was_down[action_id] = down
        self._armed[action_id] = armed
        return released

    def poll(
        self,
        controls: Controls,
        action: ActionId,
        context_token: int = 0
    ) -> bool:
        return self.released(
            action,
            self._controls_down(controls, action, context_token)
        )

    @staticmethod
    def _controls_down(
        controls: Controls,
        action: ActionId,
        context_token: int
    ) -> bool:
        if int(context_token) != 0:
            return bool(controls.down_for(action, context_token))
        return bool(controls.down(action))
