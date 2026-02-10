# title:  vand particles pack
# author: vand
# desc:   a set of beautiful particles ready to be used on any project!!!
#
# NOTE: Ported from Lua to TIC-80 Python (PocketPy) for Wyrdway.

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tic80 import circ, circb, line, tri

    from ..fx_manager import FxSystem
    from ...drive.rng import Rng

import math


class _VandParticle:
    def update(self, dt: float, world_dx: float, world_dy: float, frame: int, rng: Rng) -> bool:
        return True

    def draw(self) -> None:
        return


class _TriParticle(_VandParticle):
    def __init__(self, x: float, y: float, r: float, rng: Rng) -> None:
        ang = rng.uniform(0.0, math.pi * 2.0)
        self.x = x
        self.y = y
        self.ang = rng.uniform(0.0, math.pi)
        self.angv = rng.uniform(-1.0, 1.0) * 2.0
        self.c = 4
        self.vx = math.cos(ang)
        self.vy = math.sin(ang)
        self.r = rng.uniform(0.0, r)
        self.t = 20.0

    def update(self, dt: float, world_dx: float, world_dy: float, frame: int, rng: Rng) -> bool:
        self.x += world_dx + self.vx
        self.y += world_dy + self.vy
        self.vx *= 0.95
        self.vy *= 0.95
        self.angv *= 0.9
        self.ang += self.angv
        if self.t < 5.0:
            self.r /= 1.1
            if frame % 5 == 0:
                if self.c > 1:
                    self.c -= 1
        self.t -= 1.0 + rng.uniform(0.0, 1.0)
        if self.r < 1.0:
            return True
        return False

    def draw(self) -> None:
        a = self.ang
        b = self.ang + (2.0 / 3.0) * math.pi
        c = self.ang + (4.0 / 3.0) * math.pi
        xa = math.cos(a)
        ya = math.sin(a)
        xb = math.cos(b)
        yb = math.sin(b)
        xc = math.cos(c)
        yc = math.sin(c)
        tri(
            self.x + xa * self.r,
            self.y + ya * self.r,
            self.x + xb * self.r,
            self.y + yb * self.r,
            self.x + xc * self.r,
            self.y + yc * self.r,
            self.c
        )


class _Tri2Particle(_VandParticle):
    def __init__(self, x: float, y: float, r: float, rng: Rng) -> None:
        ang = rng.uniform(0.0, math.pi * 2.0)
        force = 1.0 + rng.uniform(0.0, 1.0) * 0.5
        self.x = x
        self.y = y
        self.ang = ang
        self.c = 12
        self.vx = math.cos(ang) * force
        self.vy = math.sin(ang) * force
        self.r = rng.uniform(0.0, r)
        self.t = 20.0

    def update(self, dt: float, world_dx: float, world_dy: float, frame: int, rng: Rng) -> bool:
        self.x += world_dx + self.vx
        self.y += world_dy + self.vy
        self.vx *= 0.95
        self.vy *= 0.95
        if self.t < 10.0:
            self.r /= 1.1
            if frame % 5 == 0:
                if self.c < 15:
                    self.c += 1
        self.t -= 1.0 + rng.uniform(0.0, 1.0)
        if self.r < 1.0:
            return True
        return False

    def draw(self) -> None:
        a = self.ang
        b = self.ang + (2.0 / 3.0) * math.pi
        c = self.ang + (4.0 / 3.0) * math.pi
        xa = math.cos(a)
        ya = math.sin(a)
        xb = math.cos(b)
        yb = math.sin(b)
        xc = math.cos(c)
        yc = math.sin(c)
        tri(
            self.x + xa * self.r * 2.0,
            self.y + ya * self.r * 2.0,
            self.x + xb * self.r,
            self.y + yb * self.r,
            self.x + xc * self.r,
            self.y + yc * self.r,
            self.c
        )


