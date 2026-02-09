from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import line

    from ...core.palette import ColorId


class Particles2D:
    """Очень простой буфер частиц для DRIVE (screen-space).

    Ограничения/цели:
    - без спрайтов: рисуем пиксели/короткие линии
    - без аллокаций на каждом кадре: используем ring-buffer через pop(0) при переполнении
    - частицы живут в screen-space, но мы можем “двигать мир”, сдвигая их на world_dx/world_dy

    Частица хранится как:
      (x, y, dx, dy, vx, vy, life, color)

    Где:
    - (x, y) — позиция
    - (dx, dy) — короткий отрезок от (x, y) до (x+dx, y+dy) (0,0 => точка)
    - (vx, vy) — собственная скорость частицы (в пикселях/сек)
    - life — сколько кадров осталось жить
    - color — индекс палитры 0..15
    """

    def __init__(self, max_particles: int) -> None:
        self._max = int(max_particles)
        # В буфере храним color как int (в рантайме это индекс палитры).
        # ColorId используем только на уровне API/подсказок редактора.
        self._items: list[tuple[float, float, float,
                                float, float, float, int, int]] = []

    def clear(self) -> None:
        self._items = []

    def count(self) -> int:
        return len(self._items)

    def spawn(
        self,
        x: float,
        y: float,
        dx: float,
        dy: float,
        vx: float,
        vy: float,
        life_frames: int,
        color: ColorId
    ) -> None:
        if self._max > 0 and len(self._items) >= self._max:
            # Сбрасываем самый старый.
            self._items.pop(0)
        self._items.append(
            (x, y, dx, dy, vx, vy, int(life_frames), color))

    def update(self, dt: float, world_dx: float, world_dy: float) -> None:
        """Обновляет частицы.

        `world_dx/world_dy` — сдвиг мира в screen-space за этот кадр.
        """
        i = 0
        while i < len(self._items):
            x, y, dx, dy, vx, vy, life, color = self._items[i]
            if life <= 0:
                self._items.pop(i)
                continue

            x += world_dx + vx * dt
            y += world_dy + vy * dt
            life -= 1

            self._items[i] = (x, y, dx, dy, vx, vy, life, color)
            i += 1

    def draw(self) -> None:
        """Рисует все частицы."""
        i = 0
        while i < len(self._items):
            x, y, dx, dy, vx, vy, life, color = self._items[i]
            x0 = int(x)
            y0 = int(y)
            x1 = int(x + dx)
            y1 = int(y + dy)
            line(x0, y0, x1, y1, color)
            i += 1
