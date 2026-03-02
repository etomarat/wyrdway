from typing import TYPE_CHECKING

if TYPE_CHECKING:
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
        actions: list[ActionId]
    ) -> None:
        i = 0
        while i < len(actions):
            action = actions[i]
            self.sync_action(action, bool(controls.down(action)))
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

    def poll(self, controls: Controls, action: ActionId) -> bool:
        return self.released(action, bool(controls.down(action)))