class _PlusParticle(_VandParticle):
    def __init__(self, x: float, y: float, r: float, rng: Rng) -> None:
        self.x = x
        self.y = y
        self.ang = rng.uniform(0.0, math.pi)
        self.angv = rng.uniform(-1.0, 1.0) * 2.0
        self.c = 6
        ang = rng.uniform(0.0, math.pi * 2.0)
        self.vx = math.cos(ang)
        self.vy = math.sin(ang)
        self.r = rng.uniform(0.0, r)
        self.t = 20.0

    def update(self, dt: float, world_dx: float, world_dy: float, frame: int, rng: Rng) -> bool:
        self.x += world_dx + self.vx
        self.y += world_dy + self.vy
        self.vx *= 0.95
        self.vy *= 0.95
        self.angv *= 0.9
        self.ang += self.angv
        if self.t < 5.0:
            self.r /= 1.1
            if frame % 5 == 0:
                if self.c > 1:
                    self.c -= 1
        self.t -= 1.0 + rng.uniform(0.0, 1.0)
        if self.r < 1.0:
            return True
        return False

    def draw(self) -> None:
        a = self.ang
        b = self.ang + math.pi
        c = self.ang + math.pi / 2.0
        d = self.ang + (3.0 * math.pi) / 2.0
        xa = math.cos(a)
        ya = math.sin(a)
        xb = math.cos(b)
        yb = math.sin(b)
        xc = math.cos(c)
        yc = math.sin(c)
        xd = math.cos(d)
        yd = math.sin(d)
        line(
            int(self.x + xa * self.r),
            int(self.y + ya * self.r),
            int(self.x + xb * self.r),
            int(self.y + yb * self.r),
            self.c
        )
        line(
            int(self.x + xc * self.r),
            int(self.y + yc * self.r),
            int(self.x + xd * self.r),
            int(self.y + yd * self.r),
            self.c
        )


class _MarkerParticle(_VandParticle):
    def __init__(self, x: float, y: float, rng: Rng) -> None:
        self.x = x
        self.y = y
        self.p1 = 0.1
        self.p2 = 1.1
        self.ang = rng.uniform(0.0, math.pi * 2.0)
        self.c = 8
        self.t = 20.0

    def update(self, dt: float, world_dx: float, world_dy: float, frame: int, rng: Rng) -> bool:
        self.x += world_dx
        self.y += world_dy
        if self.t < 10.0:
            self.p1 /= 1.1
            self.p2 /= 1.08
            if frame % 20 == 0:
                if self.c < 11:
                    self.c += 1
        else:
            self.p1 += 1.0
            self.p2 += 1.2
        self.t -= 1.0 + rng.uniform(0.0, 1.0)
        if self.p2 < 2.0:
            return True
        return False

    def draw(self) -> None:
        xa = math.cos(self.ang)
        ya = math.sin(self.ang)
        line(
            int(self.x + xa * self.p1),
            int(self.y + ya * self.p1),
            int(self.x + xa * self.p2),
            int(self.y + ya * self.p2),
            self.c
        )


class _DustParticle(_VandParticle):
    def __init__(self, x: float, y: float, r: float, rng: Rng) -> None:
        ang = rng.uniform(0.0, math.pi) + math.pi
        self.x = x
        self.y = y
        self.c = 12
        self.ty = rng.uniform(-1.0, 1.0)
        self.vx = math.cos(ang)
        self.vy = math.sin(ang)
        self.r = rng.uniform(0.0, r)
        self.t = 20.0

    def update(self, dt: float, world_dx: float, world_dy: float, frame: int, rng: Rng) -> bool:
        self.x += world_dx + self.vx
        self.y += world_dy + self.vy
        self.vx *= 0.95
        self.vy *= 0.95
        if self.t < 5.0:
            self.r /= 1.1
            if frame % 10 == 0:
                if self.c < 15:
                    self.c += 1
        self.t -= 1.0 + rng.uniform(0.0, 1.0)
        if self.r < 1.0:
            return True
        return False

    def draw(self) -> None:
        if self.ty >= 0.0:
            circ(int(self.x), int(self.y), int(self.r), self.c)
        else:
            circb(int(self.x), int(self.y), int(self.r), 0)


class _DustDownParticle(_VandParticle):
    """Вариант dust, который "стелется" вниз (в +Y screen-space), а не вверх."""

    def __init__(self, x: float, y: float, r: float, rng: Rng) -> None:
        ang = rng.uniform(0.0, math.pi)
        self.x = x
        self.y = y
        self.c = 12
        self.ty = rng.uniform(-1.0, 1.0)
        self.vx = math.cos(ang)
        self.vy = math.sin(ang)
        self.r = rng.uniform(0.0, r)
        self.t = 20.0

    def update(self, dt: float, world_dx: float, world_dy: float, frame: int, rng: Rng) -> bool:
        self.x += world_dx + self.vx
        self.y += world_dy + self.vy
        self.vx *= 0.95
        self.vy *= 0.95
        if self.t < 5.0:
            self.r /= 1.1
            if frame % 10 == 0:
                if self.c < 15:
                    self.c += 1
        self.t -= 1.0 + rng.uniform(0.0, 1.0)
        if self.r < 1.0:
            return True
        return False

    def draw(self) -> None:
        if self.ty >= 0.0:
            circ(int(self.x), int(self.y), int(self.r), self.c)
        else:
            circb(int(self.x), int(self.y), int(self.r), 0)


