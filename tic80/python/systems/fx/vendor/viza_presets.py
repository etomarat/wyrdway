# title:  pslib presets
# author: Viza (original pslib)
#
# NOTE: Presets ported from `vendor/viza_pslib.lua` to TIC-80 Python (PocketPy) for Wyrdway.

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...drive.rng import Rng
    from .viza_pslib import (
        PslibAffector,
        PslibDrawFunc,
        PslibEmitter,
        PslibFx,
        PslibTimer,
        affect_attract,
        affect_bouncezone,
        affect_force,
        affect_forcezone,
        affect_orbit,
        affect_stopzone,
        draw_ps_agespr,
        draw_ps_animspr,
        draw_ps_fillcirc,
        draw_ps_pixel,
        draw_ps_rndspr,
        draw_ps_streak,
        emitter_box,
        emitter_point,
        emittimer_burst,
        emittimer_constant,
        make_psystem
    )


def _ms(v: float) -> float:
    return v * 0.001


class _BurstParams:
    def __init__(self, num: int) -> None:
        self.num = num


class _ConstantParams:
    def __init__(self, nextemittime: float, speed: float) -> None:
        self.nextemittime = nextemittime
        self.speed = speed


class _EmitterPointParams:
    def __init__(
        self,
        x: float,
        y: float,
        minstartvx: float,
        maxstartvx: float,
        minstartvy: float,
        maxstartvy: float
    ) -> None:
        self.x = x
        self.y = y
        self.minstartvx = minstartvx
        self.maxstartvx = maxstartvx
        self.minstartvy = minstartvy
        self.maxstartvy = maxstartvy


class _EmitterBoxParams:
    def __init__(
        self,
        minx: float,
        maxx: float,
        miny: float,
        maxy: float,
        minstartvx: float,
        maxstartvx: float,
        minstartvy: float,
        maxstartvy: float
    ) -> None:
        self.minx = minx
        self.maxx = maxx
        self.miny = miny
        self.maxy = maxy
        self.minstartvx = minstartvx
        self.maxstartvx = maxstartvx
        self.minstartvy = minstartvy
        self.maxstartvy = maxstartvy


class _ForceParams:
    def __init__(self, fx: float, fy: float) -> None:
        self.fx = fx
        self.fy = fy


class _ForceZoneParams:
    def __init__(
        self,
        fx: float,
        fy: float,
        zoneminx: float,
        zonemaxx: float,
        zoneminy: float,
        zonemaxy: float
    ) -> None:
        self.fx = fx
        self.fy = fy
        self.zoneminx = zoneminx
        self.zonemaxx = zonemaxx
        self.zoneminy = zoneminy
        self.zonemaxy = zonemaxy


class _StopZoneParams:
    def __init__(self, zoneminx: float, zonemaxx: float, zoneminy: float, zonemaxy: float) -> None:
        self.zoneminx = zoneminx
        self.zonemaxx = zonemaxx
        self.zoneminy = zoneminy
        self.zonemaxy = zonemaxy


class _BounceZoneParams:
    def __init__(
        self,
        damping: float,
        zoneminx: float,
        zonemaxx: float,
        zoneminy: float,
        zonemaxy: float
    ) -> None:
        self.damping = damping
        self.zoneminx = zoneminx
        self.zonemaxx = zonemaxx
        self.zoneminy = zoneminy
        self.zonemaxy = zonemaxy


class _AttractParams:
    def __init__(self, x: float, y: float, mradius: float, strength: float) -> None:
        self.x = x
        self.y = y
        self.mradius = mradius
        self.strength = strength


class _OrbitParams:
    def __init__(self, phase: float, speed: float, xstrength: float, ystrength: float) -> None:
        self.phase = phase
        self.speed = speed
        self.xstrength = xstrength
        self.ystrength = ystrength


class _ColorsParams:
    def __init__(self, colors: list[int]) -> None:
        self.colors = colors


class _FramesParams:
    def __init__(self, frames: list[int]) -> None:
        self.frames = frames


class _AnimFramesParams:
    def __init__(self, frames: list[int], speed: float, currframe: float) -> None:
        self.frames = frames
        self.speed = speed
        self.currframe = currframe


def make_bubbles_fx(rng: Rng) -> PslibFx:
    fx = PslibFx()
    ps = make_psystem(rng, _ms(500), _ms(3000), 1, 9, 0.5, 0.5)
    ps.autoremove = False
    ps.emittimers.append(PslibTimer(emittimer_constant,
                         _ConstantParams(ps.now(), _ms(0.2))))
    ps.emitters.append(
        PslibEmitter(
            emitter_box,
            _EmitterBoxParams(0, 240, 100, 110, 0, 0, -1.5, -0.2)
        )
    )
    ps.drawfuncs.append(PslibDrawFunc(draw_ps_agespr, _FramesParams(
        [16, 16, 17, 17, 17, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 19])))
    ps.affectors.append(PslibAffector(
        affect_orbit, _OrbitParams(0.0, 0.001, 0.5, 0)))
    fx.add(ps)
    return fx


