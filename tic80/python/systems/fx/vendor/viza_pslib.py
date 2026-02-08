# title:  pslib
# author: Viza
# desc:   An advenced particle system library for the VIC-80
#
# NOTE: Ported from Lua to TIC-80 Python (PocketPy) for Wyrdway.

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

    from tic80 import circ, line, pix, spr

    from ...drive.rng import Rng
    from ..fx_manager import FxSystem
else:
    Any = object

import math


class _PslibParticle:
    def __init__(self) -> None:
        self.x = 0.0
        self.y = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.prev_x = 0.0
        self.prev_y = 0.0
        self.phase = 0.0
        self.starttime = 0.0
        self.deathtime = 0.0
        self.startsize = 1.0
        self.endsize = 1.0
        self._rndspr_frame = 0


class PslibTimer:
    def __init__(self, timerfunc: Any, params: Any) -> None:
        self.timerfunc = timerfunc
        self.params = params


class PslibEmitter:
    def __init__(self, emitfunc: Any, params: Any) -> None:
        self.emitfunc = emitfunc
        self.params = params


class PslibAffector:
    def __init__(self, affectfunc: Any, params: Any) -> None:
        self.affectfunc = affectfunc
        self.params = params


class PslibDrawFunc:
    def __init__(self, drawfunc: Any, params: Any) -> None:
        self.drawfunc = drawfunc
        self.params = params


class ParticleSystem:
    def __init__(
        self,
        rng: Rng,
        minlife_s: float,
        maxlife_s: float,
        minstartsize: float,
        maxstartsize: float,
        minendsize: float,
        maxendsize: float
    ) -> None:
        self.autoremove = True
        self.minlife = minlife_s
        self.maxlife = maxlife_s
        self.minstartsize = minstartsize
        self.maxstartsize = maxstartsize
        self.minendsize = minendsize
        self.maxendsize = maxendsize

        self.particles: list[_PslibParticle] = []
        self.emittimers: list[PslibTimer] = []
        self.emitters: list[PslibEmitter] = []
        self.drawfuncs: list[PslibDrawFunc] = []
        self.affectors: list[PslibAffector] = []

        self._rng = rng
        self._t = 0.0

    def now(self) -> float:
        return self._t

    def step(self, dt: float, world_dx: float, world_dy: float) -> None:
        self._t += dt
        timenow = self._t

        i = 0
        while i < len(self.emittimers):
            et = self.emittimers[i]
            keep = et.timerfunc(self, et.params)
            if keep is False:
                self.emittimers.pop(i)
                continue
            i += 1

        i = 0
        while i < len(self.particles):
            p = self.particles[i]
            denom = p.deathtime - p.starttime
            if denom > 0.0:
                p.phase = (timenow - p.starttime) / denom
            else:
                p.phase = 1.0

            j = 0
            while j < len(self.affectors):
                a = self.affectors[j]
                a.affectfunc(p, a.params)
                j += 1

            p.prev_x = p.x
            p.prev_y = p.y
            p.x = p.x + world_dx + p.vx
            p.y = p.y + world_dy + p.vy

            dead = False
            if p.x < 0 or p.x > 240 or p.y < 0 or p.y > 136:
                dead = True
            if timenow >= p.deathtime:
                dead = True
            if dead:
                self.particles.pop(i)
                continue
            i += 1

    def emit_particle(self) -> None:
        if len(self.emitters) <= 0:
            return
        p = _PslibParticle()
        e = self.emitters[int(self._rng.uniform(
            0.0, float(len(self.emitters)))) % len(self.emitters)]
        e.emitfunc(self, p, e.params)

        p.phase = 0.0
        p.starttime = self._t
        life = self._rng.uniform(
            0.0, self.maxlife - self.minlife) + self.minlife
        p.deathtime = self._t + life

        p.startsize = self._rng.uniform(
            0.0, self.maxstartsize - self.minstartsize) + self.minstartsize
        p.endsize = self._rng.uniform(
            0.0, self.maxendsize - self.minendsize) + self.minendsize
        p._rndspr_frame = int(p.startsize)

        self.particles.append(p)


class PslibFx(FxSystem):
    def __init__(self) -> None:
        self._systems: list[ParticleSystem] = []

    def add(self, ps: ParticleSystem) -> None:
        self._systems.append(ps)

    def alive(self) -> bool:
        i = 0
        while i < len(self._systems):
            ps = self._systems[i]
            if (not ps.autoremove) or len(ps.particles) > 0 or len(ps.emittimers) > 0:
                return True
            i += 1
        return False

    def update(self, dt: float, world_dx: float, world_dy: float) -> None:
        i = 0
        while i < len(self._systems):
            self._systems[i].step(dt, world_dx, world_dy)
            i += 1

    def draw(self) -> None:
        i = 0
        while i < len(self._systems):
            ps = self._systems[i]
            j = 0
            while j < len(ps.drawfuncs):
                df = ps.drawfuncs[j]
                df.drawfunc(ps, df.params)
                j += 1
            i += 1


def make_psystem(
    rng: Rng,
    minlife_s: float,
    maxlife_s: float,
    minstartsize: float,
    maxstartsize: float,
    minendsize: float,
    maxendsize: float
) -> ParticleSystem:
    return ParticleSystem(rng, minlife_s, maxlife_s, minstartsize, maxstartsize, minendsize, maxendsize)