class _DustDownLongParticle(_VandParticle):
    """Dust_down c параметризуемым временем жизни (для длинных хвостов дыма/выхлопа)."""

    def __init__(self, x: float, y: float, r: float, life_frames: int, rng: Rng) -> None:
        ang = rng.uniform(0.0, math.pi)
        self.x = x
        self.y = y
        self.c = 12
        self.ty = rng.uniform(-1.0, 1.0)
        self.vx = math.cos(ang)
        self.vy = math.sin(ang)
        self.r = rng.uniform(0.0, r)

        lf = int(life_frames)
        if lf < 6:
            lf = 6
        self._fade_t = 5.0
        if float(lf) * 0.22 > self._fade_t:
            self._fade_t = float(lf) * 0.22
        self.t = float(lf)

    def update(self, dt: float, world_dx: float, world_dy: float, frame: int, rng: Rng) -> bool:
        self.x += world_dx + self.vx
        self.y += world_dy + self.vy
        self.vx *= 0.95
        self.vy *= 0.95
        if self.t < self._fade_t:
            self.r /= 1.08
            if frame % 10 == 0:
                if self.c < 15:
                    self.c += 1
        self.t -= 1.0 + rng.uniform(0.0, 1.0) * 0.65
        if self.r < 1.0:
            return True
        return False

    def draw(self) -> None:
        if self.ty >= 0.0:
            circ(int(self.x), int(self.y), int(self.r), self.c)
        else:
            circb(int(self.x), int(self.y), int(self.r), 0)


class _DustDownTwoToneLongParticle(_VandParticle):
    """Dust_down с 2 цветами (светлый -> тёмный) и длинной жизнью."""

    def __init__(self, x: float, y: float, r: float, c0: int, c1: int, life_frames: int, rng: Rng
                 ) -> None:
        ang = rng.uniform(0.0, math.pi)
        self.x = x
        self.y = y
        self._c0 = int(c0)
        self._c1 = int(c1)
        self.c = int(c0)
        self.ty = rng.uniform(-1.0, 1.0)
        self.vx = math.cos(ang)
        self.vy = math.sin(ang)
        self.r = rng.uniform(0.0, r)

        lf = int(life_frames)
        if lf < 6:
            lf = 6
        self._t0 = float(lf)
        self.t = float(lf)

        # Переключаем цвет примерно после половины жизни.
        self._switch_t = self._t0 * 0.55
        self._fade_t = 5.0
        if float(lf) * 0.22 > self._fade_t:
            self._fade_t = float(lf) * 0.22

    def update(self, dt: float, world_dx: float, world_dy: float, frame: int, rng: Rng) -> bool:
        self.x += world_dx + self.vx
        self.y += world_dy + self.vy
        self.vx *= 0.95
        self.vy *= 0.95
        if self.t < self._switch_t:
            self.c = self._c1
        else:
            self.c = self._c0
        if self.t < self._fade_t:
            self.r /= 1.08
        self.t -= 1.0 + rng.uniform(0.0, 1.0) * 0.65
        if self.r < 1.0:
            return True
        return False

    def draw(self) -> None:
        if self.ty >= 0.0:
            circ(int(self.x), int(self.y), int(self.r), self.c)
        else:
            circb(int(self.x), int(self.y), int(self.r), 0)


class _DustDownColorParticle(_VandParticle):
    """Dust, который стелется вниз (+Y) и остаётся в заданном цвете."""

    def __init__(self, x: float, y: float, r: float, c: int, rng: Rng) -> None:
        ang = rng.uniform(0.0, math.pi)
        self.x = x
        self.y = y
        self.c = int(c)
        self.ty = rng.uniform(-1.0, 1.0)
        self.vx = math.cos(ang)
        self.vy = math.sin(ang)
        self.r = rng.uniform(0.0, r)
        self.t = 20.0

    def update(self, dt: float, world_dx: float, world_dy: float, frame: int, rng: Rng) -> bool:
        self.x += world_dx + self.vx
        self.y += world_dy + self.vy
        self.vx *= 0.95
        self.vy *= 0.95
        if self.t < 5.0:
            self.r /= 1.1
        self.t -= 1.0 + rng.uniform(0.0, 1.0)
        if self.r < 1.0:
            return True
        return False

    def draw(self) -> None:
        # Для цветного дыма/пыли нам важна читаемость цвета. Поэтому рисуем всегда filled.
        circ(int(self.x), int(self.y), int(self.r), self.c)


