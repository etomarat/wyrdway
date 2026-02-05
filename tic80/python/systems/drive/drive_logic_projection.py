from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import *

    from .drive_logic_core import DriveLogic


def drive_project_world_to_road_near_idx(
    self: DriveLogic,
    x: float,
    y: float,
    idx_guess: int
) -> tuple[float, float]:
    """Проецирует world точку (x,y) в координаты дороги (s,d) около idx_guess.

    Возвращает:
    - s: прогресс по дороге (float, может быть между дискретными шагами)
    - d: смещение вправо от centerline (положительное = справа)

    Примечание про idx_guess:
    - это индекс сэмпла centerline (дискретной линии дороги) из RoadModel,
      вокруг которого ищем ближайшую точку;
    - обычно это текущий `self._road_idx`, чтобы ограничить поиск локальным окном,
      не сканируя всю дорогу каждый кадр.
    """
    n = self._road.center_points_len()
    if n <= 0:
        return 0.0, 0.0

    start = idx_guess - 30
    end = idx_guess + 30
    if start < 0:
        start = 0
    if end > n - 1:
        end = n - 1

    best_i = start
    best_d2 = 1.0e30
    best_cx = 0.0
    best_cy = 0.0
    best_dx = 1.0
    best_dy = 0.0

    i = start
    while i <= end:
        cx, cy, dx, dy = self._road.center_point_at_index(i)
        ox = x - cx
        oy = y - cy
        d2 = ox * ox + oy * oy
        if d2 < best_d2:
            best_d2 = d2
            best_i = i
            best_cx = cx
            best_cy = cy
            best_dx = dx
            best_dy = dy
        i += 1

    # Локальные координаты относительно ближайшей точки centerline.
    ox = x - best_cx
    oy = y - best_cy
    s = best_i * self._road.ds + (ox * best_dx + oy * best_dy)

    right_x = -best_dy
    right_y = best_dx
    d = ox * right_x + oy * right_y
    return s, d


def drive_update_road_projection(self: DriveLogic) -> None:
    """Обновляет (road_s, road_d, offroad) по текущей world позиции.

    Идея:
    - ищем ближайшую точку centerline в окне индексов вокруг предыдущей,
      чтобы было быстро и стабильно;
    - d считаем как проекцию на нормаль “вправо” от дороги.
    """
    n = self._road.center_points_len()
    if n <= 0:
        self._road_s = 0.0
        self._road_d = 0.0
        self._offroad = False
        return

    idx0 = self._road_idx
    start = idx0 - 40
    end = idx0 + 80
    if start < 0:
        start = 0
    if end > n - 1:
        end = n - 1

    best_i = start
    best_d2 = 1.0e30
    best_cx = 0.0
    best_cy = 0.0
    best_dx = 1.0
    best_dy = 0.0

    i = start
    while i <= end:
        cx, cy, dx, dy = self._road.center_point_at_index(i)
        ox = self._x - cx
        oy = self._y - cy
        d2 = ox * ox + oy * oy
        if d2 < best_d2:
            best_d2 = d2
            best_i = i
            best_cx = cx
            best_cy = cy
            best_dx = dx
            best_dy = dy
        i += 1

    max_far = self._road.road_width * self._road.road_width * 64.0
    if best_d2 > max_far:
        best_i = 0
        best_d2 = 1.0e30
        i = 0
        while i < n:
            cx, cy, dx, dy = self._road.center_point_at_index(i)
            ox = self._x - cx
            oy = self._y - cy
            d2 = ox * ox + oy * oy
            if d2 < best_d2:
                best_d2 = d2
                best_i = i
                best_cx = cx
                best_cy = cy
                best_dx = dx
                best_dy = dy
            i += 1

    self._road_idx = best_i
    self._road_s = best_i * self._road.ds

    # Важно: знак `road_d` должен совпадать со знаком `d` у объектов дороги (Obstacle/Zone).
    #
    # Для world позиции объектов мы используем нормаль `nrm = (-dir_y, dir_x)`:
    #   world = center + nrm * d
    #
    # Поэтому и `road_d` считаем по той же оси `nrm`, иначе всё “зеркалится”:
    # зона/препятствие рисуются справа, а `road_d` говорит, что это слева.
    right_x = -best_dy
    right_y = best_dx
    self._road_d = (self._x - best_cx) * right_x + \
        (self._y - best_cy) * right_y

    width = self._road.width_at(self._road_s)
    self._offroad = abs(self._road_d) > (width * 0.5)


def drive_hitbox_world_circles(self: DriveLogic) -> tuple[float, float, float, float, float, float]:
    """Возвращает 2 круговых хитбокса в world-space: rear(x,y,r), front(x,y,r).

    Хитбоксы задаются в пикселях спрайта (см. tuning hitbox_*_px/py) и затем
    преобразуются в локальные оффсеты относительно car_sprite_anchor_*:
      right_offset = (hitbox_px - anchor_x)
      fwd_offset = -(hitbox_py - anchor_y)

    Затем оффсеты переводятся в world-space через (fwd/right) машины.
    """
    d = self._tuning.DRIVE

    ax = d.car_sprite_anchor_x
    ay = d.car_sprite_anchor_y

    rear_px = d.hitbox_rear_px
    rear_py = d.hitbox_rear_py
    front_px = d.hitbox_front_px
    front_py = d.hitbox_front_py

    rear_right = rear_px - ax
    rear_fwd = -(rear_py - ay)
    front_right = front_px - ax
    front_fwd = -(front_py - ay)

    fwd_x = self._fwd_x
    fwd_y = self._fwd_y
    right_x = -fwd_y
    right_y = fwd_x

    x = self._x
    y = self._y

    rear_x = x + fwd_x * rear_fwd + right_x * rear_right
    rear_y = y + fwd_y * rear_fwd + right_y * rear_right
    front_x = x + fwd_x * front_fwd + right_x * front_right
    front_y = y + fwd_y * front_fwd + right_y * front_right

    rear_r = d.hitbox_rear_radius
    front_r = d.hitbox_front_radius
    if rear_r < 0.0:
        rear_r = 0.0
    if front_r < 0.0:
        front_r = 0.0

    return rear_x, rear_y, rear_r, front_x, front_y, front_r


def drive_hitbox_road_circles(self: DriveLogic) -> tuple[float, float, float, float, float, float]:
    """Возвращает 2 круговых хитбокса машины (rear/front) в road-space.

    Формат: (rear_s, rear_d, rear_r, front_s, front_d, front_r).

    Зачем это нужно:
    - зоны/препятствия живут в координатах дороги (s вдоль, d поперёк);
    - игрок ориентируется по спрайту, а хитбоксы настроены под спрайт;
    - значит, пересечения с зонами должны проверяться по хитбоксам, а не по
      “центральной точке физики”.

    Реализация:
    - берём world позиции кругов,
    - отдельно проецируем каждую точку на ближайшую часть centerline в окне
      вокруг текущего `road_idx`.

    Примечание: это стабильнее, чем “локально-линейная” проекция через одну
    касательную в `road_s`, и лучше совпадает с тем, что игрок видит в кадре.
    """
    rear_x, rear_y, rear_r, front_x, front_y, front_r = drive_hitbox_world_circles(
        self)
    idx0 = self._road_idx
    rear_s, rear_d = drive_project_world_to_road_near_idx(
        self, rear_x, rear_y, idx0)
    front_s, front_d = drive_project_world_to_road_near_idx(
        self, front_x, front_y, idx0)
    return rear_s, rear_d, rear_r, front_s, front_d, front_r
