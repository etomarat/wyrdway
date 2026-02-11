from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable, Generic, TypeVar

    from .fx_manager import FxSystem

    P = TypeVar("P")
else:
    class _CallableCompat:
        @classmethod
        def __class_getitem__(cls, _item: object):
            return object

    class _GenericCompat:
        @classmethod
        def __class_getitem__(cls, _item: object):
            return cls

    Callable = _CallableCompat
    Generic = _GenericCompat
    FxSystem = object
    P = object


class FxRegistry(Generic[P]):
    def __init__(self) -> None:
        self._factories: dict[int, Callable[[P], FxSystem]] = {}
        self._labels: dict[int, str] = {}

    def register(self, fx_id: int, factory: Callable[[P], FxSystem], label: str) -> None:
        self._factories[fx_id] = factory
        self._labels[fx_id] = label

    def label(self, fx_id: int) -> str:
        s = self._labels.get(fx_id)
        return s if s is not None else ("fx#" + str(fx_id))

    def spawn(self, fx_id: int, params: P) -> FxSystem | None:
        f = self._factories.get(fx_id)
        if f is None:
            return None
        return f(params)