class _GrowPuffColorParticle(_VandParticle):
    """Пуф, который растёт со временем (для выхлопа/пара)."""

    def __init__(
        self,
        x: float,
        y: float,
        r0: float,
        r1: float,
        c: int,
        life_frames: int,
        world_follow: float,
        rng: Rng
    ) -> None:
        self.x = x
        self.y = y
        self.c = int(c)
        self._wf = float(world_follow)

        lf = int(life_frames)
        if lf <= 1:
            lf = 1
        self._t0 = float(lf)
        self.t = float(lf)

        self.r = float(r0)
        self._rv = (float(r1) - float(r0)) / float(lf)

        # Небольшое дрожание, чтобы пуфы не были идеальной колонной.
        # Для выхлопа хотим тонкую струйку: меньше бокового разлёта.
        self.vx = (rng.uniform(0.0, 1.0) - 0.5) * 0.18
        self.vy = rng.uniform(0.0, 1.0) * 0.12

    def update(self, dt: float, world_dx: float, world_dy: float, frame: int, rng: Rng) -> bool:
        # Дым/выхлоп "не такой тяжёлый", как следы шин: пусть слегка отстаёт от world-shift,
        # чтобы хвост читался на экране (иначе на высокой скорости всё улетает за низ).
        self.x += world_dx * self._wf + self.vx
        self.y += world_dy * self._wf + self.vy

        # Чем старше пуф, тем больше он расползается: у трубы будет тонкая струйка,
        # а дальше по хвосту — более "клубастый" дым.
        p = 1.0
        if self._t0 > 0.0:
            p = 1.0 - self.t / self._t0
            if p < 0.0:
                p = 0.0
            if p > 1.0:
                p = 1.0

        self.vx += (rng.uniform(0.0, 1.0) - 0.5) * 0.05 * p
        self.vy += (rng.uniform(0.0, 1.0) - 0.5) * 0.03 * p

        damp = 0.92 + 0.05 * p
        self.vx *= damp
        self.vy *= damp

        self.r += self._rv
        if self.t < 6.0:
            # В конце слегка схлопываем, чтобы не оставались "вечные шарики".
            self.r *= 0.92

        self.t -= 1.0 + rng.uniform(0.0, 1.0) * 0.35
        if self.t < 0.0 or self.r < 0.7:
            return True
        return False

    def draw(self) -> None:
        circ(int(self.x), int(self.y), int(self.r), self.c)


class _FireParticle(_VandParticle):
    def __init__(self, x: float, y: float, r: float, c: int, rng: Rng) -> None:
        ang = rng.uniform(0.0, math.pi * 2.0)
        self.x = x
        self.y = y
        self.c = c
        self.vx = math.cos(ang) * 0.5
        self.vy = math.sin(ang) * 0.5
        self.r = rng.uniform(0.0, r)
        self.t = 10.0

    def update(self, dt: float, world_dx: float, world_dy: float, frame: int, rng: Rng) -> bool:
        self.x += world_dx + self.vx
        self.y += world_dy + self.vy
        self.vx *= 0.95
        self.vy *= 0.95
        if self.t < 5.0:
            self.r /= 1.1
            if frame % 5 == 0:
                if self.c > 1:
                    self.c -= 1
        self.t -= 1.0 + rng.uniform(0.0, 1.0)
        if self.r < 1.0:
            return True
        return False

    def draw(self) -> None:
        circ(int(self.x), int(self.y), int(self.r), self.c)


class _FireDirParticle(_VandParticle):
    def __init__(
        self,
        x: float,
        y: float,
        r: float,
        c: int,
        ang0: float,
        ang_range: float,
        rng: Rng
    ) -> None:
        ang = ang0 + rng.uniform(-ang_range * 0.5, ang_range * 0.5)
        self.x = x
        self.y = y
        self.c = c
        self.vx = math.cos(ang) * 0.5
        self.vy = math.sin(ang) * 0.5
        self.r = rng.uniform(0.0, r)
        self.t = 10.0

    def update(self, dt: float, world_dx: float, world_dy: float, frame: int, rng: Rng) -> bool:
        self.x += world_dx + self.vx
        self.y += world_dy + self.vy
        self.vx *= 0.95
        self.vy *= 0.95
        if self.t < 5.0:
            self.r /= 1.1
            if frame % 5 == 0:
                if self.c > 1:
                    self.c -= 1
        self.t -= 1.0 + rng.uniform(0.0, 1.0)
        if self.r < 1.0:
            return True
        return False

    def draw(self) -> None:
        circ(int(self.x), int(self.y), int(self.r), self.c)