def make_magicsparks_fx(rng: Rng, ex: float, ey: float) -> PslibFx:
    fx = PslibFx()
    ps = make_psystem(rng, _ms(300), _ms(1700), 1, 5, 1, 5)
    ps.emittimers.append(PslibTimer(emittimer_burst, _BurstParams(10)))
    ps.emitters.append(
        PslibEmitter(
            emitter_box,
            _EmitterBoxParams(ex - 8, ex + 8, ey - 8,
                              ey + 8, -1.5, 1.5, -3, -2)
        )
    )
    ps.drawfuncs.append(PslibDrawFunc(
        draw_ps_rndspr, _FramesParams([32, 33, 34, 35, 36])))
    ps.affectors.append(PslibAffector(affect_force, _ForceParams(0, 0.3)))
    fx.add(ps)
    return fx


def make_butterflies_fx(rng: Rng, ex: float, ey: float) -> PslibFx:
    fx = PslibFx()
    ps = make_psystem(rng, _ms(2000), _ms(3000), 1, 9, 1, 5)
    ps.emittimers.append(PslibTimer(emittimer_burst, _BurstParams(10)))
    ps.emitters.append(PslibEmitter(emitter_box, _EmitterBoxParams(
        ex - 16, ex + 16, ey - 8, ey + 8, 0, 0, -1, -0.5)))
    ps.drawfuncs.append(PslibDrawFunc(
        draw_ps_animspr, _AnimFramesParams([22, 23, 24, 23], 0.2, 1)))
    ps.affectors.append(PslibAffector(
        affect_forcezone, _ForceZoneParams(-0.05, 0.0, 64, 127, 64, 100)))
    ps.affectors.append(PslibAffector(
        affect_forcezone, _ForceZoneParams(0.05, 0.0, 0, 64, 30, 70)))
    fx.add(ps)
    return fx


def make_3dwarp_fx(rng: Rng) -> PslibFx:
    fx = PslibFx()
    ps = make_psystem(rng, _ms(1000), _ms(2000), 1, 2, 0.5, 0.5)
    ps.autoremove = False
    ps.emittimers.append(PslibTimer(emittimer_constant,
                         _ConstantParams(ps.now(), _ms(0.001))))
    ps.emitters.append(PslibEmitter(
        emitter_box, _EmitterBoxParams(118, 122, 63, 67, 0, 0, 0, 0)))
    ps.affectors.append(PslibAffector(
        affect_attract, _AttractParams(120, 65, 64, 0.01)))
    ps.drawfuncs.append(PslibDrawFunc(draw_ps_streak, _ColorsParams(
        [2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 10, 15, 1, 10, 10, 10, 15, 10, 10, 15, 10, 15, 15])))
    fx.add(ps)
    return fx


def make_starfield_fx(rng: Rng) -> PslibFx:
    fx = PslibFx()
    ps = make_psystem(rng, _ms(4000), _ms(6000), 1, 2, 0.5, 0.5)
    ps.autoremove = False
    ps.emittimers.append(PslibTimer(emittimer_constant,
                         _ConstantParams(ps.now(), _ms(0.01))))
    ps.emitters.append(PslibEmitter(
        emitter_box, _EmitterBoxParams(235, 240, 0, 136, -2.0, -0.5, 0, 0)))
    ps.drawfuncs.append(PslibDrawFunc(draw_ps_pixel, _ColorsParams(
        [15, 10, 15, 10, 15, 10, 10, 15, 10, 15, 15, 10, 10, 15])))
    fx.add(ps)
    return fx


def make_waterfall_fx(rng: Rng, ex: float, ey: float) -> PslibFx:
    fx = PslibFx()
    ps = make_psystem(rng, _ms(1500), _ms(2000), 1, 2, 0.5, 0.5)
    ps.autoremove = False
    ps.emittimers.append(PslibTimer(emittimer_constant,
                         _ConstantParams(ps.now(), _ms(0.01))))
    ps.emitters.append(PslibEmitter(emitter_box, _EmitterBoxParams(
        ex - 8, ex + 8, ey, ey + 1, -0.5, 0.5, 0, 0)))
    ps.drawfuncs.append(PslibDrawFunc(draw_ps_streak, _ColorsParams(
        [15, 13, 2, 13, 13, 2, 13, 2, 2, 15, 15, 15])))
    ps.affectors.append(PslibAffector(affect_force, _ForceParams(0, 0.3)))
    ps.affectors.append(PslibAffector(affect_bouncezone,
                        _BounceZoneParams(0.2, 40, 200, 100, 136)))
    fx.add(ps)
    return fx


