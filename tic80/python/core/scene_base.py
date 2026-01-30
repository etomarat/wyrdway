from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from tic80 import *


class Scene(Protocol):
    """Контракт сцены в режиме Replace: одна активная сцена за кадр."""

    def enter(self, params: object | None = None) -> None:
        """Вызывается при активации сцены."""

    def update(self, dt: float) -> None:
        """Логика кадра (ввод/состояние)."""

    def draw(self) -> None:
        """Отрисовка сцены."""

    def exit(self) -> None:
        """Очистка при выходе из сцены."""
