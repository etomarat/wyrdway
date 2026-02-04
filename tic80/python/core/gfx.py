from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import line


def gfx_line(x0, y0, x1, y1, color) -> None:
    """Простейшая обёртка над TIC-80 line().

    Для совместимости со старыми export-рантаймами не делаем дополнительных
    преобразований типов и не используем try/except каскад.
    """
    line(x0, y0, x1, y1, color)