class _ExplosionParticle(_VandParticle):
    def __init__(self, x: float, y: float, r: float, rng: Rng) -> None:
        ang = rng.uniform(0.0, math.pi) + math.pi
        self.x = x
        self.y = y
        self.c = 4
        self.vx = math.cos(ang) * rng.uniform(0.0, 1.0) * 2.0
        self.vy = math.sin(ang) * rng.uniform(0.0, 1.0) * 2.0
        self.r = rng.uniform(0.0, r)
        self.t = 20.0

    def update(self, dt: float, world_dx: float, world_dy: float, frame: int, rng: Rng) -> bool:
        self.x += world_dx + self.vx
        self.y += world_dy + self.vy
        self.vx *= 0.99
        self.vy *= 0.99
        if self.t < 5.0:
            self.r /= 1.1
            if frame % 5 == 0:
                if self.c > 1:
                    self.c -= 1
        self.t -= 1.0 + rng.uniform(0.0, 1.0)
        if self.r < 1.0:
            return True
        return False

    def draw(self) -> None:
        circ(int(self.x), int(self.y), int(self.r), self.c)


class _ExplosionDirParticle(_VandParticle):
    def __init__(self, x: float, y: float, r: float, ang0: float, ang_range: float, rng: Rng
                 ) -> None:
        ang = ang0 + rng.uniform(-ang_range * 0.5, ang_range * 0.5)
        self.x = x
        self.y = y
        self.c = 4
        # Меньше рандома: скорость в узком диапазоне вокруг базовой.
        speed = 1.4 + rng.uniform(0.0, 1.0) * 0.5
        self.vx = math.cos(ang) * speed
        self.vy = math.sin(ang) * speed
        self.r = rng.uniform(0.0, r)
        self.t = 20.0

    def update(self, dt: float, world_dx: float, world_dy: float, frame: int, rng: Rng) -> bool:
        self.x += world_dx + self.vx
        self.y += world_dy + self.vy
        self.vx *= 0.99
        self.vy *= 0.99
        if self.t < 5.0:
            self.r /= 1.1
            if frame % 5 == 0:
                if self.c > 1:
                    self.c -= 1
        self.t -= 1.0 + rng.uniform(0.0, 1.0)
        if self.r < 1.0:
            return True
        return False

    def draw(self) -> None:
        circ(int(self.x), int(self.y), int(self.r), self.c)


class _StarParticle(_VandParticle):
    def __init__(self, x: float, y: float, rng: Rng) -> None:
        ang = rng.uniform(0.0, math.pi * 2.0)
        self.x = x
        self.y = y
        self.vx = math.cos(ang)
        self.vy = math.sin(ang)
        self.r = rng.uniform(0.0, 1.0)
        self.t = 10.0

    def update(self, dt: float, world_dx: float, world_dy: float, frame: int, rng: Rng) -> bool:
        self.x += world_dx + self.vx
        self.y += world_dy + self.vy
        self.vx /= 1.1
        self.vy /= 1.1
        self.t -= 1.0 + rng.uniform(0.0, 1.0)
        if self.t < 0.0:
            return True
        return False

    def draw(self) -> None:
        circb(int(self.x), int(self.y), int(self.r), 14)