def emittimer_burst(ps: ParticleSystem, params: Any) -> bool:
    num = int(params.num)
    i = 0
    while i < num:
        ps.emit_particle()
        i += 1
    return False


def emittimer_constant(ps: ParticleSystem, params: Any) -> bool:
    if params.nextemittime <= ps.now():
        ps.emit_particle()
        params.nextemittime = params.nextemittime + params.speed
    return True


def emitter_point(ps: ParticleSystem, p: _PslibParticle, params: Any) -> None:
    p.x = params.x
    p.y = params.y
    p.vx = ps._rng.uniform(0.0, params.maxstartvx -
                           params.minstartvx) + params.minstartvx
    p.vy = ps._rng.uniform(0.0, params.maxstartvy -
                           params.minstartvy) + params.minstartvy


def emitter_box(ps: ParticleSystem, p: _PslibParticle, params: Any) -> None:
    p.x = ps._rng.uniform(0.0, params.maxx - params.minx) + params.minx
    p.y = ps._rng.uniform(0.0, params.maxy - params.miny) + params.miny
    p.vx = ps._rng.uniform(0.0, params.maxstartvx -
                           params.minstartvx) + params.minstartvx
    p.vy = ps._rng.uniform(0.0, params.maxstartvy -
                           params.minstartvy) + params.minstartvy


def affect_force(p: _PslibParticle, params: Any) -> None:
    p.vx = p.vx + params.fx
    p.vy = p.vy + params.fy


def affect_forcezone(p: _PslibParticle, params: Any) -> None:
    if p.x >= params.zoneminx and p.x <= params.zonemaxx and p.y >= params.zoneminy and p.y <= params.zonemaxy:
        p.vx = p.vx + params.fx
        p.vy = p.vy + params.fy


def affect_stopzone(p: _PslibParticle, params: Any) -> None:
    if p.x >= params.zoneminx and p.x <= params.zonemaxx and p.y >= params.zoneminy and p.y <= params.zonemaxy:
        p.vx = 0.0
        p.vy = 0.0


def affect_bouncezone(p: _PslibParticle, params: Any) -> None:
    if p.x >= params.zoneminx and p.x <= params.zonemaxx and p.y >= params.zoneminy and p.y <= params.zonemaxy:
        p.vx = -p.vx * params.damping
        p.vy = -p.vy * params.damping


def affect_attract(p: _PslibParticle, params: Any) -> None:
    if abs(p.x - params.x) + abs(p.y - params.y) < params.mradius:
        p.vx = p.vx + (p.x - params.x) * params.strength
        p.vy = p.vy + (p.y - params.y) * params.strength


def affect_orbit(p: _PslibParticle, params: Any) -> None:
    params.phase = params.phase + params.speed
    p.x = p.x + math.sin(params.phase) * params.xstrength
    p.y = p.y + math.cos(params.phase) * params.ystrength


def draw_ps_fillcirc(ps: ParticleSystem, params: Any) -> None:
    colors = params.colors
    n = len(colors)
    i = 0
    while i < len(ps.particles):
        p = ps.particles[i]
        idx = int(p.phase * n)
        if idx < 0:
            idx = 0
        if idx >= n:
            idx = n - 1
        r = (1.0 - p.phase) * p.startsize + p.phase * p.endsize
        circ(int(p.x), int(p.y), int(r), int(colors[idx]))
        i += 1


def draw_ps_pixel(ps: ParticleSystem, params: Any) -> None:
    colors = params.colors
    n = len(colors)
    i = 0
    while i < len(ps.particles):
        p = ps.particles[i]
        idx = int(p.phase * n)
        if idx < 0:
            idx = 0
        if idx >= n:
            idx = n - 1
        pix(int(p.x), int(p.y), int(colors[idx]))
        i += 1


def draw_ps_streak(ps: ParticleSystem, params: Any) -> None:
    colors = params.colors
    n = len(colors)
    i = 0
    while i < len(ps.particles):
        p = ps.particles[i]
        idx = int(p.phase * n)
        if idx < 0:
            idx = 0
        if idx >= n:
            idx = n - 1
        line(int(p.x), int(p.y), int(p.prev_x),
             int(p.prev_y), int(colors[idx]))
        i += 1


def draw_ps_animspr(ps: ParticleSystem, params: Any) -> None:
    params.currframe = params.currframe + params.speed
    if params.currframe > len(params.frames):
        params.currframe = 1
    i = 0
    while i < len(ps.particles):
        p = ps.particles[i]
        idx = int(params.currframe + p.startsize) % len(params.frames)
        spr(int(params.frames[idx]), int(p.x), int(p.y), 0)
        i += 1


def draw_ps_agespr(ps: ParticleSystem, params: Any) -> None:
    i = 0
    n = len(params.frames)
    while i < len(ps.particles):
        p = ps.particles[i]
        idx = int(p.phase * n)
        if idx < 0:
            idx = 0
        if idx >= n:
            idx = n - 1
        spr(int(params.frames[idx]), int(p.x), int(p.y), 0)
        i += 1


def draw_ps_rndspr(ps: ParticleSystem, params: Any) -> None:
    frames = params.frames
    n = len(frames)
    i = 0
    while i < len(ps.particles):
        p = ps.particles[i]
        idx = p._rndspr_frame
        if idx < 0:
            idx = 0
        if idx >= n:
            idx = n - 1
        spr(int(frames[idx]), int(p.x), int(p.y), 0)
        i += 1
