from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class FxLayer:
    UNDER_CAR = 0
    OVER_CAR = 1
    WORLD = 2
    UI = 3


class FxSystem:
    def update(self, dt: float, world_dx: float, world_dy: float) -> None:
        return

    def draw(self) -> None:
        return

    def alive(self) -> bool:
        return True


class FxManager:
    def __init__(self) -> None:
        self._layers: dict[int, list[FxSystem]] = {}

    def clear(self) -> None:
        self._layers = {}

    def add(self, layer: int, system: FxSystem) -> None:
        items = self._layers.get(layer)
        if items is None:
            items = []
            self._layers[layer] = items
        items.append(system)

    def update(self, dt: float, world_dx: float, world_dy: float) -> None:
        for layer in self._layers:
            items = self._layers[layer]
            i = 0
            while i < len(items):
                s = items[i]
                s.update(dt, world_dx, world_dy)
                if not s.alive():
                    items.pop(i)
                    continue
                i += 1

    def draw(self, layer: int) -> None:
        items = self._layers.get(layer)
        if items is None:
            return
        i = 0
        while i < len(items):
            items[i].draw()
            i += 1