class VandParticles(FxSystem):
    """Порт Vand particles pack как FxSystem (screen-space)."""

    def __init__(self, seed: int) -> None:
        self._rng = Rng(seed)
        self._frame = 0
        self._particles: list[_VandParticle] = []

    def alive(self) -> bool:
        return len(self._particles) > 0

    def update(self, dt: float, world_dx: float, world_dy: float) -> None:
        self._frame += 1

        i = 0
        write = 0
        while i < len(self._particles):
            p = self._particles[i]
            dead = p.update(dt, world_dx, world_dy, self._frame, self._rng)
            if not dead:
                self._particles[write] = p
                write += 1
            i += 1
        while len(self._particles) > write:
            self._particles.pop()

    def draw(self) -> None:
        i = 0
        while i < len(self._particles):
            self._particles[i].draw()
            i += 1

    def rotate_around(self, cx: float, cy: float, cos_t: float, sin_t: float) -> None:
        """Компенсация вращения камеры: поворачивает все частицы вокруг точки.

        В DRIVE top-down камера поворачивается так, чтобы машина всегда “смотрела вверх”.
        Для хвостов (выхлоп/дым) иногда хочется, чтобы они оставались в мире и не
        “поворачивали вместе с машиной”. Тогда мы поворачиваем частицы на -dtheta
        (где dtheta = изменение heading между кадрами).
        """
        i = 0
        while i < len(self._particles):
            p = self._particles[i]
            x = getattr(p, "x", None)
            y = getattr(p, "y", None)
            if x is not None and y is not None:
                dx = float(x) - cx
                dy = float(y) - cy
                rx = dx * cos_t - dy * sin_t
                ry = dx * sin_t + dy * cos_t
                setattr(p, "x", cx + rx)
                setattr(p, "y", cy + ry)

            vx = getattr(p, "vx", None)
            vy = getattr(p, "vy", None)
            if vx is not None and vy is not None:
                rvx = float(vx) * cos_t - float(vy) * sin_t
                rvy = float(vx) * sin_t + float(vy) * cos_t
                setattr(p, "vx", rvx)
                setattr(p, "vy", rvy)
            i += 1

    def spawn_tri(self, x: float, y: float, r: float) -> None:
        self._particles.append(_TriParticle(x, y, r, self._rng))

    def spawn_tri2(self, x: float, y: float, r: float) -> None:
        self._particles.append(_Tri2Particle(x, y, r, self._rng))

    def spawn_plus(self, x: float, y: float, r: float) -> None:
        self._particles.append(_PlusParticle(x, y, r, self._rng))

    def spawn_marker(self, x: float, y: float) -> None:
        self._particles.append(_MarkerParticle(x, y, self._rng))

    def spawn_dust(self, x: float, y: float, r: float) -> None:
        self._particles.append(_DustParticle(x, y, r, self._rng))

    def spawn_dust_down(self, x: float, y: float, r: float) -> None:
        self._particles.append(_DustDownParticle(x, y, r, self._rng))

    def spawn_dust_down_life(self, x: float, y: float, r: float, life_frames: int) -> None:
        self._particles.append(_DustDownLongParticle(x, y, r, int(life_frames), self._rng))

    def spawn_dust_down_two_tone_life(self,
                                      x: float, y: float,
                                      r: float, c0: int, c1: int, life_frames: int) -> None:
        self._particles.append(
            _DustDownTwoToneLongParticle(
                x, y, r, int(c0), int(c1), int(life_frames), self._rng
            )
        )

    def spawn_dust_down_color(self, x: float, y: float, r: float, c: int) -> None:
        self._particles.append(_DustDownColorParticle(x, y, r, c, self._rng))

    def spawn_puff_grow_color(
        self,
        x: float,
        y: float,
        r0: float,
        r1: float,
        c: int,
        life_frames: int,
        world_follow: float = 1.0
    ) -> None:
        self._particles.append(
            _GrowPuffColorParticle(
                x, y, r0, r1, c, life_frames, world_follow, self._rng
            )
        )

    def spawn_fire(self, x: float, y: float, r: float, c: int) -> None:
        self._particles.append(_FireParticle(x, y, r, c, self._rng))

    def spawn_explosion(self, x: float, y: float, r: float) -> None:
        # В оригинале explosion спавнит fire частицы "внутри" move(). Здесь делаем
        # упрощение: explosion = набор circle + небольшое количество fire.
        self._particles.append(_ExplosionParticle(x, y, r, self._rng))
        i = 0
        while i < 6:
            self.spawn_fire(x, y, r * 0.8, 4)
            i += 1

    def spawn_explosion_dir(self, x: float, y: float, r: float, dir_x: float, dir_y: float) -> None:
        ang0 = math.atan2(dir_y, dir_x)
        # Узкий "конус", чтобы направление читалось сильнее.
        ang_range = math.pi / 3.0
        self._particles.append(_ExplosionDirParticle(x, y, r, ang0, ang_range, self._rng))

        fire_range = math.pi / 2.0
        i = 0
        while i < 6:
            self._particles.append(_FireDirParticle(x, y, r * 0.8, 4, ang0, fire_range, self._rng))
            i += 1

    def spawn_star(self, x: float, y: float) -> None:
        self._particles.append(_StarParticle(x, y, self._rng))
