from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable
    from .fx_manager import FxSystem

    FxFactory = Callable[[object], FxSystem]
else:
    FxFactory = object


class FxRegistry:
    def __init__(self) -> None:
        self._factories: dict[int, FxFactory] = {}
        self._labels: dict[int, str] = {}

    def register(self, fx_id: int, factory: FxFactory, label: str) -> None:
        self._factories[fx_id] = factory
        self._labels[fx_id] = label

    def label(self, fx_id: int) -> str:
        s = self._labels.get(fx_id)
        return s if s is not None else ("fx#" + str(fx_id))

    def spawn(self, fx_id: int, params: object) -> FxSystem | None:
        f = self._factories.get(fx_id)
        if f is None:
            return None
        # factory is a callable: (params) -> FxSystem
        return f(params)
