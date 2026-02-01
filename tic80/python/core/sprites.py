from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import spr


class SpriteSpec:
    """Описание спрайта на спрайт-листе TIC-80.

    В TIC-80 базовый спрайт — 8×8. Большие спрайты рисуются через `spr()` с
    параметрами `w/h` (в тайлах).

    Поля:
    - `base_id`: id левого верхнего тайла.
    - `tile_w`, `tile_h`: размер в тайлах 8×8.
    - `colorkey`: цвет-ключ прозрачности (в TIC-80 нет alpha).
    """

    def __init__(self, base_id: int, tile_w: int, tile_h: int, colorkey: int) -> None:
        self.base_id = base_id
        self.tile_w = tile_w
        self.tile_h = tile_h
        self.colorkey = colorkey

    def draw(self, x: int, y: int, scale: int = 1, flip: int = 0, rotate: int = 0) -> None:
        """Рисует спрайт в точке (x, y).

        Важно: все параметры передаются позиционно — TIC-80 API функции чаще
        всего не поддерживают keyword-аргументы.
        """
        spr(self.base_id, x, y, self.colorkey, scale,
            flip, rotate, self.tile_w, self.tile_h)


class TopdownVehicleSprites:
    """Набор кадров машины для top-down вида.

    Сейчас поддерживаем минимальный набор под m1.5:
    - forward / left / right

    Поворот здесь — это не физический поворот по heading, а визуальный кадр под
    нажатие руля. Это работает хорошо, если камера ориентирована по направлению
    дороги (road-forward вверх экрана).
    """

    def __init__(self, forward: SpriteSpec, left: SpriteSpec, right: SpriteSpec) -> None:
        self._forward = forward
        self._left = left
        self._right = right

    def draw(self, steer_input: int, x: int, y: int) -> None:
        """Рисует подходящий кадр по `steer_input` (-1/0/+1)."""
        if steer_input < 0:
            self._left.draw(x, y)
            return
        if steer_input > 0:
            self._right.draw(x, y)
            return
        self._forward.draw(x, y)


# Машина “Нива” (top-down, 32×32):
# - страницы/адреса фиксируем в `docs/30_style/1_sprite_sheet_layout.md`.
# - пока считаем, что colorkey = 0.
_NIVA_TILE_W = 4
_NIVA_TILE_H = 4
_NIVA_COLORKEY = 12  # white

NIVA_TOPDOWN = TopdownVehicleSprites(
    SpriteSpec(320, _NIVA_TILE_W, _NIVA_TILE_H, _NIVA_COLORKEY),
    SpriteSpec(324, _NIVA_TILE_W, _NIVA_TILE_H, _NIVA_COLORKEY),
    SpriteSpec(328, _NIVA_TILE_W, _NIVA_TILE_H, _NIVA_COLORKEY)
)