def make_blood_fx(rng: Rng, ex: float, ey: float) -> PslibFx:
    fx = PslibFx()
    ps = make_psystem(rng, _ms(2000), _ms(3000), 1, 2, 0.5, 0.5)
    ps.emittimers.append(PslibTimer(emittimer_burst, _BurstParams(30)))
    ps.emitters.append(PslibEmitter(
        emitter_point, _EmitterPointParams(ex, ey, 1, 3, -3, -2)))
    ps.drawfuncs.append(PslibDrawFunc(draw_ps_pixel, _ColorsParams([6])))
    ps.affectors.append(PslibAffector(affect_force, _ForceParams(0, 0.15)))
    ps.affectors.append(PslibAffector(
        affect_stopzone, _StopZoneParams(0, 240, 100, 127)))
    fx.add(ps)
    return fx


def make_sparks_fx(rng: Rng, ex: float, ey: float) -> PslibFx:
    fx = PslibFx()
    ps = make_psystem(rng, _ms(300), _ms(700), 1, 2, 0.5, 0.5)
    ps.emittimers.append(PslibTimer(emittimer_burst, _BurstParams(10)))
    ps.emitters.append(PslibEmitter(
        emitter_point, _EmitterPointParams(ex, ey, -1.5, 1.5, -3, -2)))
    ps.drawfuncs.append(PslibDrawFunc(
        draw_ps_fillcirc, _ColorsParams([15, 14, 12, 9, 4, 3])))
    ps.affectors.append(PslibAffector(affect_force, _ForceParams(0, 0.3)))
    fx.add(ps)
    return fx


def make_explosparks_fx(rng: Rng, ex: float, ey: float) -> PslibFx:
    fx = PslibFx()
    ps = make_psystem(rng, _ms(300), _ms(700), 1, 2, 0.5, 0.5)
    ps.emittimers.append(PslibTimer(emittimer_burst, _BurstParams(10)))
    ps.emitters.append(PslibEmitter(
        emitter_point, _EmitterPointParams(ex, ey, -1.5, 1.5, -1.5, 1.5)))
    ps.drawfuncs.append(PslibDrawFunc(
        draw_ps_pixel, _ColorsParams([12, 10, 1, 4, 1, 2])))
    ps.affectors.append(PslibAffector(affect_force, _ForceParams(0, 0.1)))
    fx.add(ps)
    return fx


def make_explosion_fx(rng: Rng, ex: float, ey: float) -> PslibFx:
    fx = PslibFx()
    ps = make_psystem(rng, _ms(100), _ms(500), 9, 14, 1, 3)
    ps.emittimers.append(PslibTimer(emittimer_burst, _BurstParams(4)))
    ps.emitters.append(PslibEmitter(emitter_box, _EmitterBoxParams(
        ex - 4, ex + 4, ey - 4, ey + 4, 0, 0, 0, 0)))
    ps.drawfuncs.append(PslibDrawFunc(
        draw_ps_fillcirc, _ColorsParams([15, 0, 14, 9, 9, 4])))
    fx.add(ps)
    return fx


def make_smoke_fx(rng: Rng, ex: float, ey: float) -> PslibFx:
    fx = PslibFx()
    ps = make_psystem(rng, _ms(200), _ms(2000), 1, 3, 6, 9)
    ps.autoremove = False
    ps.emittimers.append(PslibTimer(emittimer_constant,
                         _ConstantParams(ps.now(), _ms(200))))
    ps.emitters.append(PslibEmitter(emitter_box, _EmitterBoxParams(
        ex - 4, ex + 4, ey, ey + 2, 0, 0, 0, 0)))
    ps.drawfuncs.append(PslibDrawFunc(
        draw_ps_fillcirc, _ColorsParams([1, 3, 2])))
    ps.affectors.append(PslibAffector(
        affect_force, _ForceParams(0.003, -0.009)))
    fx.add(ps)
    return fx


def make_explosmoke_fx(rng: Rng, ex: float, ey: float) -> PslibFx:
    fx = PslibFx()
    ps = make_psystem(rng, _ms(1500), _ms(2000), 5, 8, 17, 18)
    ps.emittimers.append(PslibTimer(emittimer_burst, _BurstParams(1)))
    ps.emitters.append(PslibEmitter(
        emitter_point, _EmitterPointParams(ex, ey, 0, 0, 0, 0)))
    ps.drawfuncs.append(PslibDrawFunc(draw_ps_fillcirc, _ColorsParams([2])))
    ps.affectors.append(PslibAffector(
        affect_force, _ForceParams(0.003, -0.01)))
    fx.add(ps)
    return fx


def make_rich_explosion_fx(rng: Rng, ex: float, ey: float) -> PslibFx:
    fx = PslibFx()
    a = make_explosmoke_fx(rng, ex, ey)
    b = make_explosparks_fx(rng, ex, ey)
    c = make_explosion_fx(rng, ex, ey)
    fx._systems.extend(a._systems)
    fx._systems.extend(b._systems)
    fx._systems.extend(c._systems)
    return fx
